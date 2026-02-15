#!/usr/bin/env python3
"""
Geocode hospitals_ready → hospitals_geo.
- Modo copy: copia hospitals_ready para hospitals_geo (usa lat/lon já existentes; destrava a UI na hora).
- Modo geocode: geocodifica faltantes com retry/backoff, batch e checkpoint (tmp a cada batch).
"""
import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA = BASE_DIR / "data"
OUT = DATA / "geo"
OUT.mkdir(parents=True, exist_ok=True)
CACHE = DATA / "geocache.sqlite"

try:
    from backend.utils.env import get_env, parse_bounds
except ImportError:
    sys.path.insert(0, str(BASE_DIR))
    from backend.utils.env import get_env, parse_bounds


def _bbox():
    try:
        raw = get_env("COUNTRY_BOUNDS", "-34,5.5,-74.5,-32")
        sN, nN, wW, eE = parse_bounds(raw, (-34.0, 5.5, -74.5, -32.0))
    except Exception:
        sN, nN, wW, eE = -34.0, 5.5, -74.5, -32.0
    return sN, nN, wW, eE


def _in_bbox(lat, lon):
    sN, nN, wW, eE = _bbox()
    return (sN <= lat <= nN) and (wW <= lon <= eE)


def _ensure_cache():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(CACHE))
    con.execute("CREATE TABLE IF NOT EXISTS geocache (q TEXT PRIMARY KEY, lat REAL, lon REAL)")
    con.commit()
    return con


def _session_with_retry(timeout=10, backoff=2, retries=3):
    s = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.request_timeout = timeout
    return s


def _geocode_nominatim(q: str, sess: requests.Session):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": q, "format": "json", "limit": 1, "countrycodes": "br"}
    headers = {"User-Agent": "sophia-obstetric/1.0"}
    r = sess.get(url, params=params, headers=headers, timeout=sess.request_timeout)
    r.raise_for_status()
    j = r.json()
    if j:
        return float(j[0]["lat"]), float(j[0]["lon"])
    return None, None


def _geocode_mapbox(q: str, sess: requests.Session, token: str):
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + requests.utils.quote(q) + ".json"
    params = {"access_token": token, "language": "pt-BR", "limit": 1, "country": "BR"}
    r = sess.get(url, params=params, timeout=sess.request_timeout)
    r.raise_for_status()
    j = r.json()
    if j.get("features"):
        lon, lat = j["features"][0]["center"]
        return float(lat), float(lon)
    return None, None


def _geocode(q: str, con, sess, provider="auto"):
    cur = con.cursor()
    cur.execute("SELECT lat, lon FROM geocache WHERE q = ?", (q,))
    hit = cur.fetchone()
    if hit:
        return hit[0], hit[1]
    lat = lon = None
    token = os.environ.get("MAPBOX_TOKEN") or get_env("MAPBOX_TOKEN", "")
    if provider == "mapbox" or (provider == "auto" and token):
        try:
            lat, lon = _geocode_mapbox(q, sess, token)
        except Exception:
            lat, lon = None, None
    if (lat is None or lon is None) and (provider in ("nominatim", "auto")):
        try:
            lat, lon = _geocode_nominatim(q, sess)
        except Exception:
            lat, lon = None, None
    if lat is not None and lon is not None:
        con.execute("INSERT OR REPLACE INTO geocache(q,lat,lon) VALUES(?,?,?)", (q, lat, lon))
        con.commit()
    return lat, lon


def run(mode="geocode", rate=1.0, batch_size=250, provider="auto"):
    src = OUT / "hospitals_ready.parquet"
    if not src.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {src}. Rode prepare_geo_v2.py antes.")
    df = pd.read_parquet(src)

    if mode == "copy":
        out = OUT / "hospitals_geo.parquet"
        df.to_parquet(out, index=False)
        print(f"[OK] copy mode: salvo {out} ({len(df)} linhas)")
        return out

    miss = df["lat"].isna() | df["lon"].isna()
    print(f"[INFO] geocode faltantes: {int(miss.sum())} / {len(df)}")
    if miss.sum() == 0:
        out = OUT / "hospitals_geo.parquet"
        df.to_parquet(out, index=False)
        print(f"[OK] nada a geocodificar; salvo {out}")
        return out

    con = _ensure_cache()
    sess = _session_with_retry(timeout=10, backoff=1.5, retries=3)
    sleep_s = 1.0 / max(0.1, rate)

    to_index = df.loc[miss].index.tolist()
    for i in range(0, len(to_index), batch_size):
        batch = to_index[i : i + batch_size]
        for idx in batch:
            q = (df.at[idx, "endereco"] or "").strip()
            if not q:
                continue
            if "Brasil" not in q and "BRASIL" not in q:
                q = q + ", Brasil"
            try:
                lat, lon = _geocode(q, con, sess, provider=provider)
            except Exception:
                lat = lon = None
            if lat is not None and lon is not None and _in_bbox(lat, lon):
                df.at[idx, "lat"] = lat
                df.at[idx, "lon"] = lon
            time.sleep(sleep_s)
        out_tmp = OUT / "hospitals_geo.tmp.parquet"
        df.to_parquet(out_tmp, index=False)
        print(f"[CKPT] batch {i // batch_size + 1}: {len(batch)} itens processados; tmp salvo")

    mask_bad = df["lat"].notna() & df["lon"].notna() & ~df.apply(lambda r: _in_bbox(r["lat"], r["lon"]), axis=1)
    df.loc[mask_bad, ["lat", "lon"]] = np.nan

    out = OUT / "hospitals_geo.parquet"
    df.to_parquet(out, index=False)
    print(f"[OK] salvo {out} ({len(df)} linhas)")
    cov = (df["lat"].notna() & df["lon"].notna()).mean()
    print(f"[OK] coord_coverage={cov:.2%}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["copy", "geocode"], default="geocode")
    ap.add_argument("--rate", type=float, default=1.0, help="req/s (Nominatim recomenda 1)")
    ap.add_argument("--batch-size", type=int, default=250)
    ap.add_argument("--provider", choices=["auto", "nominatim", "mapbox"], default="auto")
    args = ap.parse_args()
    run(mode=args.mode, rate=args.rate, batch_size=args.batch_size, provider=args.provider)
