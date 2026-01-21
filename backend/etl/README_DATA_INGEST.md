# Data Ingest - Infraestrutura de Cache Híbrido CNES

Este módulo implementa a **infraestrutura de dados** para o sistema de Cache Híbrido, conforme arquitetura definida pelo Agente Architect.

## 📋 Objetivo

Transformar arquivos CSV do governo (CNES/DataSUS) em uma tabela SQL consultável que serve como **Source of Truth local**, permitindo:

1. **Busca rápida**: Consultas SQL indexadas em milissegundos
2. **Resiliência**: Fallback quando API do DataSUS está offline
3. **Filtragem na entrada**: Remove consultórios, óticas, laboratórios (apenas hospitais, UPAs, UBS)
4. **Classificação puerperal rigorosa**: Identifica corretamente maternidades e UPAs

## 🏗️ Estrutura

```
backend/
├── database/
│   └── schema.sql              # Schema PostgreSQL/SQLite
├── etl/
│   ├── data_ingest.py          # Script principal de ingestão
│   ├── test_data_ingest.py     # Testes unitários
│   └── README_DATA_INGEST.md   # Este arquivo
└── data/
    └── cnes_base_dados.csv     # CSV do CNES (baixar do site do governo)
```

## 🚀 Uso

### 1. Preparação

#### Baixar dados do CNES

1. Acesse: https://dados.gov.br/dados/conjuntos-dados/base-de-dados-cnes---estabelecimentos
2. Baixe o arquivo CSV completo ou por estado/município
3. Salve como `backend/data/cnes_base_dados.csv`

**Nota:** O CSV completo pode ter >2GB. Para desenvolvimento, use uma amostra limitada.

### 2. Criar Schema

Execute o SQL:

```bash
# Para PostgreSQL/Supabase
psql -U usuario -d database -f backend/database/schema.sql

# Para SQLite (cria automaticamente)
python backend/etl/data_ingest.py
```

### 3. Executar Ingestão

```bash
cd backend
python etl/data_ingest.py
```

O script:
- ✅ Cria a tabela automaticamente (se não existir)
- ✅ Filtra apenas unidades relevantes (Hospitais, UPAs, UBS)
- ✅ Classifica rigorosamente (maternidade vs emergência)
- ✅ Higieniza nomes (Title Case)
- ✅ Descarta dados ambíguos (regra de ouro)

### 4. Executar Testes

```bash
python backend/etl/test_data_ingest.py
```

**Teste Crítico:** Verifica se UPA nunca é marcada como maternidade (deve passar).

## 📊 Schema da Tabela

### Tabela: `hospitals_cache`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `cnes_id` | VARCHAR(20) PK | ID único CNES |
| `name` | VARCHAR(255) | Nome oficial |
| `fantasy_name` | VARCHAR(255) | Nome fantasia |
| `city`, `state` | VARCHAR | Localização |
| `lat`, `long` | DECIMAL | Coordenadas (pode ser NULL - será preenchido via Google Maps) |
| `has_maternity` | BOOLEAN | **CRÍTICO:** TRUE se tem Obstetrícia (Código 065) |
| `is_emergency_only` | BOOLEAN | TRUE se é UPA (Tipo 73) |
| `is_sus` | BOOLEAN | TRUE se vinculado ao SUS |
| `management` | ENUM | MUNICIPAL, ESTADUAL, FEDERAL, PRIVADO, DUPLA |
| `tipo_unidade` | VARCHAR | Código CNES (05, 07, 73, etc.) |
| `codigo_servicos` | TEXT | Códigos de serviços (ex: '065,066,067') |
| `data_source_date` | DATE | Data da base oficial (para aviso de desatualização) |

## 🔍 Lógica de Filtragem

### Tipos Permitidos

- **05**: Hospital Geral
- **07**: Hospital Especializado
- **73**: Pronto Atendimento (UPA)
- **01**: Posto de Saúde
- **02**: Centro de Saúde/UBS

**Descarta:** Consultórios, óticas, laboratórios, farmácias, etc.

