# Sistema de Emergência Obstétrica - Guia Completo

Este documento descreve o sistema completo de busca de hospitais para emergências obstétricas, otimizado para situações críticas.

## 🎯 Objetivo

Fornecer à gestante em emergência:
- ✅ Hospitais mais próximos ordenados por **tempo de trânsito real** (não distância linear)
- ✅ Botão de ligação destacado para contato imediato
- ✅ Informações essenciais (telefone, endereço, formas de pagamento)
- ✅ Links diretos para GPS com rota calculada

## 🏗️ Arquitetura

### Fluxo de Busca (100% Gratuito)

```
1. Usuária solicita hospitais próximos (lat/lon)
   ↓
2. BallTree/PostGIS encontra hospitais em raio de 50km (Custo: R$ 0)
   ↓
3. OSRM ordena top 10 por tempo de viagem real (Custo: R$ 0)
   ↓
4. Cache de 5 minutos (economiza requisições)
   ↓
5. Retorna cards formatados para emergência
```

### Componentes

1. **BallTree/PostGIS**: Busca espacial inicial (encontra candidatos) - **Gratuito**
2. **OSRM (OpenStreetMap)**: Ordenação por tempo real (refina resultados) - **Gratuito**
3. **Cache**: Evita chamadas repetidas em 5 minutos
4. **Filtro de Telefone**: Remove hospitais sem contato (risco crítico)
5. **Links GPS**: Google Maps Web e Waze (gratuitos para usuário)

## 🔧 Configuração

### 1. Variáveis de Ambiente

Adicione ao `.env` (apenas se usar PostgreSQL):

```bash
# PostgreSQL (opcional - se usar PostGIS)
POSTGRES_HOST=seu-server.postgres.database.azure.com
POSTGRES_DB=sophia
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha

# OSRM (opcional - padrão usa servidor público)
# Para produção, recomenda-se instalar via Docker
OSRM_BASE_URL=http://router.project-osrm.org
```

### 2. OSRM - Open Source Routing Machine

**Padrão:** Usa servidor público gratuito (`router.project-osrm.org`)

**Para Produção (Recomendado):**
1. Instale OSRM via Docker:
   ```bash
   docker run -t -v $(pwd):/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/brazil-latest.osm.pbf
   docker run -t -v $(pwd):/data osrm/osrm-backend osrm-contract /data/brazil-latest.osrm
   docker run -t -i -p 5000:5000 -v $(pwd):/data osrm/osrm-backend osrm-routed --algorithm mld /data/brazil-latest.osrm
   ```
2. Configure `OSRM_BASE_URL=http://localhost:5000` no `.env`

**Custo:** R$ 0,00 (100% gratuito)

## 📡 API Endpoint

### GET `/api/hospitais-proximos`

**Parâmetros:**
- `lat` (float, obrigatório): Latitude
- `lon` (float, obrigatório): Longitude
- `radius_km` (float, opcional): Raio em km (padrão: 50)
- `limit` (int, opcional): Limite de resultados (padrão: 10)
- `ordenar_por_tempo` (bool, opcional): Ordenar por tempo real (padrão: true)
- `categoria` (str, opcional): 'Público' ou 'Privado'
- `apenas_com_telefone` (bool, opcional): Filtrar apenas com telefone (padrão: false)

**Exemplo:**
```bash
GET /api/hospitais-proximos?lat=-23.5505&lon=-46.6333&radius_km=50&limit=5&ordenar_por_tempo=true
```

**Resposta:**
```json
{
  "items": [
    {
      "cnes": "1234567",
      "nome": "Maternidade Santa Fé",
      "endereco_exato": "Rua Exemplo, 123 - Centro, SP",
      "telefone": "(11) 98888-7777",
      "telefone_limpo": "11988887777",
      "natureza": "Público",
      "sus": "Aceita Cartão SUS",
      "metodos_pagamento": "Aceita Cartão SUS / Aceita Convênios",
      "tem_maternidade": true,
      "tem_uti_neonatal": true,
      "estimativa": "12 min (com trânsito)",
      "distancia": "4.5 km",
      "distancia_rua": "4.5 km",
      "tempo_estimado": "12 minutos",
      "segundos_total": 720,
      "link_gps": "https://www.google.com/maps/dir/?api=1&destination=-23.5505,-46.6333&travelmode=driving",
      "link_waze": "https://waze.com/ul?ll=-23.5505,-46.6333&navigate=yes",
      "link_ligar": "tel:11988887777",
      "latitude": -23.5505,
      "longitude": -46.6333
    }
  ],
  "count": 1,
  "meta": {
    "lat": -23.5505,
    "lon": -46.6333,
    "radius_km": 50,
    "limit": 5,
    "ordenado_por_tempo": true
  }
}
```

## 🎨 Frontend - Cards de Emergência

### HTML

