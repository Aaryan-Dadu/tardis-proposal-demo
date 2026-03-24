#!/usr/bin/env python
"""
Run full notebook generation for all detected config changes.
Executes directly in CI without server dispatch (dev-only-ci workflow).
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
    setup_yaml: Path,
    env_name: str,
    output_dir: Path,
    template_path: Path,
) -> bool:
    """Execute notebook with papermill for a single config."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Derive notebook name from config
    config_stem = config_path.stem
    output_nb = output_dir / f"{config_stem}.ipynb"
    
    logger.info(f"Generating notebook for {config_path.name}")
    logger.info(f"  Output: {output_nb}")
    logger.info(f"  Environment: {env_name}")
    
    cmd = [
        "conda", "run",
        "-n", env_name,
        "papermill",
        "--log-level", "INFO",
        "-p", "setup_yaml_path", str(setup_yaml),
        "-p", "config_file_path", str(config_path),
        str(template_path),
        str(output_nb),
    ]
    
    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=False,
            text=True,
            timeout=3600,  # 60 min timeout per notebook
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
    project_root = Path.cwd()
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
        
        setup_yaml_path = Path(entry.get("setup_yaml", ""))
        if not setup_yaml_path.exists():
            logger.warning(f"setup.yaml not found: {setup_yaml_path}")
            continue
        
        env_name = entry.get("env_name", "")
        config_path = Path(entry.get("config_file_path", ""))
        
        if not env_name or not config_path.exists():
            logger.warning(f"Invalid entry: env_name={env_name}, config={config_path}")
            continue
        
        # Run papermill for this config
        success = run_papermill_for_config(
            config_path=config_path,
            setup_yaml=setup_yaml_path,
            env_name=env_name,
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
