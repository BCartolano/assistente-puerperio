#!/usr/bin/env python3
"""Agrupa hospitals_ready por UF: confirmados (has_maternity), prováveis, total. Salva em reports/confirmados_por_uf.csv."""
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
GEO = BASE / "data" / "geo"
REPORTS = BASE / "reports"


def main() -> int:
    p = GEO / "hospitals_ready.parquet"
    if not p.exists():
        print("[ERRO] data/geo/hospitals_ready.parquet não encontrado. Rode prepare_geo_v2 primeiro.", file=sys.stderr)
        return 2
    df = pd.read_parquet(p)
    if "uf" not in df.columns:
        print("[ERRO] Coluna 'uf' não encontrada em hospitals_ready.", file=sys.stderr)
        return 3
    g = df.groupby("uf").agg(
        confirmados=("has_maternity", lambda s: (s == True).sum()),
        provaveis=("is_probable", lambda s: (s == True).sum()),
        total=("cnes_id", "count"),
    ).reset_index().sort_values("confirmados", ascending=False)
    print(g.to_string(index=False))
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "confirmados_por_uf.csv"
    g.to_csv(out, index=False)
    print(f"[OK] salvo {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
