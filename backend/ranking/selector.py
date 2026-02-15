#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ranking Selector – Top-N por "emergência obstétrica".
Prioridade: has_maternity true > tempo de viagem (ou distância) > atende SUS (se filtrado) > telefone disponível.
"""

import math
from typing import List, Dict, Any, Optional


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em km (Haversine)."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def select_top_n(
    establishments: List[Dict[str, Any]],
    user_lat: float,
    user_lon: float,
    n: int = 3,
    filter_sus: Optional[bool] = None,
    max_km: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Ordena e retorna os top N estabelecimentos para emergência obstétrica.
    Prioridade: has_maternity > distância > atende SUS (se filter_sus) > telefone disponível.
    """
    results = []
    for est in establishments:
        lat = est.get("lat") or est.get("latitude")
        lon = est.get("long") or est.get("longitude")
        if lat is None or lon is None:
            continue
        try:
            lat, lon = float(lat), float(lon)
        except (TypeError, ValueError):
            continue
        dist = haversine_km(user_lat, user_lon, lat, lon)
        if max_km is not None and dist > max_km:
            continue
        if filter_sus is not None:
            sus = est.get("atende_sus") or est.get("is_sus") or est.get("sus")
            if isinstance(sus, bool) and sus != filter_sus:
                continue
            if isinstance(sus, str) and filter_sus and sus.lower() not in ("sim", "s", "1", "true"):
                continue
        has_maternity = est.get("has_maternity") or est.get("maternity") or False
        if isinstance(has_maternity, (int, float)):
            has_maternity = bool(has_maternity)
        phone = est.get("phone") or est.get("telefone") or est.get("nu_telefone")
        has_phone = bool(phone and str(phone).strip() and str(phone).strip().lower() not in ("nan", ""))
        results.append({
            **est,
            "distance_km": round(dist, 2),
            "_has_maternity": 1 if has_maternity else 0,
            "_has_phone": 1 if has_phone else 0,
            "_sus_match": 1 if (filter_sus is None or (est.get("atende_sus") or est.get("is_sus")) == filter_sus) else 0,
        })

    # Ordenar: has_maternity desc, distance asc, _has_phone desc
    results.sort(
        key=lambda x: (
            -x["_has_maternity"],
            x["distance_km"],
            -x["_has_phone"],
        )
    )
    # Remover chaves auxiliares
    for r in results[:n]:
        r.pop("_has_maternity", None)
        r.pop("_has_phone", None)
        r.pop("_sus_match", None)
    return results[:n]
