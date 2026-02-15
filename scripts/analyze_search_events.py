#!/usr/bin/env python3
"""
Analisa logs/search_events.jsonl e gera métricas/CSVs.
Uso:
  python scripts/analyze_search_events.py
  python scripts/analyze_search_events.py --since 2025-02-01 --until 2025-02-29
Saída:
  reports/search_metrics.txt (resumo)
  reports/search_timeline.csv (por dia)
  reports/search_grid_summary.csv (grid 0.1° ~ 11km)
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
LOG = BASE_DIR / "logs" / "search_events.jsonl"
OUT = BASE_DIR / "reports"
OUT.mkdir(parents=True, exist_ok=True)


def load_df(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de log não encontrado: {path}")
    df = pd.read_json(path, lines=True)
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df["date"] = df["ts"].dt.date
    return df


def apply_window(df: pd.DataFrame, since: str | None, until: str | None) -> pd.DataFrame:
    if since:
        df = df[df["ts"] >= pd.to_datetime(since)]
    if until:
        df = df[df["ts"] <= pd.to_datetime(until)]
    return df


def mask_privacy(df: pd.DataFrame, decimals: int = 2) -> pd.DataFrame:
    df = df.copy()
    df["lat_bucket"] = df["lat"].round(1)
    df["lon_bucket"] = df["lon"].round(1)
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description="Analisa search_events.jsonl e gera métricas/CSVs")
    ap.add_argument("--since", help="Data inicial (YYYY-MM-DD)")
    ap.add_argument("--until", help="Data final (YYYY-MM-DD)")
    args = ap.parse_args()

    df = load_df(LOG)
    df = apply_window(df, args.since, args.until)
    if df.empty:
        print("[INFO] Sem eventos nesse período.")
        return 0

    total = len(df)
    expanded = df["expanded"].fillna(False).mean()
    banner = df["banner_192"].fillna(False).mean()
    med_radius = df["radius_used"].fillna(df["radius_requested"]).median()
    hitA = (df["found_A"] > 0).mean() if "found_A" in df.columns else 0.0
    hitB = (df["found_B"] > 0).mean() if "found_B" in df.columns else 0.0
    sus_ratio = df["sus"].map(lambda x: {True: "sus_on", False: "sus_off"}.get(x, "sus_null")).value_counts(normalize=True)

    # timeline diária
    tl = df.groupby(df["ts"].dt.date).agg(
        total=("ts", "count"),
        expanded_pct=("expanded", "mean"),
        banner_192_pct=("banner_192", "mean"),
        med_radius=("radius_used", "median"),
        hitA_pct=("found_A", lambda s: (s > 0).mean()),
        hitB_pct=("found_B", lambda s: (s > 0).mean()),
    ).reset_index()
    tl = tl.rename(columns={tl.columns[0]: "date"})
    tl.to_csv(OUT / "search_timeline.csv", index=False)

    # grid
    gdf = mask_privacy(df)
    grid = gdf.groupby(["lat_bucket", "lon_bucket"]).agg(
        total=("ts", "count"),
        expanded_pct=("expanded", "mean"),
        banner_192_pct=("banner_192", "mean"),
        med_radius=("radius_used", "median"),
        hitA_pct=("found_A", lambda s: (s > 0).mean()),
        hitB_pct=("found_B", lambda s: (s > 0).mean()),
    ).reset_index().sort_values("total", ascending=False)
    grid.to_csv(OUT / "search_grid_summary.csv", index=False)

    # resumo txt
    lines = []
    lines.append(f"Eventos: {total}")
    lines.append(f"Expansão usada: {expanded:.1%}")
    lines.append(f"Banner 192: {banner:.1%}")
    lines.append(f"Raio mediano usado: {med_radius:.1f} km")
    lines.append(f"Hit A (confirmados) em buscas: {hitA:.1%}")
    lines.append(f"Hit B (prováveis) em buscas: {hitB:.1%}")
    lines.append(f"SUS (on/off/sem): {sus_ratio.to_dict()}")
    hot = grid[grid["total"] >= 5].sort_values("banner_192_pct", ascending=False).head(10)
    lines.append("\nHotspots (grid 0.1° com maior banner_192, min 5 buscas):")
    for _, r in hot.iterrows():
        lines.append(f"  ({r.lat_bucket:.1f},{r.lon_bucket:.1f}) • buscas={int(r.total)} • banner_192={r.banner_192_pct:.1%} • exp={r.expanded_pct:.1%} • med_radius={r.med_radius:.1f} km")
    (OUT / "search_metrics.txt").write_text("\n".join(lines), encoding="utf-8")

    print("[OK] Salvo:")
    print(" -", OUT / "search_metrics.txt")
    print(" -", OUT / "search_timeline.csv")
    print(" -", OUT / "search_grid_summary.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
