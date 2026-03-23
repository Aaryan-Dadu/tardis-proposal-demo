# 🧪 Environment Details

## CI environment

Defined in `envs/ci-environment.yml`.

Purpose:
- run detection/generation scripts
- run sanity checks
- dispatch queue and sync outputs

Key points:
- Python 3.13 aligned with TARDIS requirement
- lightweight orchestration dependencies

## Server control environment

Created by `server/run_on_azure_example.sh`.

Purpose:
- run server orchestration scripts
- build gallery (`nbconvert`, `nbformat`)

## Per-config execution environments

Created by `server/setup_env_from_setup_yaml.py` using per-config `setup.yaml`:
- lockfile-based conda package resolution
- TARDIS install from requested git ref
- extra runtime packages ensured

Environment naming:
- sanitized from config/setup path (e.g., `a4-setups-2026-...`)

Lifecycle:
- created per queue item
- cleaned after run (to prevent disk growth)
