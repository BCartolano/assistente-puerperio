#!/usr/bin/env bash
set -euo pipefail
echo "Limpando caches e pastas de build..."
rm -rf node_modules dist build .cache .parcel-cache .turbo .next .nuxt coverage
echo "OK: limpou caches e pastas de build"
echo
echo "Dica: se usar pnpm, rode 'pnpm store prune' para limpar o store global."
