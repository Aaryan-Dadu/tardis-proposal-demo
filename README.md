# TARDIS Proposal Prototype

This prototype automates notebook generation and gallery publishing for TARDIS setups.

## Welcome mentors

Thank you for reviewing my GSoC proposal prototype. This repository shows the implementation in a working form. The `main` branch runs server based execution orchestrated by CI, while the `dev-only-ci` branch runs full notebook generation directly on GitHub CI runners. Generated notebooks and gallery outputs are included for review.

## For mentors

- `main` branch: server based flow with CI orchestration.
- `dev-only-ci` branch: CI runner only flow.
- Proposal text: `proposal.md`.
- Technical docs: `docs/README.md`.
- Generated outputs: `out/` and `docs-site/`.

## What it does

- Detects changed config files in `setups/`
- Generates per-config `setup.yaml`
- Runs notebook generation through explicit branch workflows (`main` server based, `dev-only-ci` CI runner only)
- Builds static gallery pages in `docs-site/`
- Publishes output notebooks and gallery

## Main branches

- `main`: server based flow, CI dispatches queue and publishes results
- `dev-only-ci`: CI runner only flow, no server dependency

## Quick run

1. Edit or add a config in `setups/`
2. Push to the target branch
3. Open Actions tab and watch workflow logs
4. Check generated notebooks in `out/` and gallery in `docs-site/`

## Documentation

See [docs/README.md](docs/README.md) for architecture, setup, environment, and usage details.

## Feedback

Please share your feedback [here](https://github.com/Aaryan-Dadu/tardis-proposal-demo/issues/1)
