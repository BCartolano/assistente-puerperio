# Router do Chatbot - Sophia Emergency v2

## Visão Geral

Router web para processar intents do chatbot via HTTP. Suporta Flask e FastAPI (opcional).

## Endpoints

### GET `/api/v1/chat/ping`
Health check do chatbot.

**Resposta:**
```json
{
  "ok": true,
  "version": "sophia-chat-v1",
  "intents": ["atende_sus", "publico_privado", "convenios", ...]
}
```

### GET `/api/v1/chat/intents`
Lista todas as intents disponíveis.

**Resposta:**
```json
{
  "ok": true,
  "intents": ["atende_sus", "publico_privado", "convenios", ...]
}
```

### POST `/api/v1/chat/intent`
Processa uma intent do chatbot.

**Request:**
```json
{
  "intent": "publico_privado",
  "slots": {
    "hospital": "Hospital Municipal",
    "lat": -23.19,
    "lon": -45.79
  }
}
```

**Resposta:**
```json
{
  "ok": true,
  "intent": "publico_privado",
  "text": "O Hospital Municipal é público e aceita Cartão SUS."
}
```

## Uso

### cURL
```bash
curl -s -X POST "http://localhost:5000/api/v1/chat/intent" \
  -H "Content-Type: application/json" \
  -d '{"intent":"publico_privado","slots":{"hospital":"Hospital Municipal","lat":-23.19,"lon":-45.79}}'
```

### JavaScript (Frontend)
```javascript
const r = await fetch('/api/v1/chat/intent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    intent: 'publico_privado', 
    slots: { hospital: nome, lat, lon } 
  })
});
const data = await r.json();
console.log(data.text);
```

### CLI (se disponível)
```bash
python chatbot/cli.py publico_privado '{"hospital":"Hospital Municipal","lat":-23.19,"lon":-45.79}'
```

## Logging

Todos os eventos são logados em **`logs/chat_events.jsonl`** (formato JSONL):

```json
{"ts": 1704201600.0, "intent": "publico_privado", "ok": true, "text": "...", "req": {...}, "ip": "127.0.0.1", "user_id": null}
```

**Campos:**
- `ts`: timestamp Unix
- `intent`: intent processada
- `ok`: sucesso (true/false)
- `text`: resposta gerada
- `req`: payload completo da requisição
- `ip`: IP do cliente (ou X-Forwarded-For)
- `user_id`: ID do usuário (se header X-User-Id presente)

## Rate Limiting (Opcional)

Rate limit simples por IP (configurável via `CHAT_RATE_MAX`):

```bash
CHAT_RATE_MAX=60  # máximo 60 requisições por minuto por IP
```

**Comportamento:**
- Janela: 60 segundos
- Default: 60 req/min (desabilitado se `CHAT_RATE_MAX=0`)
- Resposta: `429 Too Many Requests` se exceder

## Segurança

- **CORS**: Respeita `ALLOW_ORIGINS` do Flask/FastAPI
- **Rate Limit**: Opcional, configurável via `CHAT_RATE_MAX`
- **Logging**: Todos os eventos são logados (inclui IP)

## Estrutura de Arquivos

```
backend/
  chat/
    __init__.py          # Módulo do chatbot
    router.py            # Router Flask
    router_fastapi.py    # Router FastAPI (opcional)
```

## Registro

### Flask (`backend/app.py`)
```python
from backend.chat.router import CHAT_BP
app.register_blueprint(CHAT_BP)
```

### FastAPI (`backend/api/main.py`)
```python
from backend.chat.router_fastapi import router as chat_router
app.include_router(chat_router)
```

## Handlers

O router espera que exista `chatbot/handlers.py` com:

```python
def handle_intent(intent: str, slots: dict) -> str:
    """Processa uma intent e retorna texto de resposta."""
    # ...
    return "Resposta do chatbot"

INTENT_MAP = {
    "publico_privado": handle_publico_privado,
    "atende_sus": handle_atende_sus,
    # ...
}
```

**Se `chatbot/handlers.py` não existir:**
- Router retorna `500` em `/intent`
- `/ping` e `/intents` retornam lista vazia
- Logs mostram aviso de handlers indisponíveis

## Intents Sugeridas

- **`publico_privado`**: "É público ou privado?"
- **`atende_sus`**: "Atende SUS?"
- **`convenios`**: "Quais convênios?"
- **`rotas`**: "Rotas até X?"
- **`tem_maternidade`**: "Tem maternidade?"
- **`emergencia`**: Escalada para "Ligue 192 (SAMU)"

## Troubleshooting

**Erro: "handlers indisponíveis"**
- Verifique se `chatbot/handlers.py` existe e tem `handle_intent` e `INTENT_MAP`

**Erro: "intent desconhecida"**
- Verifique se a intent está em `INTENT_MAP`
- Use `GET /api/v1/chat/intents` para listar intents disponíveis

**Rate limit 429**
- Ajuste `CHAT_RATE_MAX` no `.env` ou desabilite (`CHAT_RATE_MAX=0`)

**Logs não aparecem**
- Verifique permissões da pasta `logs/`
- Verifique se `logs/chat_events.jsonl` está sendo criado
