#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-http://127.0.0.1:5000}"

cyan() { printf "\033[36m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
red() { printf "\033[31m%s\033[0m\n" "$*"; }

fail() { red "FAIL: $*"; exit 1; }

check_http() {
  local url="$1"
  local code
  code=$(curl -sS -o /dev/null -w "%{http_code}" "$url") || true
  [[ "$code" == "200" ]] || fail "$url -> HTTP $code"
  green "OK 200: $url"
}

check_json() {
  local url="$1"
  local headers
  headers=$(curl -sSI "$url") || true
  echo "$headers" | grep -iq "content-type: application/json" || fail "Content-Type JSON ausente em $url"
  green "OK JSON: $url"
}

check_header() {
  local url="$1" name="$2"
  curl -sSI "$url" | grep -i "^$name:" >/dev/null || fail "Header $name ausente em $url"
  green "OK header $name: $url"
}

cyan "Base: $BASE"

# Raiz
check_http "$BASE/"
# Conteúdos
check_http "$BASE/conteudos"
# Educational API
check_http "$BASE/api/educational"
check_json "$BASE/api/educational"
check_header "$BASE/api/educational" "ETag"
check_header "$BASE/api/educational" "Cache-Control"
# Nearby API (lat/lon exemplo: São Paulo)
NEAR="$BASE/api/nearby?lat=-23.55&lon=-46.63&radius_km=10&limit=5"
check_http "$NEAR"
check_json "$NEAR"

# Opcional: exibe contagem
COUNT=$(curl -sS "$BASE/api/educational" | sed -n 's/.*"count"[[:space:]]*:[[:space:]]*\([0-9]\+\).*/\1/p' | head -n1 || true)
[[ -n "${COUNT:-}" ]] && cyan "Educational count: $COUNT"

green "Smoke tests concluídos com sucesso."
