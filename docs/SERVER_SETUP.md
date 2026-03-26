# Server Setup Guide

Use this only if running server-dispatch mode from `main` workflow.

## Prerequisites

- Linux VM with conda installed
- SSH access from GitHub Actions
- Repository cloned on server

## Required secrets

- `AZURE_SERVER_HOST`
- `AZURE_SERVER_USER`
- `AZURE_SSH_PRIVATE_KEY`
- `AZURE_SERVER_REPO_PATH`

## Server run command

From workflow, server entrypoint is:

```bash
bash server/run_on_azure_example.sh
```

## What server script does

1. Syncs repository to target ref
2. Reads queue from `generated/server-queue.json`
3. Sets up per-config environments
4. Runs notebook generation
5. Builds gallery artifacts
