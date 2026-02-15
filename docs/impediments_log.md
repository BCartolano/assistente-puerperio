# Log de Impedimentos – Localizador de Emergência Obstétrica

Registro de bloqueios e resolução. SM e bmad-master acompanham.

---

## Template por entrada

| Campo | Descrição |
|-------|-----------|
| **ID** | Número ou sigla (ex.: IMP-001). |
| **Data** | Data de abertura. |
| **Descrição** | O que está bloqueando. |
| **Impacto** | Tarefa(s) ou pessoa(s) afetadas. |
| **Status** | Aberto / Em resolução / Resolvido. |
| **Resolução** | Breve descrição da solução (quando resolvido). |

---

## Entradas (exemplo inicial)

### IMP-001 (exemplo)

| Campo | Valor |
|-------|--------|
| **Data** | 2025-02 |
| **Descrição** | CSVs CNES não estavam em data/raw/; pipeline dependia do caminho. |
| **Impacto** | ETL e pipeline de maternidade. |
| **Status** | Resolvido |
| **Resolução** | Pipeline flexível com SEARCH_PATHS múltiplos (data/, BASE_DE_DADOS_CNES_202512, etc.); script de diagnóstico para localizar arquivos. |

---

*Novos impedimentos devem ser adicionados acima com o mesmo formato. SM mantém este documento atualizado.*

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** SM Agent (BMAD)
