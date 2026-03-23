#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
QUEUE_PATH="${QUEUE_PATH:-$REPO_ROOT/generated/server-queue.json}"
OUT_ROOT="${OUT_ROOT:-$REPO_ROOT/out}"
CONDA_BIN="${CONDA_BIN:-$HOME/miniconda3/bin/conda}"
CONTROL_ENV_NAME="${CONTROL_ENV_NAME:-a4-control}"

if [[ ! -x "$CONDA_BIN" ]]; then
  echo "Conda binary not found at $CONDA_BIN"
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is not available on the server"
  exit 1
fi

cd "$REPO_ROOT"

echo "Resetting tracked local changes before sync..."
git restore .

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "Pulling latest changes from origin/${CURRENT_BRANCH}..."
git pull --ff-only origin "$CURRENT_BRANCH"

"$CONDA_BIN" env remove -n "$CONTROL_ENV_NAME" -y >/dev/null 2>&1 || true
"$CONDA_BIN" create -y -n "$CONTROL_ENV_NAME" python=3.13 pyyaml nbconvert nbformat

"$CONDA_BIN" run -n "$CONTROL_ENV_NAME" python server/process_server_queue.py \
  --queue "$QUEUE_PATH" \
  --output-root "$OUT_ROOT" \
  --conda-bin "$CONDA_BIN"

"$CONDA_BIN" run -n "$CONTROL_ENV_NAME" python scripts/build_gallery.py \
  --manifest "$OUT_ROOT/notebook-manifest.json" \
  --output-dir "$REPO_ROOT/docs-site"
