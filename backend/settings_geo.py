# -*- coding: utf-8 -*-
# Caminhos padrão usados pelo indexador/nearby.
# Podem ser sobrescritos por variáveis de ambiente:
# CNES_BASE_DIR, DATA_DIR, HOSPITALS_INDEX_PATH

import os

# Pasta backend (onde está app.py e static/data)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Raiz do projeto (onde ficam data/ e BASE_DE_DADOS_CNES_202512)
_ROOT = os.path.dirname(BASE_DIR)

CNES_BASE_DIR = os.environ.get(
    "CNES_BASE_DIR",
    os.path.join(_ROOT, "BASE_DE_DADOS_CNES_202512"),
)
DATA_DIR = os.environ.get(
    "DATA_DIR",
    os.path.join(_ROOT, "data"),
)
HOSPITALS_INDEX_PATH = os.environ.get(
    "HOSPITALS_INDEX_PATH",
    os.path.join(BASE_DIR, "static", "data", "hospitais_index.json"),
)
