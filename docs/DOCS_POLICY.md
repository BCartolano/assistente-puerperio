# Política de documentação (curta e grossa)

- **Fonte única de verdade:** toda documentação vai em `docs/`.
- Nada de guias/como-usar/instalação soltos pelo repo. Fora de `docs/` o pre-commit barra.
- Arquivos antigos/desabilitados vão para `docs/archive/` (mantém histórico sem poluir).
- Imagens em `docs/assets/` preferencialmente WebP/AVIF. Evitar PDFs/PSDs grandes.
- Tamanho: arquivos de docs com mais de 1 MB devem ser evitados (o guard alerta).

## Estrutura sugerida

- `docs/INDEX.md` — índice curado (atualize sempre que criar/arquivar algo).
- `docs/ADR/` — Architecture Decision Records resumidos (opcional).
- `docs/Guides/` — guias de uso reais (não rascunhos).
- `docs/assets/` — imagens comprimidas.
- `docs/archive/` — docs obsoletos (só o que precisa ficar por histórico).

## Processo

1. Criou um doc? Linke em `docs/INDEX.md`.
2. Ficou obsoleto? Mova para `docs/archive/` com `git mv`.
3. Rascunho da IA? Salve em `ai-sandbox/` (está no .gitignore) ou fora do repo.
4. Periodicamente, rode `npm run docs:triage` e limpe o que sobrou.

Obs.: para "apagar de verdade" do histórico (repo muito grande), usar git filter-repo conforme `RESGATE_LOGIN_E_BLINDAGEM.md` e `HISTORY_PURGE.md`.
