#!/usr/bin/env bash
# Thin wrapper around tools/release.py.
#
# Usage:
#   ./tools/release.sh <addon-id> <new-version> [news-string]
#
# Examples:
#   ./tools/release.sh plugin.video.sporthdme 0.1.85
#   ./tools/release.sh plugin.video.sporthdme 0.1.85 "- fix s2watch\n- super.league.st"
#
# Add --dry-run as the last arg to preview without writing.

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <addon-id> <new-version> [news] [--dry-run]" >&2
  exit 2
fi

ADDON="$1"
VERSION="$2"
shift 2

NEWS=""
DRY_RUN=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN="--dry-run" ;;
    *) NEWS="$arg" ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CMD=(python3 "$REPO_ROOT/tools/release.py" --addon "$ADDON" --version "$VERSION")
if [[ -n "$NEWS" ]]; then
  CMD+=(--news "$NEWS")
fi
if [[ -n "$DRY_RUN" ]]; then
  CMD+=("$DRY_RUN")
fi

"${CMD[@]}"
