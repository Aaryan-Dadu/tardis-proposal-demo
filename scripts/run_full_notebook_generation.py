#!/usr/bin/env python
"""
Run full notebook generation for all detected config changes.
Executes directly in CI without server dispatch (dev-only-ci workflow).
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def resolve_project_path(path: Path, project_root: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root / path


def project_relative_or_name(path: Path, project_root: Path) -> Path:
    try:
        return path.relative_to(project_root)
    except ValueError:
        return Path(path.name)


def load_manifest_rows(manifest_path: Path) -> list[dict]:
    """Load manifest with graceful fallback for empty/corrupt files."""
    if not manifest_path.exists():
        logger.warning(f"Manifest not found: {manifest_path}")
        return []
    
    try:
        content = manifest_path.read_text(encoding="utf-8").strip()
        if not content:
            logger.warning(f"Manifest is empty: {manifest_path}")
            return []
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse manifest JSON: {e}")
        return []


def run_papermill_for_config(
    config_path: Path,
    env_name: str,
    atom_data: str,
    output_dir: Path,
    template_path: Path,
) -> bool:
    """Execute notebook with papermill for a single config."""
    project_root = Path.cwd().resolve()
    resolved_config_path = resolve_project_path(config_path, project_root)

    # Make output mirror the config's folder structure
    relative_config_dir = project_relative_or_name(resolved_config_path.parent, project_root)
    mirrored_output_dir = output_dir / relative_config_dir

    mirrored_output_dir.mkdir(parents=True, exist_ok=True)

    output_nb = mirrored_output_dir / f"{config_path.stem}.ipynb"
    
    logger.info(f"Generating notebook for {config_path.name}")
    logger.info(f"  Output: {output_nb}")
    logger.info(f"  Environment: {env_name}")
    
    cmd = [
        "conda", "run",
        "-n", env_name,
        "papermill",
        "--log-level", "INFO",
        "-k", "python3",
        str(template_path),
        str(output_nb),
    ]
    
    try:
        run_env = os.environ.copy()
        run_env["CONFIG_PATH"] = str(project_relative_or_name(resolved_config_path, project_root))
        run_env["ATOM_DATA"] = atom_data
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=False,
            text=True,
            timeout=3600,  # 60 min timeout per notebook
            env=run_env,
        )
        
        if result.returncode == 0:
            logger.info(f"✓ Successfully generated {output_nb}")
            return True
        else:
            logger.error(f"✗ Notebook generation failed for {config_path.name}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"✗ Notebook generation timed out for {config_path.name}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error generating notebook for {config_path.name}: {e}")
        return False


def env_name_for_config(config_path: Path) -> str:
    raw = str(config_path.with_suffix("")).replace("/", "-").replace("_", "-")
    return f"a4-{raw}"[:80]


def load_setup_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return {}
    return data


def ensure_conda_env(setup_yaml: Path, env_name: str) -> bool:
    cmd = [
        "python",
        "scripts/setup_env_from_setup_yaml.py",
        "--setup-yaml",
        str(setup_yaml),
        "--env-name",
        env_name,
    ]
    result = subprocess.run(cmd, check=False)
    return result.returncode == 0


def normalize_atom_data(atom_data: str) -> str:
    candidate = atom_data.strip()
    if not candidate:
        return "kurucz_cd23_chianti_H_He_latest"

    candidate_path = Path(candidate)
    if candidate_path.suffix.lower() == ".h5" and not candidate_path.exists():
        return candidate_path.stem
    return candidate


def create_notebook_manifest(output_dir: Path) -> None:
    """Create manifest of generated notebooks."""
    manifest_path = output_dir / "notebook-manifest.json"
    
    notebooks = list(output_dir.glob("**/*.ipynb"))
    manifest = []
    
    for nb_path in sorted(notebooks):
        entry = {
            "notebook_path": str(nb_path.relative_to(Path.cwd())),
            "config_name": nb_path.stem,
        }
        manifest.append(entry)
    
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8"
    )
    logger.info(f"Created manifest with {len(manifest)} notebooks: {manifest_path}")


def main() -> int:
    """Main entry point."""
    project_root = Path.cwd().resolve()
    generated_dir = project_root / "generated"
    output_dir = project_root / "out"
    template_path = project_root / "templates" / "config_report_template.ipynb"
    
    # Ensure template exists
    if not template_path.exists():
        logger.error(f"Template not found: {template_path}")
        return 1
    
    # Load setup.yaml manifest
    setup_manifest_path = generated_dir / "setup-generation-manifest.json"
    setup_entries = load_manifest_rows(setup_manifest_path)
    
    if not setup_entries:
        logger.warning("No setup.yaml entries found in manifest.")
        return 0
    
    logger.info(f"Found {len(setup_entries)} setup.yaml entries")
    
    successful = 0
    failed = 0
    
    for entry in setup_entries:
        if not isinstance(entry, dict):
            logger.warning(f"Skipping invalid manifest entry: {entry}")
            continue
        
        setup_yaml_path = resolve_project_path(Path(entry.get("setup_yaml", "")), project_root)
        if not setup_yaml_path.exists():
            logger.warning(f"setup.yaml not found: {setup_yaml_path}")
            continue
        
        config_str = entry.get("config") or entry.get("config_file_path")
        config_path = Path(config_str) if isinstance(config_str, str) and config_str.strip() else Path()
        resolved_config_path = resolve_project_path(config_path, project_root) if config_path != Path() else Path()

        setup_data = load_setup_yaml(setup_yaml_path)
        if (not resolved_config_path.exists()) and isinstance(setup_data, dict):
            setup_config_path = setup_data.get("config", {}).get("path")
            if isinstance(setup_config_path, str) and setup_config_path.strip():
                config_path = Path(setup_config_path)
                resolved_config_path = resolve_project_path(config_path, project_root)

        if not resolved_config_path.exists():
            logger.warning(f"Invalid entry: config path missing for setup {setup_yaml_path}")
            continue

        env_name = env_name_for_config(project_relative_or_name(resolved_config_path, project_root))
        atom_data = normalize_atom_data(
            str(entry.get("atom_data") or setup_data.get("config", {}).get("atom_data") or "kurucz_cd23_chianti_H_He_latest")
        )
        logger.info(f"Preparing environment for {resolved_config_path.name}: {env_name}")
        if not ensure_conda_env(setup_yaml_path, env_name):
            logger.error(f"✗ Environment setup failed for {setup_yaml_path}")
            failed += 1
            continue
        
        # Run papermill for this config
        success = run_papermill_for_config(
            config_path=resolved_config_path,
            env_name=env_name,
            atom_data=atom_data,
            output_dir=output_dir,
            template_path=template_path,
        )
        
        if success:
            successful += 1
        else:
            failed += 1
    
    logger.info(f"\nNotebook generation summary:")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Failed: {failed}")
    
    # Create manifest of generated notebooks
    if successful > 0:
        create_notebook_manifest(output_dir)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
