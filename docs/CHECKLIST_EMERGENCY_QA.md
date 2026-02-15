# Checklist – Emergency API e QA

## Pipeline

```bash
python backend/pipelines/prepare_geo_v2.py --snapshot 202512
python backend/pipelines/geocode_ready.py --mode copy
```

## Health

```bash
curl http://localhost:5000/api/v1/health
```

## Busca (debug)

```bash
curl "http://localhost:5000/api/v1/emergency/search?lat=-23.19&lon=-45.79&radius_km=25&expand=true&limit=20&min_results=12&debug=true" | jq
```

Verifique nos itens: `esfera`, `sus_badge`, `label_maternidade`, `nome` (display_name).

## UI

1. Recarregue com **Ctrl+F5**.
2. Confira:
   - Hospital municipal → badge verde **Público** + badge verde **Aceita SUS** (ou "Aceita Cartão SUS").
   - Nenhum **Desconhecido** perto do selo de maternidade.
   - Clínica de psicologia não aparece (ou aparece sem selo rosa de maternidade).

## Exibição dos badges

| Esfera       | Badge        | Cor   |
|-------------|--------------|-------|
| Público     | Público      | Verde |
| Filantrópico| Filantrópico | Azul  |
| Privado     | Privado      | Âmbar |

| SUS             | Badge              | Cor   |
|-----------------|--------------------|-------|
| Aceita SUS      | Aceita Cartão SUS  | Verde |
| Não atende SUS  | Não atende SUS     | Cinza |
| Vazio           | Não renderiza      | —     |

Selo de maternidade: apenas **Ala de Maternidade** ou **Provável maternidade (ligue para confirmar)**. Nunca exibir "Desconhecido".

Na API: `esfera`, `sus_badge`, `label_maternidade`, `display_name`. No card: `item.nome = display_name || nome`; se `sus_badge` for string vazia, não criar badge de SUS.

## QA automático

```bash
python scripts/qa_mismatches.py
```

Gera 3 CSVs em `reports/`:

1. **qa_publico_vs_privado.csv** – Nome indica público (municip/estad/federal) mas `esfera` não é Público.
2. **qa_ambulatorial_vazando.csv** – Prováveis com palavras ambulatoriais (psicolog, fono, fisioter, etc.).
3. **qa_maternidade_nao_marcada.csv** – Nome indica maternidade mas não está em `has_maternity` nem `is_probable`.

Se algum CSV tiver linhas, revise 1–2 exemplos e ajuste filtro/mapeamento no pipeline ou em `cnes_codes.json`.

## Orquestrador

O orquestrador roda `qa_mismatches` ao final (se `RUN_QA_MISMATCHES` não for `false`) e anexa **qa_hints** ao `reports/run_summary.json`:

- `qa_publico_vs_privado`, `qa_ambulatorial_vazando`, `qa_maternidade_nao_marcada`: contagens.
- `qa_reports_dir`, `qa_files`: caminhos dos CSVs.

Útil para auditar o país inteiro após o build.
