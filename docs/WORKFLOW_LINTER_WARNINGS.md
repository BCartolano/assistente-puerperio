# Avisos "Context access might be invalid" nos workflows Azure

## O que acontece

A extensão **GitHub Actions** (VS Code/Cursor) valida os arquivos em `.github/workflows/`. Ela só reconhece contextos e secrets **built-in** (por exemplo `GITHUB_TOKEN`). Qualquer uso de **secrets** ou **variables** customizados do repositório (como `AZURE_WEBAPP_NAME`, `AZURE_CLIENT_ID`, `DEPLOY_SLOT`, `SWAP_AFTER_STAGING`) gera o aviso:

**"Context access might be invalid: NOME_DA_CHAVE"**

Isso é um **falso positivo**: os workflows estão corretos; o aviso existe só porque a extensão não sabe que esses secrets/variables existem no seu repositório.

## Opções

### 1. Ignorar os avisos (recomendado)

Os workflows funcionam normalmente no GitHub. Você pode ignorar esses itens no painel Problems.

### 2. Reduzir avisos associando workflows a YAML puro

Se quiser que o editor trate os workflows só como YAML (e use o schema do GitHub), crie ou edite **`.vscode/settings.json`** na raiz do projeto e adicione:

```json
{
  "files.associations": {
    ".github/workflows/*.yml": "yaml"
  },
  "yaml.schemas": {
    "https://json.schemastore.org/github-workflow.json": ".github/workflows/*.yml"
  }
}
```

Assim, a validação da extensão GitHub Actions pode deixar de ser aplicada nesses arquivos e os avisos de "Context access might be invalid" tendem a sumir. Você continua com highlight e schema do workflow.

### 3. Desativar a extensão GitHub Actions para este workspace

Em Extensions, localize "GitHub Actions" e use "Disable (Workspace)". Os avisos somem, mas você perde recursos específicos da extensão (completion, etc.) nesses arquivos.

## Referência

- [Issue #113 – Context access might be invalid (vscode-github-actions)](https://github.com/github/vscode-github-actions/issues/113)
- Os workflows já têm na primeira linha: `# yaml-language-server: $schema=...` para o schema correto.
