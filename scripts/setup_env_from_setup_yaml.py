from __future__ import annotations

import argparse
import json
import os
import re
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


def list_remote_tags(repo_url: str) -> list[str]:
    cmd = ["git", "ls-remote", "--tags", repo_url]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    tags: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        ref = parts[1]
        if not ref.startswith("refs/tags/"):
            continue
        tag = ref.replace("refs/tags/", "", 1)
        if tag.endswith("^{}"):
            tag = tag[:-3]
        tags.append(tag)
    return sorted(set(tags))


def resolve_latest_release_tag(repo_url: str) -> str | None:
    tags = list_remote_tags(repo_url)
    best_tag: str | None = None
    best_key: tuple[int, int, int] | None = None

    pattern = re.compile(r"^release-(\d{4})\.(\d{1,2})\.(\d{1,2})$")
    for tag in tags:
        match = pattern.match(tag)
        if not match:
            continue
        key = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        if best_key is None or key > best_key:
            best_key = key
            best_tag = tag

    return best_tag


def install_tardis(conda_bin: str, env_name: str, setup_data: dict, exec_env: dict) -> tuple[str, str]:
    requested_ref = setup_data.get("tardis", {}).get("requested_ref", "release-latest")
    if not isinstance(requested_ref, str) or not requested_ref.strip():
        requested_ref = "release-latest"

    repo_url = setup_data.get("tardis", {}).get("repo_url", "https://github.com/tardis-sn/tardis.git")
    if not isinstance(repo_url, str) or not repo_url.strip():
        repo_url = "https://github.com/tardis-sn/tardis.git"

    normalized = requested_ref.strip()
    latest_release_tag = resolve_latest_release_tag(repo_url)

    if normalized in {"release-latest", "latest"}:
        candidate_refs = [
            latest_release_tag,
            "release-latest",
            "master",
            "main",
        ]
    else:
        candidate_refs = [normalized, latest_release_tag, "release-latest", "master", "main"]

    deduped_refs: list[str] = []
    for ref in candidate_refs:
        if not ref:
            continue
        if ref not in deduped_refs:
            deduped_refs.append(ref)

    subprocess.run([conda_bin, "install", "-y", "-n", env_name, "pip"], check=False, env=exec_env)

    for ref in deduped_refs:
        pip_spec = f"git+{repo_url}@{ref}"
        pip_cmd = [
            conda_bin,
            "run",
            "-n",
            env_name,
            "python",
            "-m",
            "pip",
            "install",
            "--upgrade",
            pip_spec,
        ]
        result = subprocess.run(pip_cmd, check=False)
        if result.returncode == 0:
            return ("pip", pip_spec)

    raise RuntimeError(
        f"Failed to install TARDIS from {repo_url} using refs: {', '.join(deduped_refs)}"
    )


def install_extra_packages(conda_bin: str, env_name: str, extras: list[str], exec_env: dict) -> None:
    conda_cmd = [conda_bin, "install", "-y", "-n", env_name, *extras]
    conda_result = subprocess.run(conda_cmd, check=False, env=exec_env)
    if conda_result.returncode == 0:
        return

    pip_cmd = [
        conda_bin,
        "run",
        "-n",
        env_name,
        "python",
        "-m",
        "pip",
        "install",
        "--upgrade",
        *extras,
    ]
    pip_result = subprocess.run(pip_cmd, check=False)
    if pip_result.returncode != 0:
        raise SystemExit(pip_result.returncode)


def ensure_notebook_runtime(conda_bin: str, env_name: str) -> None:
    check_cmd = [
        conda_bin,
        "run",
        "-n",
        env_name,
        "python",
        "-c",
        "import papermill, nbconvert, yaml, matplotlib",
    ]
    check_result = subprocess.run(check_cmd, check=False)
    if check_result.returncode == 0:
        return

    install_cmd = [
        conda_bin,
        "run",
        "-n",
        env_name,
        "python",
        "-m",
        "pip",
        "install",
        "--upgrade",
        "papermill",
        "nbconvert",
        "pyyaml",
        "matplotlib",
    ]
    install_result = subprocess.run(install_cmd, check=False)
    if install_result.returncode != 0:
        raise SystemExit(install_result.returncode)

    final_check = subprocess.run(check_cmd, check=False)
    if final_check.returncode != 0:
        raise SystemExit(final_check.returncode)


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

    install_method, install_spec = install_tardis(conda_bin, env_name, setup_data, exec_env)

    extras = setup_data.get("environment", {}).get("extra_packages", [])
    if isinstance(extras, list) and extras:
        normalized_extras = [pkg for pkg in extras if isinstance(pkg, str) and pkg.strip()]
        if normalized_extras:
            install_extra_packages(conda_bin, env_name, normalized_extras, exec_env)

    ensure_notebook_runtime(conda_bin, env_name)

    verify_cmd = [
        conda_bin,
        "run",
        "-n",
        env_name,
        "python",
        "-c",
        "import tardis; print(tardis.__version__)",
    ]
    verify_result = subprocess.run(verify_cmd, check=False)
    if verify_result.returncode != 0:
        raise SystemExit(verify_result.returncode)

    payload = {
        "setup_yaml": str(setup_yaml),
        "env_name": env_name,
        "conda_bin": conda_bin,
        "lockfile_url": lockfile_url,
        "tardis_install_method": install_method,
        "tardis_install_spec": install_spec,
    }
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload))


if __name__ == "__main__":
    main()
