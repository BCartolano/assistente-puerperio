# Conteúdos Educativos (JSON)

**Arquivo:** `backend/static/data/educational.json`

## Formato aceito

- Objeto com campo `"items"` (recomendado) ou lista direta de itens.
- Cada item:
  - **id:** string única (opcional; se faltar, será gerado)
  - **title:** string (obrigatório)
  - **subtitle:** string (opcional)
  - **url:** string http(s) (obrigatório)
  - **read_min:** inteiro 1..60 (opcional; default 3)
  - **icon:** `'ribbon'` | `'bottles'` (opcional; default `'ribbon'`)

## Exemplo

```json
{
  "items": [
    {
      "id": "card-cancer-mama-welcome",
      "title": "Saúde Preventiva",
      "subtitle": "Câncer de Mama",
      "url": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/c/cancer-de-mama",
      "read_min": 4,
      "icon": "ribbon"
    }
  ]
}
```

## Variável de ambiente (opcional)

- **EDU_JSON_PATH:** caminho alternativo para o JSON.

## Validação

```bash
python scripts/validate_educational.py
```

Ou especifique o arquivo:

```bash
python scripts/validate_educational.py backend/static/data/educational.json
```

## Fallback

- Se o JSON estiver ausente ou inválido, a rota `/conteudos` usa dois itens padrão (Câncer de Mama e Doação de Leite).

## Endpoint /api/educational

- **GET /api/educational** retorna:
  ```json
  { "items": [ { "id", "title", "subtitle", "url", "read_min", "icon" }, ... ], "count": N }
  ```
- Headers: **ETag** (baseado no arquivo) e **Cache-Control:** `public, max-age=60`.
- O front (`edu-cards-wire.js`) tenta usar essa API para hidratar os cards que existirem na home.
- Se a API não estiver disponível, cai para o mapeamento fixo dos dois cards.
