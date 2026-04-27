#!/bin/bash
set -e

FORCE=false
VERSION=""

for arg in "$@"; do
  case "$arg" in
    -h|--help)
      echo "Usage: ./release.sh [options] <version>"
      echo ""
      echo "  Tags and releases a new version from main."
      echo ""
      echo "  Arguments:"
      echo "    <version>          Semantic version to release (e.g. 0.2.1)"
      echo ""
      echo "  Options:"
      echo "    -f, --force        Skip clean working tree check"
      echo "    -h, --help         Show this help message"
      exit 0
      ;;
    -f|--force)
      FORCE=true
      ;;
    *)
      VERSION="$arg"
      ;;
  esac
done

if [ -z "$VERSION" ]; then
  echo "Usage: ./release.sh [options] <version>  (e.g. ./release.sh 0.2.1)"
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: invalid version '$VERSION', expected format X.Y.Z (e.g. 0.2.1)"
  exit 1
fi

# Ensure we're on main
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "Error: must be on main branch (currently on $CURRENT_BRANCH)"
  exit 1
fi

# Ensure working tree is clean
if [ -n "$(git status --porcelain)" ]; then
  if [ "$FORCE" = true ]; then
    echo "Warning: working tree is not clean, continuing anyway (--force)"
  else
    echo "Error: working tree is not clean, commit or stash changes first"
    echo "       Use -f or --force to skip this check"
    exit 1
  fi
fi

# Tag, push and create GitHub release
git tag -a "$VERSION" -m "$VERSION"
git push origin main
git push origin "$VERSION"
gh release create "$VERSION" --title "$VERSION" --generate-notes

echo "Released v$VERSION successfully"
