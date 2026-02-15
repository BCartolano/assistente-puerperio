# Tarefa – Index de Maternidades (CNES/DataSUS)

**Fontes:** TB_ESTABELECIMENTO.csv (NO_FANTASIA, NO_RAZAO_SOCIAL, NO_LOGRADOURO, NU_ENDERECO, NO_BAIRRO, CO_MUNICIPIO, CO_UF, NU_TELEFONE, CO_DDD,...), TB_GESTAO.csv, TB_NATUREZA_JURIDICA.csv, TB_TIPO_UNIDADE.csv, TB_CONTRATO_CONVENIO.csv, e demais tabelas que indiquem leitos/serviços obstétricos.

**Objetivo:** consolidar um index `{cnes, nome, lat, lon, endereco, tem_maternidade, esfera, aceita_sus, convenios}`, com validação manual.

**Heurísticas (início):** tipo de unidade hospital/maternidade; serviços ou especialidades obstétricas; leitos obstétricos; vínculo SUS; esfera.

**Saída:** `backend/static/data/maternidades_index.json` e CSV auxiliar; log/relatório com quantidades por UF e município.

**Integração:** o backend usará esse index quando houver (`maternity_only=true`) em `/api/v1/emergency/search`, filtrando apenas unidades com `tem_maternidade=true`.
