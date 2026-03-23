# 🖥️ Server Setup Guide (Azure VM)

## Prerequisites

- Linux VM with SSH access
- Miniconda installed (default path expected: `~/miniconda3/bin/conda`)
- Git installed
- Repo cloned on server
- Access to private repo via deploy key (if private)

## Required environment variables (optional overrides)

- `REPO_ROOT`
- `QUEUE_PATH`
- `OUT_ROOT`
- `CONDA_BIN`
- `CONTROL_ENV_NAME`

## Runner behavior

`server/run_on_azure_example.sh` now does:
1. `git restore .`
2. `git pull --ff-only origin <current_branch>`
3. recreates control env
4. processes queue
5. builds gallery

This ensures server state is fresh and up-to-date before every run.

## Manual execution

```bash
cd ~/tardis-proposal-demo
bash server/run_on_azure_example.sh
```

## Debug checklist

- Queue exists: `generated/server-queue.json`
- Conda path valid
- Notebook manifest produced: `out/notebook-manifest.json`
- Gallery built: `docs-site/index.html`
