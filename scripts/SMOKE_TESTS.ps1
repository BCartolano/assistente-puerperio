param(
  [string]$Base = "http://127.0.0.1:5000"
)

function Write-Cyan($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-Green($msg) { Write-Host $msg -ForegroundColor Green }
function Fail($msg) { Write-Host "FAIL: $msg" -ForegroundColor Red; exit 1 }

Write-Cyan "Base: $Base"

function Test-Http200([string]$Url) {
  try {
    $resp = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -ErrorAction Stop
    if ($resp.StatusCode -ne 200) { Fail "$Url -> HTTP $($resp.StatusCode)" }
    Write-Green "OK 200: $Url"
  } catch {
    Fail "$Url -> erro $($_.Exception.Message)"
  }
}

function Test-Json([string]$Url) {
  try {
    $resp = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -Headers @{ "Accept" = "application/json" } -ErrorAction Stop
    $ct = $resp.Headers["Content-Type"]
    if (-not $ct -or ($ct -notmatch "application/json")) { Fail "Content-Type JSON ausente em $Url" }
    Write-Green "OK JSON: $Url"
  } catch {
    Fail "$Url -> erro $($_.Exception.Message)"
  }
}

function Test-Header([string]$Url, [string]$Name) {
  try {
    $resp = Invoke-WebRequest -Uri $Url -Method Head -UseBasicParsing -ErrorAction Stop
    if (-not $resp.Headers[$Name]) { Fail "Header $Name ausente em $Url" }
    Write-Green "OK header $Name: $Url"
  } catch {
    Fail "$Url -> erro $($_.Exception.Message)"
  }
}

# /
Test-Http200 "$Base/"
# /conteudos
Test-Http200 "$Base/conteudos"
# /api/educational
Test-Http200 "$Base/api/educational"
Test-Json "$Base/api/educational"
Test-Header "$Base/api/educational" "ETag"
Test-Header "$Base/api/educational" "Cache-Control"
# /api/nearby
$near = "$Base/api/nearby?lat=-23.55&lon=-46.63&radius_km=10&limit=5"
Test-Http200 $near
Test-Json $near

try {
  $json = Invoke-RestMethod -Uri "$Base/api/educational" -Method GET -ErrorAction Stop
  if ($null -ne $json.count) { Write-Cyan "Educational count: $($json.count)" }
} catch { }

Write-Green "Smoke tests concluídos com sucesso."
exit 0
