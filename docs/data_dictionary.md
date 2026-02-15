# Dicionário de Dados – CNES (Emergência Obstétrica)

**Fonte:** Cadastro Nacional de Estabelecimentos de Saúde (CNES) / DataSUS  
**Versão dos dados:** `config/cnes_codes.json` → `data_version`  
**Snapshot esperado:** `data/raw/<snapshot>/` (ex.: `data/raw/202512/`)

---

## 1. Arquivos consumidos

| Arquivo | Descrição | Campos-chave para maternidade |
|--------|------------|-------------------------------|
| tbEstabelecimento | Cadastro de estabelecimentos | CO_CNES/CO_UNIDADE, NO_FANTASIA, NU_LATITUDE, NU_LONGITUDE, NO_LOGRADOURO, NU_ENDERECO, NU_TELEFONE, CO_TIPO_UNIDADE, TP_GESTAO, CO_NATUREZA_JUR |
| rlEstabLeito | Relação estabelecimento × leitos | CO_UNIDADE, CO_LEITO, QT_EXISTENTE |
| rlEstabServClass | Serviços e classificações | CO_UNIDADE, CO_SERVICO, CO_CLASSIFICACAO |
| (habilitações) | Habilitações por estabelecimento | Confirmar nome do arquivo e colunas no CNES |
| (dicionários) | tbLeito, tbServico, etc. | Códigos oficiais para validação |

---

## 2. Mapeamento de códigos (config/cnes_codes.json)

- **bed_types_obst:** códigos de leito que indicam obstetrícia (ex.: 01, 02, 10, 43).  
  Mapear coluna **CO_LEITO** (ou equivalente) do arquivo de leitos.
- **bed_types_neonatal:** códigos de leito neonatal/UTI Neo (ex.: 10, 41, 46, 65, 92, 93).  
  Mesma coluna **CO_LEITO**.
- **services_obst:** códigos de serviço obstétrico (ex.: 125 Urgência Obstetrícia, 141).  
  Mapear **CO_SERVICO** em rlEstabServClass.
- **classif_obst:** classificação de atendimento de urgência (ex.: 001).  
  Mapear **CO_CLASSIFICACAO** em rlEstabServClass.
- **habilitacoes_obst:** códigos de habilitação obstétrica/neonatal (a preencher com dicionário oficial).  
  Arquivo de habilitações: nome e colunas a confirmar.
- **tipos_estab_maternidade:** tipos de estabelecimento que podem ter maternidade (ex.: 05, 07 Hospital Geral).  
  Mapear **CO_TIPO_UNIDADE** ou **TP_UNIDADE** em tbEstabelecimento.
- **keywords_nome_fantasia:** (ver seção 2.1). Termos para sinal fraco “provável maternidade”.  
  Aplicar em **NO_FANTASIA** (case-insensitive).
- **campos_sus / campos_esfera / natureza_map:** campos e códigos para derivar “atende SUS” e esfera (Público/Privado/Filantrópico).  
  Mapear conforme tabelas de atendimento e natureza jurídica do CNES.

### 2.1. Keywords oficiais para nome fantasia

Termos oficiais para sinal fraco "provável maternidade", aplicados em **NO_FANTASIA** (case-insensitive): **Maternidade**, **Hospital da Mulher**, **Obstétrico**. Não inventar outros; se o dicionário tiver mais, incluir e documentar em `review_needed`.

### 2.2. Campos SUS

Campos que indicam atendimento SUS: **IND_SUS** (indicador, quando existir no arquivo), **ATEND_SUS** (flag/código, quando existir), além de CO_TIPO_ATENDIMENTO, TP_ATENDIMENTO, NU_CNPJ. Mapear nos arquivos do snapshot e preencher `campos_sus` em `config/cnes_codes.json` sem remover chaves já válidas (merge incremental).

---

## 3. Cobertura mínima (critérios de aceite)

- Incluir todos os códigos encontrados nos dicionários oficiais do CNES cujas descrições contenham as raízes: **OBSTET**, **NEONAT**, **PARTO**, **CPN**.
- Não inferir códigos; usar apenas dicionário oficial. Em caso de ambiguidade, documentar em `review_needed` no JSON e neste documento.

---

## 4. Versão e atualização

- **data_version** em `config/cnes_codes.json` deve ser **AAAA-MM** (ex.: 2025-02).
- Atualização: rodar pipeline de ingest com novo snapshot; registrar em `docs/data_versions.md`.

### 4.1. Política de merge incremental

Ao atualizar `config/cnes_codes.json`:

- **Não remover** chaves existentes.
- Apenas **acrescentar** ou **atualizar** valores conforme dicionários oficiais do CNES.
- Não sobrescrever chaves já válidas sem motivo (ex.: nova versão do dicionário).
- Em caso de ambiguidade, documentar em `review_needed` no JSON e neste documento.
