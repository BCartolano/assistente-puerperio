#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Geocode – Usa lat/long do CNES quando houver; senão geocoder configurável + cache local.
Interface geocoder com adaptadores Nominatim/Google/Mapbox; cache em data/geocache.sqlite.
"""

import os
import sys
import json
import sqlite3
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
GEOCACHE_PATH = os.path.join(BASE_DIR, "data", "geocache.sqlite")


def get_geocache_conn():
    os.makedirs(os.path.dirname(GEOCACHE_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(GEOCACHE_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS geocache (
            address_key TEXT PRIMARY KEY,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            address_normalized TEXT,
            source TEXT DEFAULT 'geocoder',
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def get_from_cache(address_key: str) -> tuple | None:
    """Retorna (lat, lon) se estiver no cache."""
    conn = get_geocache_conn()
    try:
        row = conn.execute(
            "SELECT lat, lon FROM geocache WHERE address_key = ?",
            (address_key.strip().lower(),),
        ).fetchone()
        return (row[0], row[1]) if row else None
    finally:
        conn.close()


def put_in_cache(address_key: str, lat: float, lon: float, address_normalized: str = "", source: str = "geocoder"):
    conn = get_geocache_conn()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO geocache (address_key, lat, lon, address_normalized, source, updated_at)
               VALUES (?, ?, ?, ?, ?, datetime('now'))""",
            (address_key.strip().lower(), lat, lon, address_normalized or address_key, source),
        )
        conn.commit()
    finally:
        conn.close()


def normalize_address(logradouro: str, numero: str, bairro: str, city: str, state: str) -> str:
    """Monta endereço normalizado para cache e geocoder."""
    parts = [p for p in [logradouro, numero, bairro, city, state] if p and str(p).strip()]
    return ", ".join(str(p).strip() for p in parts) if parts else ""


def geocode_with_cnes(row: dict) -> tuple | None:
    """Extrai lat/long do registro CNES (tbEstabelecimento)."""
    lat = row.get("NU_LATITUDE") or row.get("lat") or row.get("latitude")
    lon = row.get("NU_LONGITUDE") or row.get("long") or row.get("longitude")
    if lat is not None and lon is not None:
        try:
            return (float(lat), float(lon))
        except (TypeError, ValueError):
            pass
    return None


def geocode_with_nominatim(address: str) -> tuple | None:
    """Fallback: Nominatim (OpenStreetMap). Rate limit: 1 req/s."""
    try:
        import urllib.request
        import urllib.parse
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
            "q": address + ", Brasil",
            "format": "json",
            "limit": 1,
        })
        req = urllib.request.Request(url, headers={"User-Agent": "EmergenciaObstetrica/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data and len(data) > 0:
                loc = data[0]
                return (float(loc["lat"]), float(loc["lon"]))
    except Exception:
        pass
    return None


def main():
    import json
    parser = argparse.ArgumentParser(description="Geocodificação com cache")
    parser.add_argument("--address", default=None, help="Endereço para geocodificar")
    parser.add_argument("--fill-missing", default=None, help="JSON/GeoJSON com estabelecimentos; preenche lat/lon faltantes")
    args = parser.parse_args()

    if args.address:
        key = args.address.strip().lower()
        cached = get_from_cache(key)
        if cached:
            print(f"Cache: {cached[0]}, {cached[1]}")
        else:
            coords = geocode_with_nominatim(args.address)
            if coords:
                put_in_cache(key, coords[0], coords[1], args.address, "nominatim")
                print(f"Geocoded: {coords[0]}, {coords[1]}")
            else:
                print("Não foi possível geocodificar.")
    elif args.fill_missing and os.path.isfile(args.fill_missing):
        with open(args.fill_missing, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Placeholder: iterar features, usar CNES primeiro, depois cache, depois nominatim
        print("Modo fill-missing: use implementação completa no ETL se necessário.")
    else:
        print("Uso: --address 'Rua X, 100, São Paulo, SP' ou --fill-missing arquivo.json")


if __name__ == "__main__":
    main()
