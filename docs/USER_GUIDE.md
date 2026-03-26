# User Guide

## Trigger a run

1. Add or edit a setup config in `setups/`
2. Push to the branch (`main` or `dev-only-ci`)
3. Check workflow run in GitHub Actions

## What happens automatically

1. Changed configs are detected
2. `setup.yaml` is generated per changed config
3. Notebook generation runs by branch (`main` server based, `dev-only-ci` CI runner only)
4. Gallery pages are built

## Where to check output

- Notebook outputs: `out/`
- Notebook manifest: `out/notebook-manifest.json`
- Static gallery: `docs-site/`

## Common failures

- Missing atom data: dataset is resolved by name or downloaded
- Invalid config: check workflow logs for exact TARDIS error
- Empty change set: no notebook generation is expected
