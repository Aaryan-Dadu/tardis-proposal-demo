# 🗂️ File Purpose Map

## Top-level

- `README.md` — Project overview and doc entrypoint
- `LICENSE` — Licensing terms
- `.gitignore` — Ignore policy for generated vs tracked assets

## Workflows

- `.github/workflows/prototype-approach-4.yml`
  - Main CI pipeline (detect, sanity, dispatch, sync-back, commit)
- `.github/workflows/deploy-gallery.yml`
  - Manual Pages deployment workflow
- `.github/workflows/static.yml`
  - Static Pages deployment workflow

## Scripts (`scripts/`)

- `detect_changed_configs.py` — Find changed setup configs in git diff
- `generate_setup_yamls.py` — Generate per-config `setup.yaml`
- `create_sanity_configs.py` — Prepare reduced CI sanity configs
- `run_setup_yaml_sanity.py` — Install from setup and run sanity checks
- `create_server_queue.py` — Build server queue payload
- `build_gallery.py` — Build `docs-site` + rendered notebook previews

## Server (`server/`)

- `run_on_azure_example.sh` — Server orchestrator entrypoint
- `process_server_queue.py` — Queue consumer + manifest writer
- `setup_env_from_setup_yaml.py` — Per-config env setup and TARDIS install
- `run_notebook_for_config.py` — Execute notebook via papermill

## Data/Artifacts

- `generated/` — Intermediate CI JSON artifacts
- `out/` — Generated notebooks and manifest
- `docs-site/` — Static gallery site for Pages
- `templates/config_report_template.ipynb` — Papermill notebook template

## Config Inputs

- `setups/**` — TARDIS configs and per-config setup metadata
- `envs/*.yml` — CI/server control environment specs
