#!/usr/bin/env bash
set -euo pipefail
# Executa purga de histórico em um clone espelho usando git filter-repo.
# Requer: pip install git-filter-repo

ROOT="$(pwd)"
PURGE_DIR="${ROOT}/.purge"
PATHS_FILE="${PATHS_FILE:-$PURGE_DIR/paths.txt}"
MIRROR_DIR="${MIRROR_DIR:-$PURGE_DIR/mirror.git}"
REMOTE_NAME="${REMOTE_NAME:-origin}"

if ! git --version >/dev/null 2>&1; then
  echo "[purge:run] git não encontrado"
  exit 1
fi
if ! git filter-repo --help >/dev/null 2>&1; then
  echo "[purge:run] git-filter-repo não encontrado."
  echo "Instale com: pip install --user git-filter-repo"
  exit 1
fi
if [ ! -f "$PATHS_FILE" ]; then
  echo "[purge:run] $PATHS_FILE não existe. Rode 'npm run purge:plan' e edite o paths.txt."
  exit 1
fi

echo "[purge:run] Preparando clone espelho em $MIRROR_DIR ..."
rm -rf "$MIRROR_DIR"
git clone --mirror . "$MIRROR_DIR"
cd "$MIRROR_DIR"

echo "[purge:run] Rodando git filter-repo (removendo caminhos listados)..."
cp "$PATHS_FILE" paths.txt
echo "---- paths.txt ----"
grep -v '^#' paths.txt | grep -v '^$' || true
echo "-------------------"

git filter-repo --force --paths-from-file paths.txt --invert-paths

echo "[purge:run] Limpando refs e GC..."
git reflog expire --expire=now --all 2>/dev/null || true
git gc --prune=now --aggressive

echo
echo "[purge:run] Tamanho do espelho após purga:"
du -sh .
echo
read -r -p "[purge:run] Deseja fazer push --force para '$REMOTE_NAME'? (y/N) " RESP
if [[ "$RESP" == "y" || "$RESP" == "Y" ]]; then
  echo "[purge:run] Enviando branches..."
  git push --force --all "$REMOTE_NAME"
  echo "[purge:run] Enviando tags..."
  git push --force --tags "$REMOTE_NAME"
  echo "[purge:run] Concluído."
else
  echo "[purge:run] Push abortado. O espelho purgado está em $MIRROR_DIR"
fi
