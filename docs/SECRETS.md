# Secrets and Security

## Required secrets

- `AZURE_SERVER_HOST`
- `AZURE_SERVER_USER`
- `AZURE_SSH_PRIVATE_KEY`
- `AZURE_SERVER_REPO_PATH`

## Usage

- Secrets are used only in workflow steps that dispatch to server.
- If secrets are missing, workflow skips server-dispatch path.

## Security notes

- Never print private keys in logs
- Use least privilege for server user
