#!/usr/bin/env bash
# Re-fetch the corpus: the Information Technology department GRs from orgpedia/mahGRs
# at the pinned commit, copied unchanged into corpus/.
# The corpus already ships in corpus/; this script is only needed to re-create it.
# Source: https://github.com/orgpedia/mahGRs (MIT licence, Orgpedia Foundation).
set -euo pipefail

REPO_URL="https://github.com/orgpedia/mahGRs.git"
# Pinned commit so every run indexes the same corpus. Change deliberately.
COMMIT="c96e88f731589e1284ecab60ff1a63d3b9c6bb82"
CLONE="${1:-data/mahGRs}"     # sparse clone (git-ignored)
TARGET="${2:-corpus}"         # where the engine reads the corpus
SUBDIR="GRs/Information_Technology_Department"

if [ ! -d "$CLONE/.git" ]; then
  mkdir -p "$(dirname "$CLONE")"
  git clone --filter=blob:none --no-checkout "$REPO_URL" "$CLONE"
fi

(
  cd "$CLONE"
  # The full repository is large; only the IT-department folder is checked out.
  git sparse-checkout set --no-cone "/$SUBDIR/" /LICENSE /README.md
  git fetch --depth 1 origin "$COMMIT" 2>/dev/null || git fetch origin
  git checkout -q --detach "$COMMIT"
)

mkdir -p "$TARGET"
cp "$CLONE/$SUBDIR"/* "$TARGET"/
echo "Copied $(ls "$CLONE/$SUBDIR" | wc -l) files from $SUBDIR at $COMMIT into $TARGET/"
