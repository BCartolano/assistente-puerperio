#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loader de variáveis de ambiente (.env).
Variáveis: API_PORT, DB_URL, SCORING_FILE, CNES_CODES_FILE, GEOCODER, TRAVEL_TIME,
MAPBOX_TOKEN, GOOGLE_MAPS_KEY, COUNTRY_BOUNDS, SNAPSHOT, RUN_TESTS, RUN_GEOCODE,
GOLDEN_SET_FILE, ALLOW_ORIGINS, TZ.
Helpers: parse_bool(), parse_bounds().
"""

import os
from pathlib import Path
from typing import List, Tuple

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def parse_bool(value: str, default: bool = False) -> bool:
    """Converte string para bool: 1/true/on/yes → True; 0/false/off/no → False."""
    v = (value or "").strip().lower()
    if v in ("1", "true", "on", "yes"):
        return True
    if v in ("0", "false", "off", "no"):
        return False
    return default


def parse_bounds(value: str, default: Tuple[float, float, float, float] = (-34.0, 5.5, -74.5, -32.0)) -> Tuple[float, float, float, float]:
    """Converte COUNTRY_BOUNDS (ex.: '-34,5.5,-74.5,-32') em (lat_min, lat_max, lon_min, lon_max)."""
    if not value or not value.strip():
        return default
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if len(parts) != 4:
        return default
    try:
        return (float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]))
    except ValueError:
        return default


# API
API_PORT = int(get_env("API_PORT", "8000"))

# Banco/arquivos
DB_URL = get_env("DB_URL", f"sqlite:///{BASE_DIR / 'backend' / 'cnes_cache.db'}")
SCORING_FILE = get_env("SCORING_FILE", str(BASE_DIR / "config" / "scoring.yaml"))
CNES_CODES_FILE = get_env("CNES_CODES_FILE", str(BASE_DIR / "config" / "cnes_codes.json"))

# Geocoding e tempo de viagem
GEOCODER = get_env("GEOCODER", "nominatim")
TRAVEL_TIME = get_env("TRAVEL_TIME", "off")
MAPBOX_TOKEN = get_env("MAPBOX_TOKEN", "")
GOOGLE_MAPS_KEY = get_env("GOOGLE_MAPS_KEY", "")
COUNTRY_BOUNDS = get_env("COUNTRY_BOUNDS", "-34,5.5,-74.5,-32")

# Orquestrador
SNAPSHOT = get_env("SNAPSHOT", "202512")
RUN_TESTS = parse_bool(get_env("RUN_TESTS", "true"), True)
RUN_GEOCODE = parse_bool(get_env("RUN_GEOCODE", "true"), True)
GOLDEN_SET_FILE = get_env("GOLDEN_SET_FILE", str(BASE_DIR / "data" / "golden" / "golden_set.json"))

# CORS / TZ
ALLOW_ORIGINS = get_env("ALLOW_ORIGINS", "*")
TZ = get_env("TZ", "America/Sao_Paulo")
