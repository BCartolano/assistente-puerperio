# Data quality checks

- **checks/data_quality.py:** Python – telefones válidos, coordenadas no bounding box Brasil, % com evidência, duplicidade por CNPJ. Gate: reprovar se % coordenadas < 85%.
- **checks/sql:** Consultas SQL ad-hoc para auditoria (ex.: `SELECT COUNT(*) FROM hospitals_cache WHERE ...`).

Execução: `python checks/data_quality.py` (exit 0 se gate passar, 1 caso contrário).
