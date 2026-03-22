# Azure Server Setup for Approach-4

This file describes what CI expects on the Azure VM.

## Required GitHub Secrets

Set these repository secrets:

- `AZURE_SERVER_HOST` (example: `57.158.25.120`)
- `AZURE_SERVER_USER` (example: `azureuser`)
- `AZURE_SSH_PRIVATE_KEY` (private key content, PEM format)
- `AZURE_SERVER_REPO_PATH` (absolute path on VM, example: `/home/azureuser/tardis-proposal-demo`)

## Required VM State

1. Repo exists at `AZURE_SERVER_REPO_PATH`.
2. Miniconda is installed (default expected path): `/home/azureuser/miniconda3/bin/conda`.
3. Server has outbound internet access (for lockfile download and package installs).

## What CI does to server

1. Creates `${AZURE_SERVER_REPO_PATH}/generated`.
2. Uploads `generated/server-queue.json` via `scp`.
3. Executes:

```bash
cd ${AZURE_SERVER_REPO_PATH}
bash server/run_on_azure_example.sh
```

## What server script does

`server/run_on_azure_example.sh`:

1. Ensures conda binary exists.
2. Creates a control env (`a4-control`) for orchestration scripts.
3. Runs `server/process_server_queue.py`.
4. For each queued config:
   - runs `server/setup_env_from_setup_yaml.py` to create config env from lockfile + install TARDIS,
   - executes notebook template,
   - writes notebook under `out/...`.
5. Builds `docs-site/index.html` gallery from generated notebook manifest.
