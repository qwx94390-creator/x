#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VERSION="${1:-$(date +%Y%m%d-%H%M%S)}"
OUT_DIR="dist"
PKG_DIR="polymarket-bot-${VERSION}"
ARCHIVE_NAME="${PKG_DIR}.tar.gz"
ARCHIVE_PATH="${OUT_DIR}/${ARCHIVE_NAME}"

mkdir -p "$OUT_DIR"

# 打包源码（排除本地环境/缓存/构建产物），并在压缩包内带顶层目录
# 解压后目录结构为：polymarket-bot-<version>/...
tar \
  --exclude-vcs \
  --exclude='./.venv' \
  --exclude='./__pycache__' \
  --exclude='./.pytest_cache' \
  --exclude='./dist' \
  --exclude='./*.db' \
  --exclude='./*.sqlite' \
  --transform "s#^\./#${PKG_DIR}/#" \
  -czf "$ARCHIVE_PATH" \
  .

echo "Package created: $ARCHIVE_PATH"
echo "Extract and run:"
echo "  tar -xzf $ARCHIVE_NAME"
echo "  cd $PKG_DIR"
echo "  bash scripts/run_local.sh"
