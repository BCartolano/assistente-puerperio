#!/usr/bin/env python3
"""
Script de diagnóstico rápido (geo v2).
Conta estabelecimentos após filtro anti-fantasma, Confirmados/Prováveis,
cobertura de coordenadas antes/depois do geocode, simula busca e mostra top 10.
Uso: python scripts/diag_geo_v2.py --lat -23.55 --lon -46.63 --radius 25
"""
import argparse
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA = BASE_DIR / "data"
GEO = DATA / "geo"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    to_rad = math.radians
    dlat = to_rad(lat2 - lat1)
    dlon = to_rad(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def main() -> int:
    ap = argparse.ArgumentParser(description="Diagnóstico rápido: hospitals_ready + hospitals_geo + busca simulada")
    ap.add_argument("--lat", type=float, required=True, help="Latitude do usuário")
    ap.add_argument("--lon", type=float, required=True, help="Longitude do usuário")
    ap.add_argument("--radius", type=float, default=25.0, help="Raio em km para busca simulada")
    args = ap.parse_args()

    ready = GEO / "hospitals_ready.parquet"
    geo = GEO / "hospitals_geo.parquet"

    if not ready.exists():
        print(f"[ERRO] {ready} não encontrado. Rode prepare_geo_v2 primeiro.")
        return 2

    df_r = pd.read_parquet(ready)
    print(f"[INFO] hospitals_ready: {len(df_r)} linhas")
    print(f"  Confirmados (has_maternity): {int((df_r['has_maternity'] == True).sum())}")
    print(f"  Prováveis (is_probable):     {int(((df_r['has_maternity'] != True) & (df_r['is_probable'] == True)).sum())}")
    cov_ready = (df_r["lat"].notna() & df_r["lon"].notna()).mean()
    print(f"  coord_coverage (ready): {cov_ready:.2%}")

    if not geo.exists():
        print(f"[AVISO] {geo} não encontrado. Rode geocode_ready para preencher coordenadas.")
        df = df_r.copy()
    else:
        df = pd.read_parquet(geo)
        cov_geo = (df["lat"].notna() & df["lon"].notna()).mean()
        print(f"[INFO] hospitals_geo: {len(df)} linhas")
        print(f"  coord_coverage (geo):   {cov_geo:.2%}")

    df = df[(df["lat"].notna()) & (df["lon"].notna())].copy()
    if df.empty:
        print("[ERRO] Nenhum registro com coordenadas. Verifique geocodificação.")
        return 3

    df["dist_km"] = df.apply(lambda r: haversine_km(args.lat, args.lon, float(r["lat"]), float(r["lon"])), axis=1)
    in_radius = df[df["dist_km"] <= args.radius].copy()
    A = in_radius[in_radius["has_maternity"] == True]
    B = in_radius[(in_radius["has_maternity"] != True) & (in_radius["is_probable"] == True)]

    print(f"\n[BUSCA] Raio {args.radius} km ao redor ({args.lat},{args.lon})")
    print(f"  A (confirmados) no raio: {len(A)}")
    print(f"  B (prováveis)    no raio: {len(B)}")

    top = in_radius.sort_values(["has_maternity", "is_probable", "dist_km"], ascending=[False, False, True]).head(10)
    if len(top) == 0:
        print("  Nenhum no raio. Experimente radius 50/100 ou verifique filtros.")
    else:
        print("\nTop 10 no raio (prioridade A>B):")
        for _, r in top.iterrows():
            label = "Ala de Maternidade" if bool(r["has_maternity"]) else ("Provável" if bool(r["is_probable"]) else "Geral")
            nome = (r.get("nome") or r.get("name") or "")[:50]
            print(f"  {nome} • {label} • {r.get('atende_sus', '')} • {r.get('esfera', '')} • {r['dist_km']:.1f} km")

    return 0


if __name__ == "__main__":
    sys.exit(main())

# --- Checklist rápido se ainda aparecer "só 2" ---
# Depois do prepare_geo_v2:
#   • Confirmados > 0? Se 0, tbLeito não está casando (coluna código/descrição ou quantidade).
#     Ver leito_codes_obst/leito_codes_neonatal em config/cnes_codes.json.
#   • Prováveis fazem sentido? Se poucos, amplie keywords_nome_fantasia (ex.: "Hospital Materno Infantil").
# Depois do geocode_ready:
#   • coord_coverage >= 0.85? Se baixo, endereço ruim; tente "endereco + , Brasil" ou outro provider com token.
# Na busca:
#   • Teste radius 50/100; expand=true na API. Cidades menores podem ter 0–1 maternidade no raio curto.
#   • Se filtrou por SUS, teste sem o parâmetro sus primeiro.
# Dicas: Confirmado por leitos é o principal; "Provável" com keywords ampliadas + "ligue para confirmar".
# Próximos: tbServico/tbHabilitacao para mais Confirmados; TRAVEL_TIME=on + MAPBOX_TOKEN; risco neonatal.
