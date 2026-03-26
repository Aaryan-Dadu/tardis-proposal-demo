# Environment Details

## CI control environment

Defined in `envs/ci-environment.yml`.

Used for:

- change detection
- setup metadata generation
- orchestration scripts

## Server control environment

Defined in `envs/server-environment.yml`.

Used for:

- queue processing
- gallery build

## Per-config execution environment

Created from generated `setup.yaml`.

Contains:

- pinned TARDIS version or requested ref
- runtime tools like `papermill`, `nbconvert`, `pyyaml`, `matplotlib`
