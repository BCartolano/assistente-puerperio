#!/usr/bin/env python3
from pathlib import Path
import sys
import os
import pandas as pd

# Calcula BASE_DIR da mesma forma que o orquestrador
BASE_DIR = Path(__file__).resolve().parent.parent
GEO = BASE_DIR / "data" / "geo" / "hospitals_geo.min.parquet"
GEO_FALLBACK = BASE_DIR / "data" / "geo" / "hospitals_geo.parquet"
ALLOWED = {"Público", "Privado", "Filantrópico", None, ""}

def main():
    # Tenta primeiro o .min.parquet, depois o parquet completo
    geo_path = GEO if GEO.exists() else (GEO_FALLBACK if GEO_FALLBACK.exists() else None)
    if not geo_path:
        print(f"[ERRO] {GEO} ou {GEO_FALLBACK} não encontrado")
        return 2
    df = pd.read_parquet(geo_path)
    col = "esfera" if "esfera" in df.columns else None
    if not col:
        print("[ERRO] coluna 'esfera' ausente")
        return 3
    bad = df[~df[col].isin(ALLOWED)]
    if len(bad) == 0:
        print("[OK] nenhuma esfera inválida no Parquet")
        return 0
    print(f"[ERRO] {len(bad)} linhas com esfera inválida (ex.: {bad[col].dropna().unique()[:5]})")
    out = BASE_DIR / "reports" / "esfera_invalidas.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    bad[[c for c in ("cnes_id", "nome", "esfera", "municipio", "uf") if c in bad.columns]].head(100).to_csv(out, index=False, encoding="utf-8")
    print(f"[INFO] exemplos salvos em {out}")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
