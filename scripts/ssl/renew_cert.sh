#!/usr/bin/env bash
set -euo pipefail
docker compose -f docker-compose.prod-ssl.yml run --rm certbot renew --webroot -w /var/www/certbot --quiet
docker compose -f docker-compose.prod-ssl.yml exec -T nginx nginx -s reload || true
echo "[OK] Renovação verificada e Nginx recarregado."
