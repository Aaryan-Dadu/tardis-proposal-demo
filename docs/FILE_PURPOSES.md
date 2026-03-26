# File Purpose Map

## Top level

- `README.md`: project overview
- `proposal.md`: GSoC proposal text
- `setups/`: input config files
- `templates/`: notebook template
- `docs/`: technical docs
- `docs-site/`: static gallery output

## Workflow files

- `.github/workflows/prototype-approach-4.yml`: main server workflow for TARDIS Proposal Prototype
- `.github/workflows/dev-only-ci.yml`: CI-only notebook generation workflow
- `.github/workflows/static.yml`: static pages deployment

## Scripts

- `scripts/detect_changed_configs.py`: detect changed setup files
- `scripts/generate_setup_yamls.py`: generate setup metadata per config
- `scripts/run_full_notebook_generation.py`: run full notebook generation in CI-only mode
- `scripts/build_gallery.py`: generate static gallery pages

## Server scripts

- `server/run_on_azure_example.sh`: server entry script
- `server/process_server_queue.py`: queue processor
- `server/setup_env_from_setup_yaml.py`: environment setup from setup metadata
- `server/run_notebook_for_config.py`: notebook execution helper
