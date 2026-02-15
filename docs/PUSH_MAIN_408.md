# Push falha com HTTP 408 (timeout) – repositório muito grande

## Causa

O histórico do Git contém a pasta **BASE_DE_DADOS_CNES_202512/** com CSVs enormes (centenas de MB cada). O push envia ~650 MB e o servidor (GitHub/etc.) interrompe com 408.

## Solução 1 – Aumentar o buffer (tente primeiro)

No PowerShell, na pasta do projeto:

```powershell
git config http.postBuffer 1048576000
git push origin main
```

(1048576000 = 1 GB. Se ainda der timeout, use a Solução 2.)

---

## Solução 2 – Remover a pasta do histórico (push volta a ser leve)

Isso reescreve o histórico e remove os arquivos grandes de **todos** os commits. Depois é preciso um **force push**.

### Pré-requisito

Instale **git-filter-repo** (recomendado no Windows):

```powershell
pip install git-filter-repo
```

Ou use o [BFG Repo-Cleaner](https://rsc.io/bfg/) (Java).

### Com git-filter-repo

**Atenção:** isso reescreve o histórico. Se mais alguém usa o repositório, avise e combinem o force push.

```powershell
cd C:\Users\bruno\OneDrive\Documentos\chatbot-puerperio

# Remove a pasta gigante de todo o histórico
git filter-repo --path BASE_DE_DADOS_CNES_202512 --invert-paths --force

# Reconecta o remote (filter-repo remove por segurança)
git remote add origin https://github.com/BCartolano/assistente-puerperio.git

# Force push (o histórico da main no remoto será substituído)
git push origin main --force
```

Substitua a URL do `git remote add` pela URL real do seu repositório (a mesma que já estava em `origin` antes do filter-repo).

### Depois do push

O Render fará deploy da `main` normalmente. Os CSVs da CNES não devem ficar no Git; use download em tempo de build ou armazenamento externo (S3, etc.) se o app precisar deles.
