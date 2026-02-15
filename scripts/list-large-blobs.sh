#!/usr/bin/env bash
set -euo pipefail
# Lista os maiores blobs do histórico com tamanho aproximado e caminho.
# Requer git 2.11+ (--batch-all-objects).
TOP="${TOP:-200}"
tmp_all="$(mktemp)"
trap 'rm -f "$tmp_all"' EXIT

git rev-list --objects --all > "$tmp_all"
git cat-file --batch-all-objects --batch-check='%(objecttype) %(objectsize) %(objectname)' 2>/dev/null | \
  awk '$1=="blob"{print $2" "$3}' | sort -n | tail -n "$TOP" | while read -r size sha; do
  path="$(grep "^$sha " "$tmp_all" | head -n1 | cut -d' ' -f2-)"
  kb=$((size/1024))
  echo "${kb} KB  ${path}"
done | sort -nr

echo
echo "(Sugestão: adicione diretórios/arquivos suspeitos em .purge/paths.txt e rode npm run purge:run)"
