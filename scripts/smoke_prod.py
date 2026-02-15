#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke de produção:

- GET /api/v1/health/short -> 200 e dataset.present true (ou não checa se --allow-no-dataset)
- GET /api/v1/emergency/search?lat=&lon=&radius_km=&limit=1 -> 200 e pelo menos 1 resultado

Saída: exit 0 se ok; 1 se erro

Uso:
  python scripts/smoke_prod.py --base-url https://SEU_APP --lat -23.19 --lon -45.79 --radius 25
  python scripts/smoke_prod.py --base-url http://localhost:5000 --allow-no-dataset
"""
from __future__ import annotations

import argparse
import sys

try:
    import requests
except ImportError:
    print("[ERRO] instale requests: pip install requests")
    sys.exit(1)


def main() -> int:
    ap = argparse.ArgumentParser(description="Smoke de produção: health/short + emergency/search")
    ap.add_argument("--base-url", required=True, help="URL base (ex.: https://app.example.com)")
    ap.add_argument("--lat", type=float, required=True, help="Latitude para emergency/search")
    ap.add_argument("--lon", type=float, required=True, help="Longitude para emergency/search")
    ap.add_argument("--radius", type=float, default=25, help="radius_km (default 25)")
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--allow-no-dataset", action="store_true", help="Não falhar se dataset.present=false")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")

    # 1) health curto
    try:
        r = requests.get(f"{base}/api/v1/health/short", timeout=args.timeout)
        r.raise_for_status()
        hs = r.json()
        if not args.allow_no_dataset and not (hs.get("dataset") or {}).get("present", False):
            print("[ERRO] dataset.present = false")
            return 1
    except Exception as e:
        print(f"[ERRO] health_short: {e}")
        return 1

    # 2) emergency search
    try:
        url = f"{base}/api/v1/emergency/search?lat={args.lat}&lon={args.lon}&radius_km={args.radius}&limit=1"
        r = requests.get(url, timeout=args.timeout)
        r.raise_for_status()
        data = r.json() or {}
        res = data.get("results") or []
        if len(res) < 1:
            print("[ERRO] emergency/search vazio")
            return 1
        it = res[0]
        for f in ("cnes_id", "nome", "esfera", "label_maternidade", "telefone_formatado"):
            if f not in it:
                print(f"[ERRO] campo ausente no result: {f}")
                return 1
    except Exception as e:
        print(f"[ERRO] emergency/search: {e}")
        return 1

    print("[OK] smoke: health_short e emergency/search ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
