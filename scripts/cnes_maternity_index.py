# -*- coding: utf-8 -*-
"""
Esqueleto para os Agentes/Cursor processarem CNES e gerarem um index de maternidades.
Ver docs/TAREFA_MATERNIDADES.md para o plano completo.
"""
import os
import csv
import json
from typing import Dict, Iterable, List

try:
    import pandas as pd
except Exception:
    pd = None


def main():
    base = os.environ.get("CNES_BASE_DIR", r"C:\Users\...\BASE_DE_DADOS_CNES_202512")
    out = os.path.join("backend", "static", "data", "maternidades_index.json")

    # TODO: ler TB_ESTABELECIMENTO.csv, TB_GESTAO.csv, TB_NATUREZA_JURIDICA.csv, TB_TIPO_UNIDADE.csv
    # unir por CNES; marcar tem_maternidade com base em tipo/serviço/leito obstétrico; guarda esfera/SUS/convênios
    # salvar JSON, e um relatório em stdout (contagens por UF)
    raise SystemExit("Preencha este script com as regras de fusão; ver docs/TAREFA_MATERNIDADES.md")


if __name__ == "__main__":
    main()
