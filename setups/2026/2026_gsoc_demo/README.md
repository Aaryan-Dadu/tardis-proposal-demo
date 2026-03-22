# 2026 GSOC Demo Setups (Approach-4)

This folder mirrors the minimal structure used in approaches 1–3, but each config lives in its own subfolder so a local `setup.yaml` can sit beside it.

## Included examples

- `base/tardis_example.yml` (declares `metadata.tardis_version`)
- `variants/fast/tardis_example_fast.yml` (no explicit version, falls back to latest)
- `variants/downbranch/tardis_example_downbranch.yml` (declares top-level `tardis_version`)

Each config folder contains a `setup.yaml` prototype environment file.
