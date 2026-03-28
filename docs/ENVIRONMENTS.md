# Environment Details

## CI control environment

Defined in `envs/ci-environment.yml`.

Used for:

- change detection
- setup metadata generation
- sanity execution orchestration
- notebook generation orchestration
- gallery build orchestration

## Optional server environment

Defined in `envs/server-environment.yml`.

Present for optional/legacy server-side experiments; not required for the main CI workflow.

## Per-config execution environment

Created from generated `setup.yaml`.

Contains:

- pinned TARDIS version or requested ref
- runtime tools like `papermill`, `nbconvert`, `pyyaml`, `matplotlib`
