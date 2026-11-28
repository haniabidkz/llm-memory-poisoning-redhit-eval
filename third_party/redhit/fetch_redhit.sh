#!/usr/bin/env bash
# Fetch the RedHit source (CyberScienceLab/Our-Papers, RedHit/ folder) at a pinned
# commit into third_party/redhit/src/. The code is not copied into this repo, see NOTICE.md.
set -euo pipefail

REPO_URL="https://github.com/CyberScienceLab/Our-Papers.git"
COMMIT="${REDHIT_COMMIT:-3093c9b1f9a1b4ce1588f4fd99460a1cecf10db3}"
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HERE/src"

if [ -d "$DEST/.git" ]; then
  echo "RedHit already fetched at $DEST"
  git -C "$DEST" log -1 --format='commit %H (%ci)'
  exit 0
fi

git clone --filter=blob:none --no-checkout "$REPO_URL" "$DEST"
git -C "$DEST" sparse-checkout set RedHit
git -C "$DEST" checkout --quiet "$COMMIT"
git -C "$DEST" log -1 --format='fetched commit %H (%ci)'
