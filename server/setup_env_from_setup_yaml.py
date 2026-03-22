from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import yaml


def resolve_conda_bin(explicit_conda_bin: str | None) -> str:
    if explicit_conda_bin:
        return explicit_conda_bin

    candidates = [
        Path.home() / "miniconda3/bin/conda",
        Path.home() / "anaconda3/bin/conda",
        Path.home() / "mambaforge/bin/conda",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return "conda"


def sanitize_env_name(seed: str) -> str:
    safe = seed.replace("/", "-").replace("_", "-").replace(".", "-")
    return ("a4-" + safe)[:80]


def accept_conda_tos(conda_bin: str) -> None:
    channels = [
        "https://repo.anaconda.com/pkgs/main",
        "https://repo.anaconda.com/pkgs/r",
    ]
    for channel in channels:
        subprocess.run(
            [conda_bin, "tos", "accept", "--override-channels", "--channel", channel],
            check=False,
            capture_output=True,
            text=True,
        )


def load_setup_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid setup.yaml format: {path}")
    return data


def download_lockfile(lockfile_url: str) -> Path:
    with tempfile.NamedTemporaryFile(prefix="a4-lockfile-", suffix=".lock", delete=False) as tmp:
        urllib.request.urlretrieve(lockfile_url, tmp.name)
        return Path(tmp.name)


def conda_exec_env(setup_data: dict) -> dict:
    env_cfg = setup_data.get("environment", {})
    override = bool(env_cfg.get("override_channels", True))
    channels = env_cfg.get("channels", ["conda-forge"])

    run_env = os.environ.copy()
    if override:
        run_env["CONDA_OVERRIDE_CHANNELS"] = "true"
        if isinstance(channels, list) and channels:
            run_env["CONDA_CHANNELS"] = ",".join(channels)
    return run_env


def main() -> None:
    parser = argparse.ArgumentParser(description="Create conda env from setup.yaml for one config.")
    parser.add_argument("--setup-yaml", required=True)
    parser.add_argument("--env-name", default=None)
    parser.add_argument("--conda-bin", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    setup_yaml = Path(args.setup_yaml).resolve()
    if not setup_yaml.exists():
        raise FileNotFoundError(f"setup.yaml not found: {setup_yaml}")

    setup_data = load_setup_yaml(setup_yaml)

    env_name = args.env_name or setup_data.get("environment", {}).get("name") or sanitize_env_name(str(setup_yaml.parent))
    conda_bin = resolve_conda_bin(args.conda_bin)

    accept_conda_tos(conda_bin)
    exec_env = conda_exec_env(setup_data)

    lockfile_url = setup_data.get("environment", {}).get("lockfile_url")
    if not isinstance(lockfile_url, str) or not lockfile_url.strip():
        raise ValueError("setup.yaml missing environment.lockfile_url")

    lockfile_path = download_lockfile(lockfile_url)

    subprocess.run([conda_bin, "env", "remove", "-n", env_name, "-y"], check=False)
    create_cmd = [conda_bin, "create", "-y", "-n", env_name, "--file", str(lockfile_path)]
    result = subprocess.run(create_cmd, check=False, env=exec_env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    tardis_spec = setup_data.get("tardis", {}).get("conda_spec", "tardis-sn")
    install_cmd = [conda_bin, "install", "-y", "-n", env_name, tardis_spec]
    result = subprocess.run(install_cmd, check=False, env=exec_env)
    if result.returncode != 0:
        fallback_cmd = [conda_bin, "install", "-y", "-n", env_name, "tardis-sn"]
        fallback_result = subprocess.run(fallback_cmd, check=False, env=exec_env)
        if fallback_result.returncode != 0:
            raise SystemExit(fallback_result.returncode)

    extras = setup_data.get("environment", {}).get("extra_packages", [])
    if isinstance(extras, list) and extras:
        extra_cmd = [conda_bin, "install", "-y", "-n", env_name, *extras]
        subprocess.run(extra_cmd, check=False, env=exec_env)

    verify_cmd = [
        conda_bin,
        "run",
        "-n",
        env_name,
        "python",
        "-c",
        "import tardis; print(tardis.__version__)",
    ]
    subprocess.run(verify_cmd, check=False)

    payload = {
        "setup_yaml": str(setup_yaml),
        "env_name": env_name,
        "conda_bin": conda_bin,
        "lockfile_url": lockfile_url,
        "tardis_conda_spec": tardis_spec,
    }
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload))


if __name__ == "__main__":
    main()
