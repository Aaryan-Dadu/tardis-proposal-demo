from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

DEFAULT_TARDIS_CONDA_SPEC = "tardis-sn"
DEFAULT_TARDIS_REQUEST = "release-latest"
DEFAULT_LOCKFILE_URL = "https://raw.githubusercontent.com/tardis-sn/tardisbase/refs/heads/master/conda-linux-64.lock"


def normalize_conda_spec(version: str | None) -> str:
    if version is None:
        return DEFAULT_TARDIS_CONDA_SPEC

    cleaned = version.strip()
    if not cleaned:
        return DEFAULT_TARDIS_CONDA_SPEC

    if cleaned in {"master", "main", "latest", "release-latest"}:
        return DEFAULT_TARDIS_CONDA_SPEC

    return f"tardis-sn={cleaned}"


def infer_tardis_spec(config_path: Path) -> str:
    if config_path.suffix.lower() == ".csvy":
        text = config_path.read_text(encoding="utf-8")
        if "tardis_version:" in text:
            version = text.split("tardis_version:", 1)[1].splitlines()[0].strip().strip("\"'")
            return normalize_conda_spec(version)
        return DEFAULT_TARDIS_CONDA_SPEC

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    for key in ("tardis_version", "tardis-tag", "tardis_tag"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return normalize_conda_spec(value)

    metadata = data.get("metadata", {})
    if isinstance(metadata, dict):
        value = metadata.get("tardis_version")
        if isinstance(value, str) and value.strip():
            return normalize_conda_spec(value)

    return DEFAULT_TARDIS_CONDA_SPEC


def infer_tardis_request(config_path: Path) -> str:
    if config_path.suffix.lower() == ".csvy":
        text = config_path.read_text(encoding="utf-8")
        if "tardis_version:" in text:
            version = text.split("tardis_version:", 1)[1].splitlines()[0].strip().strip("\"'")
            return version or DEFAULT_TARDIS_REQUEST
        return DEFAULT_TARDIS_REQUEST

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    for key in ("tardis_version", "tardis-tag", "tardis_tag"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    metadata = data.get("metadata", {})
    if isinstance(metadata, dict):
        value = metadata.get("tardis_version")
        if isinstance(value, str) and value.strip():
            return value.strip()

    return DEFAULT_TARDIS_REQUEST


def extract_atom_data(config_path: Path) -> str:
    if config_path.suffix.lower() == ".csvy":
        return "kurucz_cd23_chianti_H_He_latest"

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    atom_data = data.get("atom_data")
    if isinstance(atom_data, str) and atom_data.strip():
        candidate = atom_data.strip()
        candidate_path = Path(candidate)
        if candidate_path.suffix.lower() == ".h5" and not candidate_path.exists():
            return candidate_path.stem
        return candidate
    return "kurucz_cd23_chianti_H_He_latest"


def create_setup_yaml(config_path: Path, tardis_spec: str, atom_data: str) -> Path:
    setup = {
        "setup_format_version": "approach-4-v1",
        "environment": {
            "name": "tardis-config-env",
            "lockfile_url": DEFAULT_LOCKFILE_URL,
            "override_channels": True,
            "channels": ["conda-forge"],
            "extra_packages": [
                "pyyaml",
                "matplotlib",
                "jupyterlab",
                "nbconvert",
                "papermill",
            ],
        },
        "tardis": {
            "install_source": "pip-git",
            "repo_url": "https://github.com/tardis-sn/tardis.git",
            "requested_ref": infer_tardis_request(config_path),
            "conda_spec": tardis_spec,
        },
        "config": {
            "path": str(config_path),
            "atom_data": atom_data,
        },
    }
    setup_path = config_path.parent / "setup.yaml"
    setup_path.write_text(yaml.safe_dump(setup, sort_keys=False), encoding="utf-8")
    return setup_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate per-config setup.yaml files.")
    parser.add_argument("--changed-json", default="generated/changed-configs.json")
    parser.add_argument("--output", default="generated/setup-generation-manifest.json")
    args = parser.parse_args()

    changed_payload = json.loads(Path(args.changed_json).read_text(encoding="utf-8"))
    configs = changed_payload.get("configs", [])

    rows = []
    for config_str in configs:
        config_path = Path(config_str)
        if not config_path.exists() or config_path.name == "setup.yaml":
            continue
        tardis_spec = infer_tardis_spec(config_path)
        atom_data = extract_atom_data(config_path)
        setup_path = create_setup_yaml(config_path, tardis_spec, atom_data)
        rows.append(
            {
                "config": str(config_path),
                "setup_yaml": str(setup_path),
                "tardis_conda_spec": tardis_spec,
                "atom_data": atom_data,
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"Generated setup.yaml for {len(rows)} config(s)")


if __name__ == "__main__":
    main()
