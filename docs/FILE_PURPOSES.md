# File Purpose Map

## Top level

- `README.md`: project overview
- `Tardis-Proposal.md`: proposal text
- `setups/`: input config files
- `templates/`: notebook template
- `docs/`: technical docs
- `docs-site/`: static gallery output

## Workflow files

- `.github/workflows/dev-only-ci.yml`: main CI workflow (detect, setup generation, sanity, notebook generation, gallery build, commit artifacts)
- `.github/workflows/static.yml`: GitHub Pages deployment workflow triggered from successful CI runs on `main`

## Scripts

- `scripts/detect_changed_configs.py`: detect changed setup files
- `scripts/generate_setup_yamls.py`: generate setup metadata per config
- `scripts/create_sanity_configs.py`: generate reduced sanity configs
- `scripts/run_setup_yaml_sanity.py`: create per-config env and execute reduced sanity runs
- `scripts/run_full_notebook_generation.py`: run full notebook generation
- `scripts/build_gallery.py`: generate static gallery pages
- `scripts/setup_env_from_setup_yaml.py`: create conda env from generated setup metadata
- `scripts/plot_from_config.py`: render TARDIS outputs from config

## Generated outputs

- `generated/`: runtime manifests and sanity artifacts
- `out/`: generated notebooks and `out/notebook-manifest.json`
- `docs-site/`: rendered gallery HTML and viewers
