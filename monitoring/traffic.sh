#!/bin/bash
# monitoring/traffic.sh
set -euo pipefail
BASE_URL="${BASE_URL:-http://localhost:5002}"

echo "[traffic] normal traffic"
for i in $(seq 1 30); do
  curl -fsS "$BASE_URL/health" >/dev/null
done

echo "[traffic] search traffic"
curl -s "$BASE_URL/search?q=abc" >/dev/null || true

# Mode “suspect” pour tester la gate plus tard (Partie E)
if [ "${SUSPECT_MODE:-0}" = "1" ]; then
  echo "[traffic] suspect traffic"
  curl -s "$BASE_URL/report?file=../../etc/passwd" >/dev/null || true
  curl -s "$BASE_URL/debug/run?cmd=id" >/dev/null || true
fi

echo "[traffic] done"
