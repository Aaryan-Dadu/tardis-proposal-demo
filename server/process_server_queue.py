from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scripts.generate_setup_yamls import create_setup_yaml, extract_atom_data, infer_tardis_spec


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


def cleanup_conda_env(conda_bin: str, env_name: str) -> None:
    """Remove conda environment after use to save disk space."""
    cleanup_cmd = [conda_bin, "remove", "-n", env_name, "--all", "-y"]
    result = subprocess.run(cleanup_cmd, check=False, capture_output=True)
    if result.returncode == 0:
        print(f"Cleaned up environment: {env_name}")
    else:
        print(f"Warning: failed to cleanup environment {env_name}")


def tail_text(text: str, max_lines: int = 40) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[-max_lines:])


def resolve_setup_yaml(item: dict, repo_root: Path) -> str:
    setup_yaml_raw = item.get("setup_yaml")
    if not setup_yaml_raw:
        raise ValueError("setup_yaml missing in queue item")

    setup_yaml_path = Path(setup_yaml_raw)
    if not setup_yaml_path.is_absolute():
        setup_yaml_path = (repo_root / setup_yaml_path).resolve()

    if setup_yaml_path.exists():
        return str(setup_yaml_path)

    config_path = Path(item["config"])
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"config not found while regenerating setup.yaml: {config_path}")

    tardis_spec = item.get("tardis_conda_spec")
    if not isinstance(tardis_spec, str) or not tardis_spec.strip():
        tardis_spec = infer_tardis_spec(config_path)

    atom_data = item.get("atom_data")
    if not isinstance(atom_data, str) or not atom_data.strip():
        atom_data = extract_atom_data(config_path)

    regenerated = create_setup_yaml(config_path, tardis_spec, atom_data)
    return str(regenerated.resolve())


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
    template_path = (repo_root / "templates/config_report_template.ipynb").resolve()

    generated = []
    for item in queue:
        config = item["config"]
        atom_data = item.get("atom_data", "kurucz_cd23_chianti_H_He_latest")
        try:
            setup_yaml = resolve_setup_yaml(item, repo_root)
        except Exception as exc:  # noqa: BLE001
            target = (output_root / Path(config).parent / f"{Path(config).stem}.ipynb").resolve()
            try:
                notebook_path_for_manifest = str(target.relative_to(repo_root))
            except ValueError:
                notebook_path_for_manifest = str(target)

            generated.append(
                {
                    "config": config,
                    "notebook": notebook_path_for_manifest,
                    "notebook_exists": target.exists(),
                    "setup_yaml": item.get("setup_yaml"),
                    "env_name": "",
                    "status": "failed",
                    "reason": "setup_yaml_missing_or_invalid",
                    "returncode": 1,
                    "stderr_tail": str(exc),
                }
            )
            print(f"Skipping {config}: {exc}")
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
        setup_result = subprocess.run(setup_cmd, check=False, capture_output=True, text=True)

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
                    "stderr_tail": tail_text(setup_result.stderr or ""),
                }
            )
            cleanup_conda_env(conda_bin, env_name)
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
            "--template",
            str(template_path),
        ]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        generated.append(
            {
                "config": config,
                "notebook": notebook_path_for_manifest,
                "notebook_exists": target.exists(),
                "setup_yaml": setup_yaml,
                "template": str(template_path),
                "env_name": env_name,
                "status": "ok" if result.returncode == 0 else "failed",
                "reason": "notebook_execution_failed" if result.returncode != 0 else "ok",
                "returncode": result.returncode,
                "stderr_tail": tail_text(result.stderr or "") if result.returncode != 0 else "",
            }
        )
        cleanup_conda_env(conda_bin, env_name)

    manifest = output_root / "notebook-manifest.json"
    manifest.write_text(json.dumps(generated, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(generated)} notebook(s)")


if __name__ == "__main__":
    main()
