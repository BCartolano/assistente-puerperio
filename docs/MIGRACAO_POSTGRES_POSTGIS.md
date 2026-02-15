# Migração para PostgreSQL + PostGIS

Este documento descreve como migrar o sistema de busca de hospitais para usar **Azure Database for PostgreSQL Flexible Server** com **PostGIS**.

## 🎯 Objetivo

Substituir o sistema atual de busca de hospitais por uma solução robusta usando PostgreSQL + PostGIS, que oferece:
- ✅ Consultas espaciais rápidas (12ms típico)
- ✅ Suporte a todos os 5.570 municípios do Brasil
- ✅ Escalabilidade para milhões de registros
- ✅ Custo acessível (R$ 80-250/mês no Azure)

## 📋 Pré-requisitos

1. **Azure Database for PostgreSQL Flexible Server** criado
2. **PostGIS** habilitado no banco
3. Arquivo CSV do CNES (`tbEstabelecimento202410.csv` ou similar)
4. Variáveis de ambiente configuradas

## 🚀 Passo a Passo

### 1. Criar o Banco de Dados no Azure

1. Acesse o [Portal do Azure](https://portal.azure.com)
2. Crie um novo recurso: **Azure Database for PostgreSQL Flexible Server**
3. Configure:
   - **Nome do servidor**: `sophia-postgres` (exemplo)
   - **Região**: Escolha a mais próxima (ex: Brazil South)
   - **Tier**: Basic (R$ 80/mês) ou General Purpose (R$ 180-250/mês)
   - **PostgreSQL version**: 14 ou superior
   - **Storage**: 32 GB mínimo
4. Habilite **PostGIS** nas configurações de extensões
5. Anote as credenciais de acesso

### 2. Configurar Variáveis de Ambiente

Adicione ao arquivo `.env`:

```bash
# PostgreSQL Configuration
POSTGRES_HOST=sophia-postgres.postgres.database.azure.com
POSTGRES_DB=sophia
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha_segura

# Caminho do arquivo CSV do CNES
CNES_CSV_PATH=BASE_DE_DADOS_CNES_202512/tbEstabelecimento202410.csv
```

### 3. Criar a Tabela

Execute o script SQL no banco de dados:

```bash
# Via psql
psql -h sophia-postgres.postgres.database.azure.com -U seu_usuario -d sophia -f sql/create_table_estabelecimentos.sql

# Ou via Azure Portal > Query Editor
```

O script cria:
- Tabela `estabelecimentos_saude`
- Extensão PostGIS
- Índices espaciais GIST para performance
- Índices adicionais para filtros comuns

### 4. Importar Dados do CNES

Execute o script Python de importação:

```bash
python scripts/import_cnes_postgres.py
```

O script:
- ✅ Lê o arquivo CSV do CNES
- ✅ Filtra estabelecimentos com maternidade
- ✅ Converte coordenadas para formato decimal
- ✅ Insere dados em lotes eficientes
- ✅ Cria geometrias PostGIS automaticamente

**Tempo estimado**: 5-15 minutos para ~600.000 estabelecimentos

### 5. Verificar Instalação

Teste a rota de API:

```bash
curl "http://localhost:5000/api/hospitais-proximos?lat=-23.5505&lon=-46.6333&radius_km=50&limit=10"
```

Deve retornar JSON com hospitais ordenados por distância.

## 📁 Arquivos Criados

1. **`sql/create_table_estabelecimentos.sql`**
   - Script SQL para criar tabela e índices

2. **`scripts/import_cnes_postgres.py`**
   - Script Python para importar dados do CNES

3. **`backend/services/postgres_service.py`**
   - Serviço de conexão com PostgreSQL

4. **`backend/api/routes_hospitais.py`**
   - Rota Flask `/api/hospitais-proximos` usando PostGIS

## 🔌 API Endpoint

### GET `/api/hospitais-proximos`

**Parâmetros:**
- `lat` (float, obrigatório): Latitude (-90 a 90)
- `lon` (float, obrigatório): Longitude (-180 a 180)
- `radius_km` (float, opcional): Raio de busca em km (padrão: 50)
- `limit` (int, opcional): Limite de resultados (padrão: 10, máx: 100)
- `tem_maternidade` (bool, opcional): Filtrar apenas com maternidade (padrão: true)

**Exemplo:**
```bash
GET /api/hospitais-proximos?lat=-23.5505&lon=-46.6333&radius_km=50&limit=10
```

**Resposta:**
```json
{
  "items": [
    {
      "cnes": "1234567",
      "nome_fantasia": "Hospital Maternidade Exemplo",
      "logradouro": "Rua Exemplo, 123",
      "bairro": "Centro",
      "municipio": "São Paulo",
      "uf": "SP",
      "telefone": "(11) 1234-5678",
      "tem_maternidade": true,
      "tem_uti_neonatal": true,
      "aceita_sus": true,
      "distancia_km": 2.5
    }
  ],
  "count": 1,
  "meta": {
    "lat": -23.5505,
    "lon": -46.6333,
    "radius_km": 50,
    "limit": 10,
    "tem_maternidade": true
  }
}
```

## ⚡ Performance

- **Consulta típica**: 12-50ms
- **Suporta**: Milhões de registros
- **Escalabilidade**: Horizontal via read replicas no Azure

## 🔒 Segurança

- Conexões SSL obrigatórias (`sslmode=require`)
- Credenciais via variáveis de ambiente
- Validação de parâmetros de entrada
- Tratamento de erros robusto

## 💰 Custos Azure

- **Basic Tier**: R$ 80/mês (suficiente para começar)
- **General Purpose**: R$ 180-250/mês (recomendado para produção)
- **Storage**: Incluído (32GB+)

## 🐛 Troubleshooting

### Erro: "PostgreSQL não disponível"
- Verifique variáveis de ambiente `POSTGRES_*`
- Teste conexão: `psql -h HOST -U USER -d DB`

### Erro: "Extension postgis does not exist"
- Execute: `CREATE EXTENSION postgis;` no banco

### Importação lenta
- Aumente `chunksize` no script (padrão: 1000)
- Verifique conexão de rede com Azure

### Consultas lentas
- Verifique se índices foram criados: `\d+ estabelecimentos_saude`
- Execute `ANALYZE estabelecimentos_saude;` após importação

## 📚 Referências

- [Azure Database for PostgreSQL](https://azure.microsoft.com/services/postgresql/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [CNES Datasus](http://cnes.datasus.gov.br/)

## ✅ Checklist de Migração

- [ ] Banco PostgreSQL criado no Azure
- [ ] PostGIS habilitado
- [ ] Variáveis de ambiente configuradas
- [ ] Tabela criada (`create_table_estabelecimentos.sql`)
- [ ] Dados importados (`import_cnes_postgres.py`)
- [ ] Rota testada (`/api/hospitais-proximos`)
- [ ] Frontend atualizado (se necessário)
- [ ] Monitoramento configurado

---

**Pronto!** A Sophia agora usa PostgreSQL + PostGIS para buscar hospitais em todo o Brasil. 🎉
