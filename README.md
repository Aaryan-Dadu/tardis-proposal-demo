# TARDIS Proposal Prototype

This prototype automates notebook generation and gallery publishing for TARDIS setups.

## Welcome mentors

Thank you for reviewing my GSoC proposal prototype. This repository shows the implementation in a working form. The `main` branch runs full notebook generation directly on GitHub CI runners, while the `server-based` branch runs server based execution orchestrated by CI. Generated notebooks and gallery outputs are included for review. Initially, `main` was based on server based approach that's why to have the stable prototype for reference of server-based approach is kept in `server-based` branch.

## For mentors

- `main` branch: CI runner only flow.
- `server-based` branch: server based flow with CI orchestration.
- Proposal text: `proposal.md`.
- Technical docs: `docs/README.md`.
- Generated outputs: `out/` and `docs-site/`.

## What it does

- Detects changed config files in `setups/`
- Generates per-config `setup.yaml`
- Runs notebook generation through explicit branch workflows (`main` CI runner only, `server-based` server based)
- Builds static gallery pages in `docs-site/`
- Publishes output notebooks and gallery

## Main branches

- `main`: Notebook generation and Gallery deployment using CI runner only
- `server-based`: Execution of notebook is done in a server, rest is same as `main`

## Quick run

1. Edit or add a config in `setups/`
2. Push to the target branch
3. Open Actions tab and watch workflow logs
4. Check generated notebooks in `out/` and gallery in `docs-site/`

### OR

Have a look at these workflows:
- A simple run on [tadis_example.yml](setups/2026/GSOC_2026_Paper/setup.yaml) on latest release of [tardis](https://github.com/tardis-sn/tardis):  
- Running [old_example.yml](setups/1987/Old_1987_Paper/old_example.yml) on a pinned version of [tardis](https://github.com/tardis-sn/tardis/tree/0d099a3fcabd6cf797d6c99bb809e0a7ad138ff8): 

## Documentation

See [docs/README.md](docs/README.md) for architecture, setup, environment, and usage details.

## Feedback

Please share your feedback [here](https://github.com/Aaryan-Dadu/tardis-proposal-demo/issues/1)
