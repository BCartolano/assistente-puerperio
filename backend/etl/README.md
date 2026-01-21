# Módulo ETL - Integração CNES/DATASUS

Este módulo realiza a extração, transformação e carga (ETL) de dados do Cadastro Nacional de Estabelecimentos de Saúde (CNES) para identificar quais hospitais são SUS, Privados ou Mistos.

## Estrutura

- `__init__.py` - Inicialização do módulo
- `setup_cnes.py` - Script principal de setup e importação

## Uso

### 1. Instalar dependências

```bash
pip install pandas sqlalchemy requests
```

### 2. Criar tabela e importar dados

Execute o script `setup_cnes.py`:

```bash
cd backend
python etl/setup_cnes.py
```

O script oferece 3 opções:

1. **Importar dados de um arquivo CSV** - Importa dados completos do CNES de um arquivo CSV
2. **Criar dados de exemplo (seed)** - Cria dados de exemplo com principais hospitais para MVP
3. **Apenas criar a tabela** - Cria apenas a estrutura do banco de dados, sem importar dados

### 3. Estrutura da Tabela

A tabela `hospitais_oficiais` contém:

- `cnes_id` (PK) - ID do CNES
- `nome_fantasia` - Nome fantasia do hospital
- `razao_social` - Razão social
- `municipio` - Município
- `uf` - Unidade Federativa
- `atende_sus` (Boolean) - Se atende pelo SUS
- `natureza` - Público/Privado/Misto
- E outros campos...

### 4. Fonte de Dados

Para importar dados reais do CNES:

1. Acesse o portal de Dados Abertos: https://dados.gov.br/dados/conjuntos-dados/base-de-dados-cnes---estabelecimentos
2. Baixe o arquivo CSV com os estabelecimentos
3. Execute o script escolhendo opção 1 e informe o caminho do arquivo

**Nota:** O arquivo CSV completo do CNES pode ter mais de 2GB. Para desenvolvimento/testes, use a opção de seed ou importe uma amostra limitada.

## Integração com o Localizador

Após importar os dados, o sistema pode enriquecer os resultados da busca de hospitais fazendo uma consulta SQL:

```python
SELECT * FROM hospitais_oficiais 
WHERE nome_fantasia LIKE '%Nome do Hospital%' 
AND municipio = 'Município'
```

Isso permite identificar se o hospital atende SUS, é público/privado, etc.
