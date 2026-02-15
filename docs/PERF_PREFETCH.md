# Preconnect / Prefetch

## O que foi adicionado

- **backend/templates/_perf_head_links.html**: links de dns-prefetch e preconnect para:
  - **api.groq.com**
  - a própria origem do app (`request.url_root`)
  - `<meta name="api-base">` com a origem da API (ajuste se usar domínio separado)
- Inclusão do partial no `<head>` de:
  - **templates/index.html**
  - **templates/conteudos.html**

## Observações

- Mantém o 0028 (perf-prefetch.js) para prefetch em idle de `/api/educational`.
- Se o backend/API ficar em outro domínio em produção, altere o conteúdo do partial ou passe a origem via contexto.

## Validação

- Abra DevTools > Network:
  - na aba Timing do primeiro request para `/`, veja “Stalled”/“SSL” menores após o preconnect.
  - confirme que os `<link rel="preconnect"|"dns-prefetch">` estão no head do HTML inicial.
