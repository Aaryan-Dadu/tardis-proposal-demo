from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Process server queue and generate notebooks.")
    parser.add_argument("--queue", default="generated/server-queue.json")
    parser.add_argument("--output-root", default="out")
    parser.add_argument("--conda-bin", default=None)
    args = parser.parse_args()

    queue = json.loads(Path(args.queue).read_text(encoding="utf-8"))
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    repo_root = Path.cwd().resolve()
    conda_bin = resolve_conda_bin(args.conda_bin)

    generated = []
    for item in queue:
        config = item["config"]
        atom_data = item.get("atom_data", "kurucz_cd23_chianti_H_He_latest")
        setup_yaml = item.get("setup_yaml")

        if not setup_yaml:
            print(f"Skipping {config}: setup_yaml missing in queue item")
            continue

        env_name = sanitize_env_name(str(Path(setup_yaml).parent))
        setup_cmd = [
            "python",
            "server/setup_env_from_setup_yaml.py",
            "--setup-yaml",
            setup_yaml,
            "--env-name",
            env_name,
            "--conda-bin",
            conda_bin,
        ]
        setup_result = subprocess.run(setup_cmd, check=False)

        target = (output_root / Path(config).parent / f"{Path(config).stem}.ipynb").resolve()
        try:
            notebook_path_for_manifest = str(target.relative_to(repo_root))
        except ValueError:
            notebook_path_for_manifest = str(target)

        if setup_result.returncode != 0:
            generated.append(
                {
                    "config": config,
                    "notebook": notebook_path_for_manifest,
                    "notebook_exists": target.exists(),
                    "setup_yaml": setup_yaml,
                    "env_name": env_name,
                    "status": "failed",
                    "reason": "setup_env_failed",
                    "returncode": setup_result.returncode,
                }
            )
            continue

        cmd = [
            conda_bin,
            "run",
            "-n",
            env_name,
            "python",
            "server/run_notebook_for_config.py",
            "--config",
            config,
            "--atom-data",
            atom_data,
            "--output-notebook",
            str(target),
        ]
        result = subprocess.run(cmd, check=False)
        generated.append(
            {
                "config": config,
                "notebook": notebook_path_for_manifest,
                "notebook_exists": target.exists(),
                "setup_yaml": setup_yaml,
                "env_name": env_name,
                "status": "ok" if result.returncode == 0 else "failed",
                "reason": "notebook_execution_failed" if result.returncode != 0 else "ok",
                "returncode": result.returncode,
            }
        )

        # Clean up conda environment after successful execution
        if result.returncode == 0:
            cleanup_cmd = [conda_bin, "remove", "-n", env_name, "--all", "-y"]
            cleanup_result = subprocess.run(cleanup_cmd, check=False)
            if cleanup_result.returncode == 0:
                print(f"Cleaned up conda environment: {env_name}")
            else:
                print(f"Warning: Failed to clean up conda environment {env_name}")

    manifest = output_root / "notebook-manifest.json"
    manifest.write_text(json.dumps(generated, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(generated)} notebook(s)")


if __name__ == "__main__":
    main()