```html
<div id="hospitais-emergencia-container">
    <!-- Cards serão inseridos aqui via JavaScript -->
</div>
```

### JavaScript

```javascript
// Busca hospitais próximos
async function buscarHospitaisEmergencia(lat, lon) {
    try {
        const response = await fetch(
            `/api/hospitais-proximos?lat=${lat}&lon=${lon}&radius_km=50&limit=5&ordenar_por_tempo=true&apenas_com_telefone=true`
        );
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            const container = document.getElementById('hospitais-emergencia-container');
            HospitalCardsEmergency.renderizar(data.items, container);
        }
    } catch (error) {
        console.error('Erro ao buscar hospitais:', error);
    }
}
```

### CSS

Os estilos estão em `backend/static/css/hospital-cards-emergency.css`:
- Botão "LIGAR AGORA" em vermelho destacado
- Cards responsivos para mobile
- Badges de natureza (Público/Privado)
- Informações de tempo e distância

## ⚡ Otimizações Implementadas

### 1. Cache de 5 Minutos

```python
# Cache automático em memória
# Se mesma usuária atualizar em < 5 min, usa cache
# Economiza custos de API Google Maps
```

### 2. Filtro de Telefone

```python
# Script de processamento remove hospitais sem telefone
# Em emergências, linha morta é risco crítico
# Apenas hospitais com contato válido são retornados
```

### 3. Ordenação Inteligente (100% Gratuita)

- **Primeiro**: Busca por proximidade (BallTree/PostGIS) - rápido e gratuito
- **Depois**: Ordena top 10 por tempo real (OSRM) - preciso e gratuito
- **Resultado**: Hospitais ordenados por tempo de chegada, não distância

### 4. Limite de API Calls

- Processa apenas top 10 hospitais com Google Maps
- Resto ordena por distância linear
- Reduz custos e melhora performance

## 🚨 Botão de Pânico

O botão "LIGAR AGORA" é:
- **Vermelho** e **destacado** (maior que botão de rota)
- **Sempre visível** no topo do card
- **Desabilitado** se hospital não tiver telefone
- **Link direto** `tel:` para acionamento imediato

## 📊 Estrutura do Card

Cada card contém:

1. **Header**:
   - Nome do hospital
   - Badges (Público/Privado, UTI Neonatal)

2. **Body**:
   - Endereço completo
   - Telefone
   - Formas de pagamento (SUS/Convênio/Particular)
   - Tempo estimado (com trânsito)
   - Distância

3. **Actions**:
   - Botão "LIGAR AGORA" (vermelho, destacado)
   - Botão "Google Maps" (link para rota)
   - Botão "Waze" (link alternativo para rota)

## 🔒 Segurança e Validação

- ✅ Validação de coordenadas (-90 a 90, -180 a 180)
- ✅ Limite de raio (0 a 500 km)
- ✅ Limite de resultados (1 a 100)
- ✅ Tratamento de erros robusto
- ✅ Fallback se Google Maps não disponível

## 💰 Custos

### Sistema de Roteamento
- **OSRM (OpenStreetMap)**: R$ 0,00 (100% gratuito)
- **Servidor público**: Sem custos, rate limit moderado
- **Instalação própria (Docker)**: R$ 0,00 (recomendado para produção)

### PostgreSQL (Opcional)
- **Basic Tier**: R$ 80/mês
- **General Purpose**: R$ 180-250/mês
- **Sem PostgreSQL**: Usa BallTree (gratuito, em memória)

### Total Estimado
- **Custo mensal**: R$ 0,00 (roteamento) + R$ 0-250 (banco opcional)
- **Para 1000 usuárias/mês**: R$ 0,00 em APIs externas

## 🐛 Troubleshooting

### Erro: "OSRM não disponível"
- Verifique conectividade com internet
- Servidor público pode estar temporariamente indisponível
- Para produção, instale OSRM próprio via Docker
- Fallback automático: ordena por distância linear

### Ordenação não funciona
- Verifica se `ordenar_por_tempo=true` na query
- Se OSRM não disponível, ordena por distância linear (fallback)
- Cache pode estar retornando dados antigos (aguarde 5 minutos)

### Cache não funciona
- Cache é em memória (reinicia com servidor)
- Para cache persistente, considere Redis

## ✅ Checklist de Implementação

- [ ] Instalar dependências: `pip install requests` (já incluído no Flask)
- [ ] Processar dados CNES: `python scripts/process_cnes_optimized.py`
- [ ] Testar API: `GET /api/hospitais-proximos?lat=-23.5505&lon=-46.6333`
- [ ] Integrar cards no frontend
- [ ] Testar botão "LIGAR AGORA"
- [ ] Testar links de GPS (Google Maps e Waze)
- [ ] Validar cache de 5 minutos
- [ ] (Opcional) Instalar OSRM próprio via Docker para produção

---

**Sistema pronto para emergências obstétricas!** 🚨💕
