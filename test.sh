#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ -z "${RECAF_JAR:-}" && ! -f "libs/recaf.jar" && ! -f "../recaf/recaf.jar" ]]; then
  echo "Missing recaf.jar. Set RECAF_JAR or place recaf.jar in libs/recaf.jar"
  exit 1
fi

echo "[1/3] Building plugin"
./gradlew jar

echo "[2/3] Checking Python entrypoint"
python recaf_mcp_server.py --help >/dev/null

echo "[3/3] Smoke test complete"
echo "If Recaf is running with the plugin loaded, you can also test:"
echo "  curl http://127.0.0.1:8750/health"
