from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

def env_name_for_config(config_path: Path) -> str:
    raw = str(config_path.with_suffix("")).replace("/", "-").replace("_", "-")
    return f"a4-{raw}"[:80]


def accept_conda_tos() -> None:
    channels = [
        "https://repo.anaconda.com/pkgs/main",
        "https://repo.anaconda.com/pkgs/r",
    ]
    for channel in channels:
        subprocess.run(
            ["conda", "tos", "accept", "--override-channels", "--channel", channel],
            check=False,
            capture_output=True,
            text=True,
        )


def ensure_conda_env(setup_yaml: Path, env_name: str) -> None:
    result = subprocess.run(
        [
            "python",
            "server/setup_env_from_setup_yaml.py",
            "--setup-yaml",
            str(setup_yaml),
            "--env-name",
            env_name,
        ],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Environment setup failed for {setup_yaml}")


def run_sanity(config_path: Path, atom_data: str, env_name: str) -> bool:
    cmd = [
        "conda",
        "run",
        "-n",
        env_name,
        "python",
        "scripts/plot_from_config.py",
        str(config_path),
        "--atom-data",
        atom_data,
        "--output-dir",
        "generated/sanity-plots",
        "--output-prefix",
        config_path.stem,
    ]
    return subprocess.run(cmd, check=False).returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Install from setup.yaml and run sanity per config.")
    parser.add_argument("--sanity-manifest", default="generated/sanity-manifest.json")
    parser.add_argument("--output", default="generated/sanity-results.json")
    args = parser.parse_args()

    rows = json.loads(Path(args.sanity_manifest).read_text(encoding="utf-8"))
    results = []

    for row in rows:
        setup_yaml = Path(row["setup_yaml"])
        sanity_config = Path(row["sanity_config"])
        env_name = env_name_for_config(sanity_config)
        try:
            ensure_conda_env(setup_yaml, env_name)
            ok = run_sanity(sanity_config, row.get("atom_data", "kurucz_cd23_chianti_H_He_latest"), env_name)
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"Sanity setup failed for {setup_yaml}: {exc}")
        results.append({**row, "sanity_passed": ok})

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    if any(not item["sanity_passed"] for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
