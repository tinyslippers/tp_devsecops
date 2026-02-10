#!/bin/bash
set -euo pipefail

# Configuration
SERVICE="${SERVICE:-catalog}"
BASE_URL="${BASE_URL:-http://localhost:5002}"
MAX_5XX="${MAX_5XX:-0}"
MAX_P95_MS="${MAX_P95_MS:-400}"
MAX_TRAV="${MAX_TRAV:-0}"

mkdir -p reports

# 1. Marqueur de temps pour extraire les logs récents
START_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "[gate] 1) Traffic generation..."
BASE_URL="$BASE_URL" bash monitoring/traffic.sh

echo "[gate] 2) Extracting logs since $START_TS..."
docker compose -f compose.staging.yml logs --no-log-prefix --since "$START_TS" "$SERVICE" > "reports/${SERVICE}_logs.raw"
grep -E '^\{' "reports/${SERVICE}_logs.raw" > "reports/${SERVICE}_logs.jsonl" || true

if [ ! -s "reports/${SERVICE}_logs.jsonl" ]; then
  echo "[gate] ERROR: No JSON logs found."
  exit 1
fi

echo "[gate] 3) Computing metrics..."
python3 monitoring/log_metrics.py "reports/${SERVICE}_logs.jsonl" "reports/log_report.json"

echo "[gate] 4) Checking thresholds..."
# Extraction des valeurs pour comparaison [cite: 81]
COUNT_5XX="$(python3 -c 'import json; print(json.load(open("reports/log_report.json"))["count_5xx"])')"
P95="$(python3 -c 'import json; print(json.load(open("reports/log_report.json"))["p95_latency_ms"])')"
TRAV="$(python3 -c 'import json; print(json.load(open("reports/log_report.json"))["patterns"]["path_traversal_hits"])')"

echo "[gate] Observed: 5xx=$COUNT_5XX | p95=${P95}ms | traversal=$TRAV"

# 5. Application des seuils [cite: 81, 82, 83, 84]
if [ "$COUNT_5XX" -gt "$MAX_5XX" ]; then echo "[gate] FAIL: too many HTTP 5xx"; exit 1; fi
if [ "$P95" -gt "$MAX_P95_MS" ]; then echo "[gate] FAIL: p95 latency too high"; exit 1; fi
if [ "$TRAV" -gt "$MAX_TRAV" ]; then echo "[gate] FAIL: suspicious traversal pattern detected"; exit 1; fi

echo "[gate] OK"
