#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
QUEUE_PATH="${QUEUE_PATH:-$REPO_ROOT/generated/server-queue.json}"
OUT_ROOT="${OUT_ROOT:-$REPO_ROOT/out}"
CONDA_BIN="${CONDA_BIN:-$HOME/miniconda3/bin/conda}"
CONTROL_ENV_NAME="${CONTROL_ENV_NAME:-a4-control}"
TARGET_REF="${TARGET_REF:-}"

if [[ ! -x "$CONDA_BIN" ]]; then
  echo "Conda binary not found at $CONDA_BIN"
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is not available on the server"
  exit 1
fi

cd "$REPO_ROOT"

TMP_QUEUE_BACKUP=""
if [[ -f "$QUEUE_PATH" ]]; then
  TMP_QUEUE_BACKUP="$(mktemp /tmp/a4-server-queue.XXXXXX.json)"
  cp "$QUEUE_PATH" "$TMP_QUEUE_BACKUP"
  echo "Backed up queue payload to $TMP_QUEUE_BACKUP"
fi

echo "Resetting local repository to a clean state before sync..."
git reset --hard HEAD
git clean -fd

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "Pulling latest changes from origin/${CURRENT_BRANCH}..."
git pull --ff-only origin "$CURRENT_BRANCH"

if [[ -n "$TARGET_REF" ]]; then
  echo "Checking out target ref: $TARGET_REF"
  git fetch --all --tags --prune
  git checkout --force "$TARGET_REF"
fi

if [[ -n "$TMP_QUEUE_BACKUP" && -f "$TMP_QUEUE_BACKUP" ]]; then
  mkdir -p "$(dirname "$QUEUE_PATH")"
  cp "$TMP_QUEUE_BACKUP" "$QUEUE_PATH"
  rm -f "$TMP_QUEUE_BACKUP"
  echo "Restored queue payload to $QUEUE_PATH"
fi

"$CONDA_BIN" env remove -n "$CONTROL_ENV_NAME" -y >/dev/null 2>&1 || true
"$CONDA_BIN" create -y -n "$CONTROL_ENV_NAME" python=3.13 pyyaml nbconvert nbformat

"$CONDA_BIN" run -n "$CONTROL_ENV_NAME" python server/process_server_queue.py \
  --queue "$QUEUE_PATH" \
  --output-root "$OUT_ROOT" \
  --conda-bin "$CONDA_BIN"

"$CONDA_BIN" run -n "$CONTROL_ENV_NAME" python scripts/build_gallery.py \
  --manifest "$OUT_ROOT/notebook-manifest.json" \
  --output-dir "$REPO_ROOT/docs-site"
