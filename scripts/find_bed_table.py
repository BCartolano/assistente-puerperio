#!/usr/bin/env python3
"""
Procura arquivos de 'leitos por estabelecimento' no seu dump do CNES.
Critério: arquivo que contenha CNES + código de leito + quantidade.
Uso: python scripts/find_bed_table.py --snapshot 202512
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent

CANDIDATE_NAMES = [
    "rlEstabLeito",
    "rlEstabTipoLeito",
    "leitos_por_estab",
    "tbLeitoEstab",
    "LEITO_ESTAB",
    "LEITO",
    "rlEstabLeitos",
    "tbLeito",
]
CNES_COLS = {"CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"}
CODE_COLS = {"CO_TIPO_LEITO", "TP_LEITO", "COD_TIPO_LEITO", "CO_LEITO"}
QTY_COLS = {"QT_LEITOS", "QT_EXIST", "QT_EXISTENTE", "QT_LEITO", "QT_SUS", "QT_TOTAL", "QTD_LEITOS", "NU_LEITOS"}


def read_any(p: Path, nrows: int = 2000) -> pd.DataFrame:
    if p.suffix.lower() == ".parquet":
        return pd.read_parquet(p)
    try:
        return pd.read_csv(p, sep=";", dtype=str, nrows=nrows, low_memory=False)
    except Exception:
        return pd.read_csv(p, sep=",", dtype=str, nrows=nrows, low_memory=False)


def cols_upper(df: pd.DataFrame) -> set:
    return set(str(c).strip().upper() for c in df.columns)


def scan_folder(folder: Path, snapshot: str, name_filter: bool) -> list:
    """Varre pasta por .csv e .parquet. Se name_filter, só arquivos cujo nome contém CANDIDATE_NAMES."""
    hits = []
    if not folder.exists():
        return hits
    files = list(folder.glob("*.csv")) + list(folder.glob("*.parquet"))
    for p in files:
        if not p.is_file():
            continue
        name = p.stem.lower()
        if name_filter and not any(k.lower() in name for k in CANDIDATE_NAMES):
            continue
        try:
            df = read_any(p)
            cols = cols_upper(df)
            if (cols & CNES_COLS) and (cols & CODE_COLS) and (cols & QTY_COLS):
                cnes = sorted(cols & CNES_COLS)
                code = sorted(cols & CODE_COLS)
                qty = sorted(cols & QTY_COLS)
                hits.append((p, cnes, code, qty))
        except Exception:
            continue
    return hits


def scan_dump_folder(folder: Path, snapshot: str) -> list:
    """Varre dump (ex.: BASE_DE_DADOS_CNES_202512) por todos .csv/.parquet com colunas certas."""
    hits = []
    if not folder.exists():
        return hits
    for p in folder.rglob("*.csv"):
        if not p.is_file():
            continue
        try:
            df = read_any(p)
            cols = cols_upper(df)
            if (cols & CNES_COLS) and (cols & CODE_COLS) and (cols & QTY_COLS):
                cnes = sorted(cols & CNES_COLS)
                code = sorted(cols & CODE_COLS)
                qty = sorted(cols & QTY_COLS)
                hits.append((p, cnes, code, qty))
        except Exception:
            continue
    for p in folder.rglob("*.parquet"):
        if not p.is_file():
            continue
        try:
            df = read_any(p)
            cols = cols_upper(df)
            if (cols & CNES_COLS) and (cols & CODE_COLS) and (cols & QTY_COLS):
                cnes = sorted(cols & CNES_COLS)
                code = sorted(cols & CODE_COLS)
                qty = sorted(cols & QTY_COLS)
                hits.append((p, cnes, code, qty))
        except Exception:
            continue
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description="Procura tabela 'leitos por estabelecimento' (CNES + tipo + quantidade)")
    ap.add_argument("--snapshot", default="202512")
    args = ap.parse_args()

    folders_data = [
        BASE / "data",
        BASE / "data" / "raw" / args.snapshot,
    ]
    dump = BASE / "BASE_DE_DADOS_CNES_202512"

    total_hits = []
    for f in folders_data:
        total_hits += scan_folder(f, args.snapshot, name_filter=False)
    total_hits += scan_dump_folder(dump, args.snapshot)

    if not total_hits:
        print("[ERRO] Não encontrei arquivo de 'leitos por estabelecimento'.", file=sys.stderr)
        print("  Critério: colunas CNES (CO_CNES/CO_UNIDADE) + código (CO_TIPO_LEITO/TP_LEITO) + quantidade (QT_*).", file=sys.stderr)
        print("  Procure por rlEstabLeito*.csv no pacote CNES/DataSUS ou use --snapshot correto.", file=sys.stderr)
        return 1

    print("[OK] Candidatos encontrados:")
    for p, cnes, code, qty in total_hits:
        print(f"  - {p}")
        print(f"    CNES={cnes} | CODE={code} | QTY={qty}")
    print("\nAponte um desses para o pipeline: copie para data/tbLeito<SNAPSHOT>.csv ou ajuste _find_file em prepare_geo_v2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
