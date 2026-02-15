import os
import requests
import pytest

BASE = os.getenv("API_BASE", "http://localhost:5000").rstrip("/")


@pytest.mark.parametrize("lat,lon", [(-23.19, -45.79)])
def test_search_esfera_canonica(lat, lon):
    r = requests.get(
        f"{BASE}/api/v1/emergency/search",
        params={"lat": lat, "lon": lon, "radius_km": 25, "limit": 10, "expand": True},
        timeout=10
    )
    assert r.status_code == 200
    data = r.json() or {}
    bad = [
        it for it in (data.get("results") or [])
        if (it.get("esfera") not in (None, "Público", "Privado", "Filantrópico"))
    ]
    assert not bad, f"esfera inválida no payload: {[(it.get('nome'), it.get('esfera')) for it in bad[:5]]}"
