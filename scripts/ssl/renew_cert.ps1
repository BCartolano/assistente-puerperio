# Renovar certificado Let's Encrypt (Windows)
docker compose -f docker-compose.prod-ssl.yml run --rm certbot renew --webroot -w /var/www/certbot --quiet
docker compose -f docker-compose.prod-ssl.yml exec -T nginx nginx -s reload
Write-Host "[OK] Renovação verificada e Nginx recarregado."