### Classificação Puerperal

```python
# REGRA 1: UPA nunca é maternidade
if tipo_unidade == '73':
    has_maternity = False
    is_emergency_only = True

# REGRA 2: Verificar código de Obstetrícia (065)
elif '065' in codigo_servicos:
    has_maternity = True
    is_emergency_only = False

# REGRA 3: Dados ambíguos = False
else:
    has_maternity = False
```

## ⚠️ Regras Críticas

### 1. Regra de Ouro: Dados Ambíguos = Descarte

Se `codigo_servicos` estiver vazio ou ambíguo:
- ❌ **NÃO** inferir especialidade pelo nome
- ❌ **NÃO** assumir que "Hospital Maternidade" tem maternidade
- ✅ **SOMENTE** confiar no código oficial '065'

### 2. UPA Nunca é Maternidade

Mesmo se uma UPA tiver o código '065' na lista de serviços:
- `has_maternity` = **FALSE**
- `is_emergency_only` = **TRUE**

UPA apenas estabiliza e transfere. Não realiza parto.

### 3. Higienização Rigorosa

- Nomes convertidos para Title Case
- Espaços extras removidos
- Caracteres especiais preservados

## 📈 Performance

### Índices Criados

```sql
-- Busca por localização (proximidade)
idx_hospitals_cache_location ON (lat, long)

-- Busca por maternidade (filtro comum)
idx_hospitals_cache_maternity ON (has_maternity) WHERE has_maternity = TRUE

-- Busca por SUS
idx_hospitals_cache_sus ON (is_sus) WHERE is_sus = TRUE

-- Busca por cidade/estado
idx_hospitals_cache_city_state ON (city, state)
```

### Consultas Otimizadas

```sql
-- Buscar maternidades SUS em uma cidade
SELECT * FROM hospitals_cache
WHERE has_maternity = 1
  AND is_sus = 1
  AND city = 'São Paulo'
  AND state = 'SP';

-- Buscar hospitais próximos (raio de 5km)
SELECT *, 
       (6371 * acos(cos(radians(?)) * cos(radians(lat)) * 
        cos(radians(long) - radians(?)) + 
        sin(radians(?)) * sin(radians(lat)))) AS distance
FROM hospitals_cache
WHERE lat IS NOT NULL
  AND long IS NOT NULL
HAVING distance < 5
ORDER BY distance;
```

## 🔄 Integração com Cache Híbrido

Esta tabela é o componente local do **Cache Híbrido**:

1. **Atualização Mensal**: Baixar CSV do CNES mensalmente e re-executar ingestão
2. **API Online**: Verificar atualizações recentes via API do CNES (se disponível)
3. **Fallback**: Se API cair, usar dados locais com aviso: *"Dados baseados no registro oficial de [Mês/Ano]. Confirme por telefone."*

## 🧪 Testes

Execute os testes para validar lógica crítica:

```bash
python backend/etl/test_data_ingest.py
```

**Testes incluídos:**
- ✅ UPA nunca é maternidade
- ✅ Dados ambíguos resultam em False
- ✅ Detecção correta de Obstetrícia
- ✅ Higienização de nomes
- ✅ Normalização de gestão

## 📝 Próximos Passos

1. ✅ **Schema criado** - Pronto
2. ✅ **Script de ingestão** - Pronto
3. ✅ **Testes unitários** - Pronto
4. ⏳ **Integração com Google Maps** - Buscar coordenadas lat/long
5. ⏳ **API de busca** - Expor endpoints para consulta
6. ⏳ **Sincronização mensal** - Script automatizado

## 🔗 Referências

- [Portal de Dados Abertos - CNES](https://dados.gov.br/dados/conjuntos-dados/base-de-dados-cnes---estabelecimentos)
- [Documentação CNES](https://cnes.datasus.gov.br/)
- [Arquitetura Cache Híbrido](.bmad-core/agents/architect.md)

---

**Desenvolvido seguindo diretrizes de Health Data Audit**  
**Zero Tolerância para Alucinação de Dados**
