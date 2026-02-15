# Manter o repositório leve (evitar 4 GB)

## Situação atual

- **Depois do `git filter-repo`:** o histórico não tem mais a pasta `BASE_DE_DADOS_CNES_202512/` (CSVs de centenas de MB). O `.git` fica em torno de **~12 MB**.
- **Pasta do projeto no seu PC:** hoje ~0,8 GB (data 294 MB, node_modules 165 MB, etc.). Se em algum lugar aparecer **4 GB**, pode ser:
  - clone antigo (antes do filter-repo) com `.git` gigante;
  - pasta `BASE_DE_DADOS_CNES_202512` ainda no disco;
  - OneDrive/backup contando versões antigas.

---

## O que NUNCA deve entrar no Git

Já estão no `.gitignore`; não commitar:

- `BASE_DE_DADOS_CNES_*/` – dumps CNES (centenas de MB/GB)
- `data/raw/`, `data/geo/` (exceto o parquet mínimo se combinado)
- `data/cache/*.pkl` – caches
- `node_modules/`, `.venv/`, `venv/`
- `*.db`, `*.sqlite`, `users.db`

Se alguém adicionar algo assim de novo, o push vai falhar no GitHub (limite 100 MB por arquivo).

---

## Se o projeto no seu PC estiver com 4 GB

1. **Apagar pasta CNES (se ainda existir):**
   ```powershell
   Remove-Item -Recurse -Force .\BASE_DE_DADOS_CNES_202512 -ErrorAction SilentlyContinue
   ```

2. **Limpar cache e dados pesados (opcional; você pode gerar de novo depois):**
   ```powershell
   Remove-Item -Recurse -Force .\data\cache -ErrorAction SilentlyContinue
   Remove-Item -Recurse -Force .\data\raw -ErrorAction SilentlyContinue
   ```

3. **Se o `.git` ainda for gigante (clone antigo):** o mais simples é **clonar de novo** a partir do GitHub (histórico já está limpo):
   ```powershell
   cd C:\Users\bruno\OneDrive\Documentos
   Rename-Item chatbot-puerperio chatbot-puerperio-old
   git clone https://github.com/BCartolano/assistente-puerperio.git chatbot-puerperio
   cd chatbot-puerperio
   ```
   Depois copie só o que precisar de `chatbot-puerperio-old` (ex.: `.env`, arquivos locais) e apague `chatbot-puerperio-old`.

4. **Reduzir uso em desenvolvimento:** você pode apagar `node_modules` e `data/cache` quando não estiver desenvolvendo e recriar quando for trabalhar (`npm install`, rodar scripts que geram cache de novo).

---

## Resumo

| Onde | Tamanho esperado |
|------|-------------------|
| `.git` (após filter-repo) | ~12 MB |
| Clone novo do GitHub | dezenas a ~100 MB (só código e assets) |
| Projeto no PC (com data + node_modules) | ~0,5–1 GB |
| **Nunca** | 4 GB no Git ou em um único clone enxuto |

Se em algum lugar ainda aparecer 4 GB, é clone antigo ou pastas de dados/cache no disco – use os passos acima para limpar ou clonar de novo.
