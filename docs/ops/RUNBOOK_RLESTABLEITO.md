# Runbook: rlEstabLeito (Leitos por Estabelecimento)

Quando você tiver o arquivo **rlEstabLeito** (leitos por estabelecimento), o pipeline já está pronto: os confirmados por leito entram como sinal forte (0.6) e o selo **"Ala de Maternidade"** passa a aparecer em larga escala na UI.

---

## Onde encontrar o rlEstabLeito

| Fonte | Descrição |
|-------|-----------|
| **DATASUS FTP** | `ftp://ftp.datasus.gov.br/dissemin/publicos/CNES/200508_/Dados/LT/` — arquivos por UF: `LT{UF}{YYMM}.dbc` (ex.: `LTSP2512.dbc` = SP, dez/2025). Pode exigir acesso de dentro do Brasil. |
| **Espelho S3** | `https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/dissemin/publicos/CNES/200508_/Dados/LT/` — mesmo layout, sem restrição geográfica. |
| **CNES – Downloads** | [cnes.datasus.gov.br – Downloads](https://cnes.datasus.gov.br/pages/downloads/arquivosAplicacao.jsp) — arquivos da aplicação CNES. |
| **Portal Dados Abertos** | [dados.gov.br – CNES](https://dados.gov.br/dados/conjuntos-dados/cnes-cadastro-nacional-de-estabelecimentos-de-saude) — conjuntos CNES. |
| **Base dos Dados** | [basedosdados.org – CNES](https://basedosdados.org/dataset/354d6d98-bc09-4e22-a58a-e4eac3a5283c) — cobertura 2005–2025. |

Em alguns pacotes o arquivo vem como **rlEstabLeito202512.csv** dentro de pasta “relacional/Leito” ou com nome parecido. O pipeline procura em:

- `data/rlEstabLeito202512.csv`
- `data/tbLeito202512.csv`
- `data/raw/202512/rlEstabLeito202512.csv`
- `BASE_DE_DADOS_CNES_202512/rlEstabLeito202512.csv`

---

## Mini-runbook (quando você tiver o rlEstabLeito 2025-12)

1. **Colocar o arquivo**
   - `data/tbLeito202512.csv` **ou** `data/rlEstabLeito202512.csv` (ou no dump com um desses nomes; o pipeline já procura).

2. **Reprocessar**
   ```bash
   python backend/pipelines/prepare_geo_v2.py --snapshot 202512
   python backend/pipelines/geocode_ready.py
   ```

3. **Validar**
   ```bash
   python scripts/diag_geo_v2.py --lat -23.55 --lon -46.63 --radius 25
   curl "http://localhost:5000/api/v1/emergency/search?lat=-23.55&lon=-46.63&radius_km=25&expand=true&limit=20&min_results=12&debug=true"
   ```
   Na UI, os cards com **"Ala de Maternidade"** devem começar a aparecer.

4. **Observabilidade**
   - `python scripts/confirmados_por_uf.py` → confirmados por UF
   - `run_summary.json` → `search_metrics` (ex.: `hitA_pct` deve subir)

---

## Como me enviar o rlEstabLeito (para eu conferir)

- **Cabeçalho + 4 linhas** (pode mascarar valores de CNES, mas manter o formato).
- Preciso ver:
  - coluna de **estabelecimento** (CO_CNES / CO_UNIDADE),
  - coluna de **tipo** (CO_TIPO_LEITO / TP_LEITO),
  - coluna de **quantidade** (QT_*).
- Com isso eu:
  - confirmo os arrays `leito_codes_obst` / `leito_codes_neonatal` (2/3/4 vs 02/03/04),
  - te mando um diff do `cnes_codes.json` se precisar,
  - valido com um print do diag mostrando “Confirmados” subindo.

---

## Script de download automático (LT por UF → CSV único)

O DATASUS distribui **LT por UF** em formato `.dbc`. O script junta todos os UFs e gera um CSV no formato esperado pelo pipeline.

**Uso:**

```bash
# Opcional: instalar leitor de DBC (um dos dois)
pip install pysus
# ou
pip install pyreaddbc

# Baixar e gerar data/rlEstabLeito202512.csv
python scripts/download_rlEstabLeito.py --snapshot 202512

# Só baixar .dbc em data/raw/202512/ (sem converter)
python scripts/download_rlEstabLeito.py --snapshot 202512 --only-download-dbc
```

**No Windows:** use `dbc-to-dbf` + `dbfread` (Python puro, não exige Build Tools nem compilador C):
```bash
python -m pip install dbc-to-dbf dbfread
```
O pacote `pyreaddbc` no Windows costuma falhar com `unistd.h` (código C para Unix). O script tenta primeiro `pyreaddbc`, depois `dbc-to-dbf`+`dbfread`, depois `pysus`. Se nenhum estiver instalado, os `.dbc` ficam em `data/raw/<snapshot>/` e o script avisa.

**Nota:** O espelho S3 pode não ter o mês mais recente (ex.: 2512). Os metadados DATASUS indicam dados até **março/2025**; dez/2025 (2512) pode ainda não estar publicado. Se nada for baixado:
- Tente um mês anterior: `python scripts/download_rlEstabLeito.py --snapshot 202511`
- Ou use o FTP oficial (de dentro do Brasil) — o script tenta download direto por FTP automaticamente
- Ou use um CSV já convertido do Portal de Dados Abertos / Base dos Dados

---

## Três caminhos possíveis

| Caminho | Situação | O que fazer |
|--------|----------|-------------|
| **1 – Operar sem rlEstabLeito** | Já funciona hoje | Confirmado por Serviço (rlEstabServClass) e por nome/tipo; “Confirmados até 100 km” ativo. |
| **2 – Mesmo snapshot** | tbEstabelecimento e rlEstabServClass de dumps diferentes | Usar tbEstabelecimento do **mesmo** diretório do rlEstabServClass (ex.: BASE_DE_DADOS_CNES_202512) e CNES normalizado (zfill 7). |
| **3 – Com rlEstabLeito** | Arquivo de leitos disponível | Colocar em `data/tbLeito202512.csv` ou `data/rlEstabLeito202512.csv`, rodar prepare_geo_v2 + geocode_ready; UI passa a exibir “Ala de Maternidade” em escala. |

---

## Formato esperado do CSV de leitos

- **Estabelecimento:** `CO_CNES` ou `CO_UNIDADE`
- **Tipo de leito:** `CO_TIPO_LEITO` ou `TP_LEITO`
- **Quantidade:** uma de `QT_LEITOS`, `QT_EXIST`, `QT_EXISTENTE`, `QT_LEITO`, `QT_SUS`, `QT_TOTAL`, `NU_LEITOS`

O pipeline normaliza códigos (ex.: 02/03/04) e usa `config/cnes_codes.json` (`leito_codes_obst`, `leito_codes_neonatal`) para marcar “Ala de Maternidade”.
