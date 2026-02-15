# Purga de histórico (reduzir o tamanho do repositório)

## Aviso importante

- Isto **REESCREVE** o histórico Git. Congele merges, avise o time, e faça push forçado. Após a purga, todos devem re-clonar ou `git reset --hard origin/main`.

## Pré-requisitos

- git >= 2.30
- **git-filter-repo:** `pip install --user git-filter-repo` (macOS/Linux/Windows com Python 3)

## O que este repo já tem

- `npm run docs:triage` — lista/move docs soltos para `docs/archive/`
- `npm run purge:plan` — gera `.purge/candidates.txt`, `.purge/large-blobs.txt` e template `.purge/paths.txt`
- `npm run purge:blobs` — top blobs por tamanho no histórico
- `npm run purge:run` — executa a purga num clone espelho `.purge/mirror.git` e pergunta antes do push

## Passo a passo (sugerido)

1. Congele a branch principal e avise o time.
2. Organize o workspace: `npm run docs:triage` e `npm run docs:archive`. Commit normal.
3. Planeje: `npm run purge:plan`. Revise `.purge/candidates.txt` e `.purge/large-blobs.txt`. Edite `.purge/paths.txt` com **apenas** o que deseja REMOVER do histórico (pastas com barra final, ex.: `ai-sandbox/`, `ideas/`).
4. Rode a purga: `npm run purge:run`. O script cria o espelho, roda filter-repo e pergunta se quer push forçado para origin.
5. Após o push: time re-clona ou `git fetch origin && git reset --hard origin/main && git gc --prune=now --aggressive`.
6. Limpe caches: `bash scripts/clean-workspace.sh`; se usar pnpm: `pnpm store prune`.

## O que colocar em .purge/paths.txt

- Pastas de rascunho/IA/sandbox: `ai-sandbox/`, `ideas/`, `notes/`, `drafts/`, `tmp/`
- Diretórios `old/`, `backup/`, `deprecated/`, `disabled/` que não devem ficar no histórico
- Binários desnecessários (PSD/AI, zips, vídeos) — idealmente fora do repo ou em LFS

## Alternativa com BFG

- Download: https://rtyley.github.io/bfg-repo-cleaner/
- Exemplo removendo arquivos >10MB: `java -jar bfg.jar --strip-blobs-bigger-than 10M` (depois `git gc --aggressive` e push forçado). **Atenção:** afeta o HEAD atual; arquivos acima do limite ficam vazios.

## Proteções já no repositório

- Pre-commit bloqueia: docs fora de `docs/` e imagens >1MB (guard-docs); arquivos >10MB (guard-large-files).
