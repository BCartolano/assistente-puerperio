#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-http://localhost:5000}"
curl -sf "$BASE/api/v1/chat/ping" >/dev/null
curl -sf -X POST "$BASE/api/v1/chat/intent" \
  -H 'Content-Type: application/json' \
  -d '{"intent":"publico_privado","slots":{"hospital":"Hospital Municipal","lat":-23.19,"lon":-45.79}}' >/dev/null
echo "[OK] chat smoke"
