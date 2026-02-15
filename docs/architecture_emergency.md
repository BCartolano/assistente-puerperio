# Arquitetura – Pipeline de Emergência Obstétrica (CNES)

**Objetivo:** visão geral do fluxo ETL → Classificador → Geocoding → API → UI, incluindo modo offline para geocodificação (cache).

---

## 1. Visão geral

```
[CSVs CNES] → ETL (ingest) → Normalização/Validação
                    ↓
              Classificador (config/cnes_codes.json + config/scoring.yaml)
                    ↓
              has_maternity, score, evidence
                    ↓
              Geocoding (lat/long do CNES ou geocoder + cache local)
                    ↓
              API (GET /v1/emergency/search, GET /v1/establishments/{cnes_id})
                    ↓
              UI (cards, botão Ligar, Rotas, filtro SUS)
```

- **ETL:** carrega CSVs do CNES (`data/raw/<snapshot>/` ou caminhos configuráveis), normaliza colunas, valida tipos, grava em DB ou Parquet.
- **Classificador:** aplica regras e pesos de `config/scoring.yaml` e códigos de `config/cnes_codes.json`; gera `has_maternity`, `score`, `evidence` (tipo, código, fonte) por estabelecimento.
- **Geocoding:** usa lat/long do CNES quando houver; senão, geocoder configurável (Nominatim/Google/Mapbox) com **cache local** (`data/geocache.sqlite` ou equivalente) para modo offline.
- **API:** expõe busca de emergência e detalhe por estabelecimento; contratos em `api/contracts/*.json`.
- **UI:** fluxo emergência (botão → consentimento GPS → sintomas graves? → 192 → lista top 3), cards com nome, esfera, atende_sus, “Ala de Maternidade”, telefone, endereço, lat/long, tempo estimado, link rotas.

---

## 2. Definições fixas (classificador)

- **has_maternity = true** se houver **pelo menos 1 sinal forte**: leito obstétrico/neonatal OU serviço/classificação obstétrica OU habilitação obstétrica/neonatal OU tipo “maternidade”.
- **“Provável”** se score entre 0,4 e 0,59 **e** keyword em nome fantasia.
- **Campos essenciais no card:** nome, esfera (Público/Privado/Filantrópico), atende_sus (Sim/Não/Desc.), “Ala de Maternidade: Sim/Provável/Não listado”, telefone, endereço, lat/long, tempo estimado, link de rotas.

---

## 3. Modo offline (geocodificação)

- **Prioridade:** coordenadas do próprio CNES (tbEstabelecimento).
- **Fallback:** geocoder externo (interface `geocoder.py` com adaptadores Nominatim/Google/Mapbox).
- **Cache:** armazenamento local (ex.: `data/geocache.sqlite` ou tabela `geocodes` em `db/schema.sql`) para não depender de rede em execuções subsequentes.
- **Normalização:** endereço normalizado antes de gravar no cache.

---

## 4. Esquema de dados e artefatos

| Artefato | Descrição |
|----------|-----------|
| `db/schema.sql` | Tabelas: establishments, beds, services, habilitations, geocodes, classifications, maternity_classification; views: v_establishments_core, v_maternity_status. Índices em cnes_id e geospatial. |
| `config/cnes_codes.json` | Arrays de códigos (leitos, serviços, classificações, habilitações, tipos estab., keywords, SUS, esfera, natureza_map). |
| `config/scoring.yaml` | Pesos e regras para has_maternity / provável. |
| `api/contracts/*.json` | JSON Schemas: GET /v1/emergency/search, GET /v1/establishments/{cnes_id}, healthcheck/version. |

---

## 5. Relação com arquitetura existente

- Este pipeline **complementa** a arquitetura em `docs/architecture.md` (chatbot, WhatsApp, agendamento).
- O backend atual (Flask + FastAPI) já expõe busca de facilidades (`/api/v1/facilities/search`); os contratos e o schema de emergência padronizam **GET /v1/emergency/search** e **GET /v1/establishments/{cnes_id}** para alinhamento com o produto “top 3 maternidades em emergência”.
- Dados podem ser consumidos pelo `FacilityService` e pelo frontend (React) que já utiliza cards e geolocalização.

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** Architect Agent (BMAD)
