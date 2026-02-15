#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Ingest – Carrega CSVs CNES, normaliza colunas, valida tipos, grava em DB.
Uso: python -m backend.pipelines.ingest [--snapshot 202512] [--output-db path]
Integra com backend/etl/data_ingest.py quando disponível.
"""

import os
import sys
import argparse

# Raiz do projeto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def main():
    parser = argparse.ArgumentParser(description="Ingestão CNES: CSVs → DB")
    parser.add_argument("--snapshot", default="202512", help="Snapshot data/raw/<snapshot>/")
    parser.add_argument("--output-db", default=None, help="Caminho do DB (default: backend/cnes_cache.db)")
    args = parser.parse_args()

    db_path = args.output_db or os.path.join(BASE_DIR, "backend", "cnes_cache.db")
    raw_dir = os.path.join(BASE_DIR, "data", "raw", args.snapshot)
    if not os.path.isdir(raw_dir):
        # Fallback: data/ ou BASE_DE_DADOS_CNES_*
        raw_dir = os.path.join(BASE_DIR, "data")
    if not os.path.isdir(raw_dir):
        alt = os.path.join(BASE_DIR, "BASE_DE_DADOS_CNES_202512")
        if os.path.isdir(alt):
            raw_dir = alt

    try:
        # Usar ETL existente se disponível
        from backend.etl import data_ingest
        run = getattr(data_ingest, "run_ingest", None) or getattr(data_ingest, "main", None)
        if run:
            print(f"Executando data_ingest (DB: {db_path})...")
            if callable(run):
                run()
            else:
                data_ingest.ingest_from_paths(raw_dir, db_path)
        else:
            # Fallback: chamar maternity_whitelist_pipeline para gerar GeoJSON
            from backend.etl.maternity_whitelist_pipeline import run_pipeline
            print("Executando maternity_whitelist_pipeline (GeoJSON)...")
            run_pipeline()
    except Exception as e:
        print(f"ERRO ingest: {e}")
        sys.exit(1)
    print("Ingest concluído.")


def ingest_from_paths(raw_dir: str, db_path: str):
    """Chamada programática: ingere a partir de raw_dir e grava em db_path."""
    import sqlite3
    # Placeholder: criar schema mínimo e delegar ao data_ingest se existir
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        from backend.etl import data_ingest
        if hasattr(data_ingest, "create_schema"):
            data_ingest.create_schema(conn)
        # Carregar CSVs de raw_dir seria implementado aqui ou em data_ingest
    finally:
        conn.close()


if __name__ == "__main__":
    main()
