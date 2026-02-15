#!/usr/bin/env python3
"""
Healthcheck do dataset geográfico (geo/ready).
- Lê data/geo/hospitals_geo.parquet (fallback: hospitals_ready.parquet).
- Mostra totais, cobertura de coordenadas/telefone, Confirmados/Prováveis/Outros.
- Quebra por UF e (opcional) por município.
- Gera relatórios em reports/:
  - geo_health_summary.txt
  - geo_by_uf.csv
  - geo_by_municipio.csv (com --municipios)
  - geo_missing_coords.csv (com --export-missing)
Uso:
  python scripts/check_geo_parquet.py
  python scripts/check_geo_parquet.py --municipios --export-missing
Saída de erro (exit code > 0) só em caso de arquivo ausente ou leitura corrompida.
"""
import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
GEO = DATA / "geo"
OUT = BASE / "reports"
OUT.mkdir(parents=True, exist_ok=True)


def norm_digits(s: str) -> str:
    return re.sub(r"\D", "", str(s or ""))


def norm_cnes(v) -> str:
    d = norm_digits(v)
    if len(d) >= 7:
        d = d[:7]
    return d.zfill(7) if d else ""


def load_df() -> tuple[pd.DataFrame, str]:
    geo = GEO / "hospitals_geo.parquet"
    ready = GEO / "hospitals_ready.parquet"
    if geo.exists():
        return pd.read_parquet(geo), str(geo)
    if ready.exists():
        return pd.read_parquet(ready), str(ready)
    raise FileNotFoundError(
        "Nenhum Parquet encontrado em data/geo/ (hospitals_geo.parquet ou hospitals_ready.parquet)."
    )


def phone_present(row) -> bool:
    tel = str(row.get("telefone") or "").strip()
    disp = str(row.get("telefone_formatado") or "").strip()
    e164 = str(row.get("phone_e164") or "").strip()
    if e164:
        return True
    if disp and disp.lower() != "telefone não informado":
        return True
    if tel and tel.lower() != "nan":
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--municipios", action="store_true", help="gerar também o geo_by_municipio.csv")
    ap.add_argument("--export-missing", action="store_true", help="exportar lista de sem coordenadas")
    args = ap.parse_args()

    df, src = load_df()
    total = len(df)
    if total == 0:
        print("[ERRO] Parquet está vazio.")
        return 2

    df = df.copy()
    if "cnes_id" in df.columns:
        df["cnes_id"] = df["cnes_id"].map(norm_cnes)

    has_coords = df["lat"].notna() & df["lon"].notna()
    has_phone = df.apply(phone_present, axis=1)
    is_conf = (df["has_maternity"] == True) if "has_maternity" in df.columns else pd.Series(False, index=df.index)
    is_prob = (
        (df["is_probable"] == True) if "is_probable" in df.columns else pd.Series(False, index=df.index)
    )
    is_prob = is_prob & (~is_conf)

    coord_cov = has_coords.mean()
    phone_cov = has_phone.mean()
    n_conf = int(is_conf.sum())
    n_prob = int(is_prob.sum())
    n_outros = int(total - n_conf - n_prob)

    ats = df["atende_sus"] if "atende_sus" in df.columns else None
    sus_sim = int((ats == "Sim").sum()) if ats is not None else 0
    sus_nao = int((ats == "Não").sum()) if ats is not None else 0
    sus_desc = int((ats == "Desconhecido").sum()) if ats is not None else 0

    uf = df["uf"].fillna("??") if "uf" in df.columns else pd.Series(["??"] * total, index=df.index)
    sus_sim_s = (ats == "Sim").astype(int) if ats is not None else pd.Series(0, index=df.index)
    sus_nao_s = (ats == "Não").astype(int) if ats is not None else pd.Series(0, index=df.index)
    sus_desc_s = (ats == "Desconhecido").astype(int) if ats is not None else pd.Series(0, index=df.index)
    by_uf = pd.DataFrame({
        "uf": uf,
        "total": 1,
        "with_coords": has_coords.astype(int),
        "confirmados": is_conf.astype(int),
        "provaveis": is_prob.astype(int),
        "outros": (~is_conf & ~is_prob).astype(int),
        "sus_sim": sus_sim_s,
        "sus_nao": sus_nao_s,
        "sus_desc": sus_desc_s,
    }).groupby("uf", as_index=False).sum()

    by_uf["pct_coords"] = (by_uf["with_coords"] / by_uf["total"]).round(4)
    by_uf["pct_confirmados"] = (by_uf["confirmados"] / by_uf["total"]).round(4)

    if args.municipios:
        mun = df["municipio"].fillna("??") if "municipio" in df.columns else pd.Series(["??"] * total, index=df.index)
        by_mun = pd.DataFrame({
            "uf": uf,
            "municipio": mun,
            "total": 1,
            "with_coords": has_coords.astype(int),
            "confirmados": is_conf.astype(int),
            "provaveis": is_prob.astype(int),
        }).groupby(["uf", "municipio"], as_index=False).sum()
        by_mun["pct_coords"] = (by_mun["with_coords"] / by_mun["total"]).round(4)
        by_mun["pct_confirmados"] = (by_mun["confirmados"] / by_mun["total"]).round(4)
        by_mun.sort_values(["confirmados", "total"], ascending=[False, False]).to_csv(
            OUT / "geo_by_municipio.csv", index=False, encoding="utf-8"
        )

    if args.export_missing:
        cols = ["cnes_id", "nome", "endereco", "municipio", "uf", "telefone", "telefone_formatado", "atende_sus"]
        miss_df = df.loc[~has_coords, [c for c in cols if c in df.columns]].copy()
        miss_df.to_csv(OUT / "geo_missing_coords.csv", index=False, encoding="utf-8")

    by_uf.sort_values(["confirmados", "total"], ascending=[False, False]).to_csv(
        OUT / "geo_by_uf.csv", index=False, encoding="utf-8"
    )

    lines = []
    lines.append(f"Fonte: {src}")
    lines.append(f"Total: {total}")
    lines.append(f"Cobertura de coordenadas: {coord_cov:.1%}")
    lines.append(f"Cobertura de telefone: {phone_cov:.1%}")
    lines.append(f"Confirmados (Ala de Maternidade): {n_conf}")
    lines.append(f"Prováveis: {n_prob}")
    lines.append(f"Outros: {n_outros}")
    lines.append(f"SUS: Sim={sus_sim} • Não={sus_nao} • Desconhecido={sus_desc}")
    lines.append("")
    lines.append("Top UFs por confirmados:")
    top = by_uf.sort_values(["confirmados", "total"], ascending=[False, False]).head(10)
    for _, r in top.iterrows():
        lines.append(f"  {r['uf']}: conf={int(r['confirmados'])} • total={int(r['total'])} • coords={r['pct_coords']:.1%}")

    (OUT / "geo_health_summary.txt").write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    print(f"\n[OK] relatórios salvos em: {OUT}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
