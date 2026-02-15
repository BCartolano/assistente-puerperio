# Lighthouse CI

Workflow: **.github/workflows/lighthouse.yml**

## O que faz

- Sobe o app Flask localmente (gunicorn 127.0.0.1:5000).
- Roda Lighthouse nas URLs:
  - /
  - /conteudos
- Publica artefatos (HTML/JSON) no job do GitHub.

## Como ver os relatórios

- Actions > CI - Lighthouse > último run > Artifacts.
- TemporaryPublicStorage: links temporários também aparecem no log do job.

## Notas

- Se sua app precisar de variáveis adicionais para subir em CI, adicione no passo "Start Flask app".
- Para auditar mais páginas, edite a lista de urls no job.
