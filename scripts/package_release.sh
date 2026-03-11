#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VERSION="${1:-$(date +%Y%m%d-%H%M%S)}"
OUT_DIR="dist"
ARCHIVE_NAME="polymarket-bot-${VERSION}.tar.gz"
ARCHIVE_PATH="${OUT_DIR}/${ARCHIVE_NAME}"

mkdir -p "$OUT_DIR"

# 打包源码（排除本地环境/缓存/构建产物）
tar \
  --exclude-vcs \
  --exclude='./.venv' \
  --exclude='./__pycache__' \
  --exclude='./.pytest_cache' \
  --exclude='./dist' \
  --exclude='./*.db' \
  --exclude='./*.sqlite' \
  -czf "$ARCHIVE_PATH" \
  .

echo "Package created: $ARCHIVE_PATH"
