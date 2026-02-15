# Arquitetura do Pipeline de Dados – Emergência Obstétrica

**Autor:** Architect  
**Base:** Requisitos lógicos em `REQUISITOS_LOGICOS_LOCALIZACAO_EMERGENCIA_OBSTETRICA.md`  
**Objetivo:** Esquema do pipeline (JOIN, GeoJSON, Score de Confiança, arquivo intermediário) para consumo pelo front-end.

---

## 1. Fontes de Dados (CNES – brutos)

| Arquivo / Tabela            | Conteúdo principal                                      |
|----------------------------|---------------------------------------------------------|
| `tb_estabelecimento`       | Cadastro (CO_CNES, nome, endereço, **Lat/Long**, tipo)  |
| `rl_estab_leito`           | Quantidade de leitos por especialidade (CO_CNES, cod_leito, qt_existente) |
| `rl_estab_serv_class`      | Serviços especializados e classificações (CO_CNES, CO_SERVICO, CO_CLASSIFICACAO) |
| `tb_atendimento_prestado`   | Convênios / SUS (CO_CNES, tipo atendimento)            |

**Chave de junção em todas:** identificador do estabelecimento (CNES). Usar **CO_CNES** (ou coluna equivalente) de forma consistente.

---

## 2. Lógica de JOIN (intersecção)

1. **Passo 1 – Serviço de Urgência**  
   Filtrar `rl_estab_serv_class`:  
   - Serviço = **125** (Urgência Obstetrícia) **e** Classificação = **001** (Atendimento de Urgência);  
   - ou código equivalente para Urgência Neonatal, conforme CNES.  
   Obter conjunto de IDs: `emergency_capable_ids`.

2. **Passo 2 – Leitos**  
   Filtrar `rl_estab_leito`:  
   - `cod_leito` IN (01, 02, 10, 46) e `qt_existente` > 0.  
   Agregar por estabelecimento: quais têm leito obstétrico (01/02) e quais têm UTI Neo (10/46).  
   Obter: `ids_with_obstetric_beds`, e por estabelecimento as flags `has_obstetric_bed`, `has_nicu`.

3. **Passo 3 – Intersecção**  
   `whitelist_ids = emergency_capable_ids ∩ ids_with_obstetric_beds`  
   Ou seja: manter **apenas** estabelecimentos que estão nos dois conjuntos.

4. **Passo 4 – Merge com cadastro**  
   JOIN `whitelist_ids` com `tb_estabelecimento` pela coluna CNES.  
   Trazer: nome, endereço, Lat, Long, telefone, etc.

5. **Passo 5 – Atendimento**  
   JOIN com `tb_atendimento_prestado` (por CNES) para preencher `accepts_sus` e `private_only`.

6. **Passo 6 – Geolocalização**  
   Descartar ou marcar para revisão registros com Lat/Long zerados ou fora do Brasil.

---

## 3. Esquema do JSON final (otimizado para GeoJSON)

Estrutura compatível com GeoJSON para consumo no front (mapas e listagem).

```json
{
  "type": "FeatureCollection",
  "metadata": {
    "source": "CNES",
    "data_version": "YYYY-MM",
    "disclaimer": "Dados do Cadastro Nacional (CNES). Confirme atendimento telefonicamente."
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {
        "id": "CNES_ID",
        "name": "Nome Fantasia ou Razão Social",
        "address": "Endereço completo",
        "city": "Município",
        "state": "UF",
        "phone": "Telefone",
        "accepts_sus": true,
        "private_only": false,
        "has_nicu": true,
        "confidence_score": 100,
        "data_version": "YYYY-MM"
      }
    }
  ]
}
```

- **confidence_score:** ver seção 4.  
- **coordinates:** [long, lat] (ordem GeoJSON).  
- Campos opcionais (ex.: `management`, `natureza_juridica`) podem ser adicionados em `properties` se necessário.

---

## 4. Sistema de Score de Confiança

| Condição                                                                 | Score | Significado      |
|--------------------------------------------------------------------------|-------|------------------|
| Tem Serviço 125/001 **e** leito obstétrico (01 ou 02) **e** (opcional) Habilitação Rede Cegonha | **100** | Verificado       |
| Tem Serviço 125/001 **e** leito obstétrico (01 ou 02)                    | **80**  | Atende critérios |
| Tem apenas leito obstétrico, **sem** Serviço 125/001                     | **0**   | Descartar        |
| Tem apenas Serviço 125/001, **sem** leito obstétrico                     | **0**   | Descartar        |

- **Regra para o pipeline:** Estabelecimentos com score **0** **não** entram no JSON final.  
- O front pode usar `confidence_score` para ordenação ou destaque (ex.: “Verificado” quando = 100).

---

## 5. Arquivo Intermediário (volume grande)

- **Se** o volume de linhas (estabelecimentos + leitos + serviços + atendimento) for grande para gerar JSON direto na memória:
  - **Opção 1:** Gerar uma base **SQLite** com as tabelas já cruzadas (uma tabela `maternities_whitelist` com todas as colunas necessárias). O script de exportação lê do SQLite e gera o GeoJSON em streaming ou em chunks.
  - **Opção 2:** Gerar **Parquet** (por exemplo uma tabela por estado ou região) e depois um job que lê Parquet e escreve GeoJSON/API.

- **Instrução ao Dev:**  
  - Se após os filtros o número de estabelecimentos for pequeno (ex.: &lt; 50k), pode gerar GeoJSON direto.  
  - Se for maior, persistir primeiro em **SQLite** (tabela única com CNES, nome, lat, long, accepts_sus, private_only, has_nicu, confidence_score, data_version) e depois um segundo passo que lê do SQLite e gera o arquivo GeoJSON final.  
  - Incluir no metadata do GeoJSON o campo `data_version` (mês/ano da base CNES) e o texto de disclaimer para exibição no front.

---

## 6. Resumo para o Dev

1. Carregar CSVs/DBFs do CNES (estabelecimento, rl_estab_leito, rl_estab_serv_class, tb_atendimento_prestado).  
2. Aplicar filtros conforme requisitos lógicos; obter `emergency_capable_ids` e `ids_with_obstetric_beds`; intersecção = whitelist.  
3. Merge com tb_estabelecimento por CNES; enriquecer com `has_nicu`, `accepts_sus`, `private_only`; calcular `confidence_score`.  
4. Descartar ou marcar coordenadas inválidas.  
5. Se volume for grande: escrever SQLite (ou Parquet) intermediário; depois gerar GeoJSON a partir dele.  
6. Incluir logs de quantos estabelecimentos foram descartados por cada critério (sem serviço 125/001, sem leito obstétrico, sem geo, etc.).
