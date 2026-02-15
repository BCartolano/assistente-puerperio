#!/usr/bin/env bash
set -euo pipefail
DOMAINS="${DOMAINS:-seudominio.com}"
EMAIL="${CERTBOT_EMAIL:-seuemail@dominio.com}"
STAGING="${STAGING:-0}"
WEBROOT="/var/www/certbot"
ARGS=(certonly --webroot -w "$WEBROOT" --agree-tos --no-eff-email -m "$EMAIL")
if [ "$STAGING" = "1" ]; then ARGS+=(--staging); fi
for d in ${DOMAINS//,/ }; do ARGS+=(-d "$d"); done
docker compose -f docker-compose.prod-ssl.yml run --rm certbot "${ARGS[@]}"
docker compose -f docker-compose.prod-ssl.yml exec -T nginx nginx -t
docker compose -f docker-compose.prod-ssl.yml exec -T nginx nginx -s reload || true
echo "[OK] Certificado emitido. Troque para nginx.ssl.conf e reinicie o nginx se ainda não estiver usando SSL."
