# API de Busca de Facilidades Puerperais

API RESTful construída com **FastAPI** para busca de hospitais, UPAs e UBS com validação rigorosa baseada em dados oficiais do CNES/DataSUS.

## 🎯 Objetivo

Expor dados do banco CNES local via API, aplicando:
- ✅ Filtros geoespaciais (Haversine)
- ✅ Regras de negócio do PM (triagem de emergência, segregação financeira)
- ✅ Mapeamento rigoroso do Analyst (códigos CNES)
- ✅ Formato de card do UX Expert
- ✅ Cache Híbrido do Architect

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install fastapi uvicorn pydantic
```

### 2. Iniciar Servidor

```bash
# Desenvolvimento (auto-reload)
python backend/api/main.py

# Ou via uvicorn
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 5000
```

### 3. Acessar Documentação

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## 📋 Endpoints

### POST `/api/v1/facilities/search`

Busca facilidades de saúde puerperal dentro de um raio especificado.

**Request Body:**
```json
{
  "latitude": -23.5505,
  "longitude": -46.6333,
  "radius_km": 10.0,
  "filter_type": "ALL",
  "is_emergency": false
}
```

**Response:**
```json
{
  "meta": {
    "legal_disclaimer": "⚠️ Aviso de Emergência: ...",
    "total_results": 3,
    "data_source_date": "2025-01-15",
    "is_cache_fallback": false
  },
  "results": [
    {
      "id": "cnes_1234567",
      "name": "Hospital Maternidade Exemplo",
      "type": "HOSPITAL",
      "tags": {
        "sus": true,
        "private": false,
        "maternity": true,
        "emergency_only": false
      },
      "badges": ["ACEITA SUS", "MATERNIDADE"],
      "address": "Rua Exemplo, 123",
      "city": "São Paulo",
      "state": "SP",
      "distance_km": 2.5,
      "google_search_term": "Hospital Maternidade Exemplo Emergency",
      "warning_message": null
    }
  ]
}
```

### GET `/api/v1/facilities/health`

Health check do serviço.

**Response:**
```json
{
  "status": "healthy",
  "service": "facilities_search",
  "database": "connected"
}
```

## 🔍 Filtros Disponíveis

### `filter_type`

- **`ALL`**: Todas as facilidades (padrão)
- **`SUS`**: Apenas unidades que atendem SUS
- **`PRIVATE`**: Apenas unidades privadas
- **`MATERNITY`**: Apenas hospitais com maternidade
- **`EMERGENCY_ONLY`**: Apenas UPAs

### `is_emergency`

Se `true`, **ignora filtros de convênio** e retorna unidades mais próximas (regra de emergência - Lei do Cheque Caução).

**Regra de Negócio (PM):**
> "Antes de mostrar o mapa, o sistema deve perguntar: 'É uma emergência médica (sangramento, desmaio, dor extrema)?'. Se SIM, direcione para a unidade de emergência mais próxima independente de convênio."

## 🏗️ Arquitetura

### Estrutura de Arquivos

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py           # Servidor FastAPI
│   ├── routes.py         # Rotas/endpoints
│   ├── models.py         # Pydantic models
│   └── README.md         # Este arquivo
├── services/
│   ├── facility_service.py  # Lógica de busca
│   └── geo_service.py       # Cálculo Haversine
└── database/
    └── schema.sql           # Schema do banco
```

### Fluxo de Dados

1. **Requisição** → `routes.py` (valida com Pydantic)
2. **Busca** → `facility_service.py` (query no banco CNES)
3. **Filtro Geoespacial** → `geo_service.py` (Haversine)
4. **Formatação** → Aplica regras do PM/Analyst/UX Expert
5. **Resposta** → JSON formatado com aviso legal obrigatório

## 🔒 Segurança

### Tratamento de Erros

- ✅ Banco não encontrado: Erro 503 com mensagem clara
- ✅ Erro de query: Erro 500 com mensagem genérica
- ✅ Handler global: Evita crash do app
- ✅ Logs detalhados: Para debug em desenvolvimento

### Validação

- ✅ Pydantic valida tipos e limites (latitude, longitude, radius)
- ✅ Regras de negócio aplicadas no service layer
- ✅ Dados ambíguos descartados (regra de ouro)

## 📊 Regras de Negócio Implementadas

### PM (Product Manager)

1. **Triagem de Emergência**: `is_emergency=true` ignora filtros de convênio
2. **Segregação Financeira**: Filtros SUS vs PRIVATE separados
3. **Definição Puerperal**: Apenas hospitais com Obstetrícia (Código 065)

### Analyst

1. **Mapeamento CNES**: Tipos 05/07 (Hospital), 73 (UPA), 01/02 (UBS)
2. **Natureza Jurídica**: 1xxx (Público), 3999 (Filantrópico), 2xxx (Privado)
3. **Código de Serviços**: 065 = Obstetrícia

### UX Expert

1. **Aviso Legal**: Sempre incluído no `meta.legal_disclaimer`
2. **Badges**: Gerados automaticamente baseados em tags
3. **Warning Messages**: Avisos para UPAs (não realizam parto)

## 🧪 Testes

### Teste Manual

```bash
# Health check
curl http://localhost:5000/api/v1/facilities/health

# Busca de maternidades SUS
curl -X POST http://localhost:5000/api/v1/facilities/search \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -23.5505,
    "longitude": -46.6333,
    "radius_km": 10,
    "filter_type": "MATERNITY",
    "is_emergency": false
  }'
```

## 🔄 Próximos Passos

1. ✅ API básica criada
2. ⏳ Integração com Google Maps API (buscar coordenadas)
3. ⏳ Cache de resultados (Redis)
4. ⏳ Rate limiting
5. ⏳ Autenticação (se necessário)
6. ⏳ Testes automatizados

## 📚 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)
- [Arquitetura Cache Híbrido](../.bmad-core/agents/architect.md)

---

**Desenvolvido seguindo diretrizes de Health Data Audit**  
**Zero Tolerância para Alucinação de Dados**
