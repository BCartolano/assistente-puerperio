#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempo de viagem: Mapbox Matrix API. Fallback None quando TRAVEL_TIME=off ou sem token.
"""

import os
from typing import List, Optional, Tuple

try:
    from backend.utils.env import TRAVEL_TIME, MAPBOX_TOKEN
except ImportError:
    TRAVEL_TIME = os.environ.get("TRAVEL_TIME", "off")
    MAPBOX_TOKEN = os.environ.get("MAPBOX_TOKEN", "")


def get_travel_times(
    origem: Tuple[float, float],
    destinos: List[Tuple[float, float]],
) -> Optional[List[Optional[float]]]:
    """
    Retorna lista de durações em segundos na mesma ordem dos destinos (ou None por destino se falha).
    Usa Mapbox Matrix API (profile driving) quando TRAVEL_TIME=on e MAPBOX_TOKEN válido.
    Caso contrário retorna None. Em qualquer erro, retorna None (fallback).
    """
    if TRAVEL_TIME.lower() != "on" or not (MAPBOX_TOKEN or "").strip():
        return None
    if not destinos:
        return []
    try:
        import urllib.request
        import urllib.parse
        import json
        coords = [f"{origem[1]},{origem[0]}"]
        for d in destinos:
            coords.append(f"{d[1]},{d[0]}")
        coords_str = ";".join(coords)
        url = (
            f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{urllib.parse.quote(coords_str)}"
            f"?access_token={MAPBOX_TOKEN}&annotations=duration"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "EmergenciaObstetrica/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        durations = data.get("durations") or []
        if durations and len(durations) > 0:
            # durations[0] = tempos da origem (índice 0) para cada destino (1..n)
            row = durations[0]
            return [round(float(row[i]), 1) if i < len(row) and row[i] is not None else None for i in range(1, len(row))]
        return [None] * len(destinos)
    except Exception:
        return None
