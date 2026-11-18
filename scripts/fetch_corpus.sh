#!/usr/bin/env bash
# Sparse-clone the Information Technology department GRs from orgpedia/mahGRs.
# The full repository is large; only GRs/Information_Technology_Department/ is checked out.
# Corpus: https://github.com/orgpedia/mahGRs (MIT licence, Orgpedia Foundation).
set -euo pipefail

REPO_URL="https://github.com/orgpedia/mahGRs.git"
# Pinned commit so every run indexes the same corpus. Change deliberately.
COMMIT="c96e88f731589e1284ecab60ff1a63d3b9c6bb82"
DEST="${1:-data/mahGRs}"
SUBDIR="GRs/Information_Technology_Department"

if [ ! -d "$DEST/.git" ]; then
  mkdir -p "$(dirname "$DEST")"
  git clone --filter=blob:none --no-checkout "$REPO_URL" "$DEST"
fi

cd "$DEST"
git sparse-checkout set --no-cone "/$SUBDIR/" /LICENSE /README.md
git fetch --depth 1 origin "$COMMIT" 2>/dev/null || git fetch origin
git checkout -q --detach "$COMMIT"

echo "Corpus at $DEST (commit $COMMIT)"
echo "Files in $SUBDIR: $(ls "$SUBDIR" | wc -l)"
