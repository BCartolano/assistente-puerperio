# Emitir certificado Let's Encrypt (Windows)
# Uso: .\issue_cert.ps1 -Domains "dominio.com,www.dominio.com" -Email "seu@email.com" [-Staging 1]
Param(
    [string]$Domains = $env:DOMAINS,
    [string]$Email = $env:CERTBOT_EMAIL,
    [int]$Staging = 0
)
$webroot = "/var/www/certbot"
$args = @("certonly", "--webroot", "-w", $webroot, "--agree-tos", "--no-eff-email", "-m", $Email)
if ($Staging -eq 1) { $args += "--staging" }
foreach ($d in $Domains.Split(",")) { $args += "-d"; $args += $d.Trim() }
docker compose -f docker-compose.prod-ssl.yml run --rm certbot $args
docker compose -f docker-compose.prod-ssl.yml exec -T nginx nginx -t
docker compose -f docker-compose.prod-ssl.yml exec -T nginx nginx -s reload
Write-Host "[OK] Certificado emitido. Troque para nginx.ssl.conf e reinicie o nginx se ainda não estiver usando SSL."
