# -*- coding: utf-8 -*-
import os
import time
from flask import Blueprint, abort, jsonify, request

from .indexer import GeoIndex
from .spatial import haversine_km

geo_bp = Blueprint("geo", __name__)


def _env(key, default=None):
    v = os.environ.get(key)
    return v if v is not None else default


def _parse_bool(q):
    if q is None:
        return None
    v = str(q).strip().lower()
    if v in {"true", "1", "sim", "s", "yes", "y"}:
        return True
    if v in {"false", "0", "nao", "não", "n", "no"}:
        return False
    return None


def _default_index_path():
    _bd = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(_bd, "static", "data", "hospitais_index.json")


def _default_source_dirs():
    _bd = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    _root = os.path.dirname(_bd)
    return [
        _env("CNES_BASE_DIR", os.path.join(_root, "BASE_DE_DADOS_CNES_202512")),
        _env("DATA_DIR", os.path.join(_root, "data")),
    ]


_INDEX_PATH = _env("HOSPITALS_INDEX_PATH", _default_index_path())
_SRC_DIRS = _default_source_dirs()
_STORE = GeoIndex(_INDEX_PATH, _SRC_DIRS, ttl_seconds=600)


@geo_bp.route("/api/nearby", methods=["GET"])
def api_nearby():
    t0 = time.time()
    try:
        lat = float(request.args.get("lat", ""))
        lon = float(request.args.get("lon", ""))
    except Exception:
        abort(400, "parâmetros lat/lon obrigatórios")
    radius_km = float(request.args.get("radius_km", 10))
    limit = int(request.args.get("limit", 20))
    f_sus = _parse_bool(request.args.get("accepts_sus"))
    f_conv = _parse_bool(request.args.get("accepts_convenio"))
    f_esfera = request.args.get("public_private")
    if f_esfera:
        f_esfera = f_esfera.strip()
        if f_esfera.lower().startswith("filan"):
            f_esfera = "Filantrópico"
        elif f_esfera.lower().startswith("pub"):
            f_esfera = "Público"
        elif f_esfera.lower().startswith("pri"):
            f_esfera = "Privado"
    try:
        _STORE.ensure_loaded()
    except Exception:
        pass
    items = _STORE.items or []
    out = []
    for h in items:
        d = haversine_km(lat, lon, h.get("lat"), h.get("lon"))
        if d is None or d > radius_km:
            continue
        if f_sus is not None and (h.get("accepts_sus") is not None) and h.get("accepts_sus") != f_sus:
            continue
        if f_conv is not None and (h.get("accepts_convenio") is not None) and h.get("accepts_convenio") != f_conv:
            continue
        if f_esfera and h.get("public_private") and h.get("public_private") != f_esfera:
            continue
        out.append({
            "cnes": h.get("cnes"),
            "name": h.get("name"),
            "address": h.get("address"),
            "lat": h.get("lat"),
            "lon": h.get("lon"),
            "public_private": h.get("public_private"),
            "accepts_sus": h.get("accepts_sus"),
            "accepts_convenio": h.get("accepts_convenio"),
            "distance_km": round(d, 2),
        })
    out.sort(key=lambda x: x["distance_km"])
    out = out[: max(1, min(limit, 200))]
    took_ms = int((time.time() - t0) * 1000)
    resp = jsonify({
        "items": out,
        "count": len(out),
        "meta": {
            "took_ms": took_ms,
            "radius_km": radius_km,
            "limit": limit,
        },
    })
    if _STORE.etag:
        resp.headers["ETag"] = _STORE.etag
    resp.headers["Cache-Control"] = "public, max-age=30"
    return resp


@geo_bp.route("/api/geo/reindex", methods=["POST"])
def api_reindex():
    token = os.environ.get("GEO_REINDEX_TOKEN")
    if token and request.headers.get("X-Geo-Token") != token:
        abort(403)
    _STORE.ensure_loaded(force_rebuild=True)
    return jsonify({"ok": True, "count": len(_STORE.items), "etag": _STORE.etag})
