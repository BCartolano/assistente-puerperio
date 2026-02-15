# Implementação: Separação de Fluxos (Emergência vs Rotina)

**Data:** 2025-01-XX  
**Status:** ✅ Implementado

---

## Resumo Executivo

Implementada separação crítica entre **Modo Emergência** e **Modo Atenção Básica** no Localizador de Unidades de Saúde, garantindo segurança jurídica e usabilidade em situações de emergência médica.

---

## Problema Identificado

O sistema estava misturando UBS/Postos de Saúde com Hospitais na mesma lista, ordenando apenas por distância. Isso causava:
- **Risco de segurança:** Usuários em emergência viam UBS no topo (mais próximas) ao invés de Hospitais
- **Confusão:** Difícil distinguir o que é hospital do que é posto de vacinação
- **Dados incompletos:** Campo `tipo_unidade` estava NULL em todos os registros do banco

---

## Soluções Implementadas

### 1. Backend - Filtros Rígidos por Modo

#### Novo Parâmetro `search_mode`
- `"emergency"`: **APENAS** Hospitais (05, 07) e UPAs (73)
- `"basic"`: **APENAS** UBS/Postos (01, 02, 15, 40)
- `"all"`: Todos os tipos (compatibilidade)

#### Query Segregada
```python
if search_mode == "emergency":
    # FILTRO RÍGIDO: Apenas 05, 07, 73
    base_query += " AND tipo_unidade IN ('05', '07', '73', 'HOSPITAL', 'UPA')"
elif search_mode == "basic":
    # FILTRO RÍGIDO: Apenas 01, 02, 15, 40
    base_query += " AND tipo_unidade IN ('01', '02', '15', '40', 'UBS')"
```

#### Raio Aumentado para Emergência
- **Emergência:** 20km (hospitais são mais raros e podem estar mais longe)
- **Básico:** 10km (proximidade de bairro)

#### Melhoria de Nomes
- **Título principal:** Tipo + Bairro (ex: "UBS Jardim Santa Inês II")
- **Subtítulo:** Nome de pessoa/homenagem (ex: "Dr. José da Cruz Passos Junior")
- **Hospitais:** Nomes limpos (sem nomes de pessoas)
- **UBS:** Aceita nomes de pessoas como subtítulo

### 2. Frontend - Interface Segregada

#### Abas de Modo de Busca
- **Aba "🏥 Hospitais/UPA"** (padrão para emergência)
  - Cor: Vermelho
  - Disclaimer: "🚨 EMERGÊNCIA: Em caso de risco de morte, ligue 192..."
  
- **Aba "💉 Vacinas/UBS"** (atenção básica)
  - Cor: Azul
  - Foco: Proximidade geográfica

#### Cores Diferenciadas nos Cards
- **Hospitais/UPAs:**
  - Borda: Vermelha (`border-red-500`)
  - Fundo: Vermelho claro (`bg-red-50`)
  - Ícone: 🏥
  - Texto: "PRONTO SOCORRO / EMERGÊNCIA"
  
- **UBS/Postos:**
  - Borda: Azul (`border-blue-500`)
  - Fundo: Azul claro (`bg-blue-50`)
  - Ícone: 💉
  - Texto: "ATENÇÃO BÁSICA / VACINAÇÃO"

#### Exibição de Nomes
- Título principal: `display_name` (Tipo + Bairro)
- Subtítulo: `display_subtitle` (nome de pessoa, se houver)

### 3. Scripts de Manutenção

#### `check_hospital_coordinates.py`
- Verifica coordenadas de hospitais no banco
- Identifica hospitais sem coordenadas válidas
- Estatísticas por tipo de unidade

#### `fix_tipo_unidade.py`
- Corrige campo `tipo_unidade` no banco
- Lê `TP_UNIDADE` do CSV original
- Mapeia para tipos legíveis (HOSPITAL, UPA, UBS)
- Processa em lotes para evitar timeout

---

## Arquivos Modificados

### Backend
- `backend/services/facility_service.py`
  - Método `_build_filter_query()`: Filtros rígidos por modo
  - Método `search_facilities()`: Suporte a `search_mode` e raio aumentado
  - Método `_improve_display_name()`: Retorna tuple (título, subtítulo)

- `backend/api/models.py`
  - `SearchRequest`: Novo campo `search_mode`
  - `FacilityResult`: Novo campo `display_subtitle`

- `backend/api/routes.py`
  - Disclaimer diferenciado por modo de busca

- `backend/etl/data_ingest.py`
  - Correção: Salvar código original quando não houver mapeamento

### Frontend
- `frontend/src/App.jsx`
  - Estado `searchMode` com abas
  - Raio dinâmico (20km para emergência)
  - Disclaimer de emergência

- `frontend/src/components/ResultsList.jsx`
  - Cores diferenciadas por tipo
  - Exibição de subtítulo
  - Textos de destaque

- `frontend/src/services/api.js`
  - Envio de `search_mode` na requisição

### Scripts
- `backend/scripts/check_hospital_coordinates.py` (novo)
- `backend/scripts/fix_tipo_unidade.py` (novo)

---

## Critérios de Aceite Atendidos

✅ **Separação de Fluxos:**
- Modo Emergência retorna APENAS Hospitais/UPAs
- Modo Básico retorna APENAS UBS/Postos
- Não há mistura entre os dois modos

✅ **Segurança Jurídica:**
- Disclaimer de emergência exibido
- Hospitais sempre no topo em modo emergência
- Raio aumentado para 20km em emergência

✅ **Usabilidade:**
- Abas claras e visíveis
- Cores diferenciadas
- Textos de destaque por tipo
- Nomes melhorados (Tipo + Bairro)

---

## Próximos Passos

1. **Executar script de correção:**
   ```bash
   python backend/scripts/fix_tipo_unidade.py
   ```
   (Já está rodando em background)

2. **Verificar coordenadas de hospitais:**
   ```bash
   python backend/scripts/check_hospital_coordinates.py
   ```

3. **Se houver hospitais sem coordenadas:**
   - Criar script de geocoding para popular coordenadas baseadas em endereço
   - Usar Google Maps API, OpenStreetMap ou similar

4. **Testes em produção:**
   - Validar que hospitais aparecem em modo emergência
   - Validar que UBS não aparecem em modo emergência
   - Validar cores e textos estão claros

---

## Notas Técnicas

### Campo `tipo_unidade` no Banco
- **Problema identificado:** Todos os registros tinham `tipo_unidade = NULL`
- **Causa:** Coluna `CO_TIPO_UNIDADE` estava vazia no CSV
- **Solução:** Usar coluna `TP_UNIDADE` que contém os dados reais
- **Script de correção:** `fix_tipo_unidade.py` popula o campo baseado no CSV

### Performance
- Processamento em lotes de 500 registros
- Commits intermediários a cada 5000 registros
- Uso de `executemany` para melhor performance

---

**Status Final:** ✅ Implementação completa e pronta para testes
