# -*- coding: utf-8 -*-
"""
Gera o índice de hospitais (hospitais_index.json) a partir de CNES/data.
Uso: python scripts/build_hospitals_index.py
     ou: python scripts/build_hospitals_index.py <src1> <src2> <out.json>
"""
import os
import sys

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from backend.geo.indexer import build_hospitals_index
from backend.settings_geo import CNES_BASE_DIR, DATA_DIR, HOSPITALS_INDEX_PATH


def main():
    src1 = CNES_BASE_DIR
    src2 = DATA_DIR
    out = HOSPITALS_INDEX_PATH
    print(f"[INDEX] Lendo fontes:\n - {src1}\n - {src2}\n[INDEX] Saída: {out}")
    payload = build_hospitals_index([src1, src2], out)
    print(f"[INDEX] OK: {payload.get('count')} itens")


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        src1 = sys.argv[1]
        src2 = sys.argv[2]
        out = sys.argv[3]
        payload = build_hospitals_index([src1, src2], out)
        print(f"[INDEX] OK: {payload.get('count')} itens (custom)")
    else:
        main()
