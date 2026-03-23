# 🔐 Secrets and Security

## Required GitHub secrets

- `AZURE_SERVER_HOST`
- `AZURE_SERVER_USER`
- `AZURE_SSH_PRIVATE_KEY`
- `AZURE_SERVER_REPO_PATH`

These are validated in workflow before dispatch.

## What each secret does

- **HOST/USER**: identifies SSH destination
- **SSH_PRIVATE_KEY**: authenticates CI to server
- **REPO_PATH**: remote repo directory for queue and runner

## Private repo access on server

Use a deploy key on the VM for read/write as needed:
- add public key in repo Deploy Keys
- configure `~/.ssh/config` for `github.com`
- use SSH remote URL (`git@github.com:owner/repo.git`)

## Security notes

- Never echo private keys in logs
- Use least privilege (read-only deploy keys if possible)\
- Keep server user permissions minimal
