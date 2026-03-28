# User Guide

## Trigger a run

1. Add or edit a setup config in `setups/`
2. Push to `main`
3. Check workflow run in GitHub Actions

## What happens automatically

1. Changed configs are detected
2. `setup.yaml` is generated per changed config
3. Reduced sanity configs are executed
4. Full notebooks are generated in CI
5. Gallery pages are built
6. On `main` push (non-PR), generated `out/` and `docs-site/` are committed
7. `static.yml` deploys `docs-site/` to GitHub Pages

## Where to check output

- Notebook outputs: `out/`
- Notebook manifest: `out/notebook-manifest.json`
- Static gallery: `docs-site/`
- CI artifacts: `main-ci-artifacts`

## Common failures

- Missing atom data: dataset is resolved by name or downloaded
- Invalid config: check workflow logs for exact TARDIS error
- Empty change set: no notebook generation is expected
- Push race during CI: workflow retries push with fetch/rebase logic; latest run should own final generated commit
