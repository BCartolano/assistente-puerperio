# -*- coding: utf-8 -*-
"""
Blueprint: Health (CNES, Emergência, Hospitais, Vacinação, Debug).
Rotas: /api/v1/emergency/*, /api/v1/facilities/search, /api/v1/health,
/api/v1/debug/*, /api/vacinas/mae|bebe|status|marcar|desmarcar,
/api/vaccination/status|mark-done, /api/baby_profile.
CNES overrides: importados de backend.startup.cnes_overrides (lazy via get_overrides_count/get_snapshot_used).
"""
import os
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime

from flask import Blueprint, request, jsonify, Response, current_app, session
from flask_login import current_user, login_required

health_bp = Blueprint("health", __name__, url_prefix="")

_BACKEND = Path(__file__).resolve().parents[1]
_PROJECT = _BACKEND.parent
REPORTS_DIR = str(_PROJECT / "reports")
QA_ALLOWED = frozenset({
    "qa_publico_vs_privado.csv",
    "qa_ambulatorial_vazando.csv",
    "qa_maternidade_nao_marcada.csv",
})


def _admin_allowed():
    fn = getattr(current_app, "_admin_allowed", None)
    if fn is not None:
        return fn()
    return False, ("disabled", 404)


def _parse_bool_emergency(s):
    if s is None:
        return None
    s = str(s).strip().lower()
    if s in ("true", "1", "sim", "yes", "y"):
        return True
    if s in ("false", "0", "nao", "não", "no", "n"):
        return False
    return None


def _sanitize_json_nan(obj):
    if isinstance(obj, dict):
        return {k: _sanitize_json_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_json_nan(v) for v in obj]
    if isinstance(obj, float) and obj != obj:
        return None
    return obj


def _read_run_summary_json():
    p = _PROJECT / "reports" / "run_summary.json"
    if not p.is_file():
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _dataset_info_health():
    geo_path = _PROJECT / "data" / "geo" / "hospitals_geo.parquet"
    ready_path = _PROJECT / "data" / "geo" / "hospitals_ready.parquet"
    p = geo_path if geo_path.is_file() else ready_path
    if not p.is_file():
        return {"present": False}
    try:
        mtime = os.path.getmtime(str(p))
        from backend.api.routes import load_geo_df
        df = load_geo_df()
        rows = len(df) if df is not None else None
        return {"present": True, "rows": rows, "path": str(p), "mtime": mtime}
    except Exception:
        return {"present": False}


# ---------- Facilities ----------
@health_bp.route('/api/v1/facilities/search', methods=['POST', 'OPTIONS'])
def api_search_facilities():
    try:
        if request.method == 'OPTIONS':
            r = Response()
            r.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            r.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            r.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            r.headers['Access-Control-Allow-Credentials'] = 'true'
            return r
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos', 'message': 'Corpo da requisição deve ser JSON válido'}), 400
        latitude = float(data.get('latitude', 0))
        longitude = float(data.get('longitude', 0))
        radius_km = float(data.get('radius_km', 10.0))
        filter_type = data.get('filter_type', 'ALL')
        is_emergency = bool(data.get('is_emergency', False))
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({'error': 'Coordenadas inválidas', 'message': 'Latitude deve estar entre -90 e 90, Longitude entre -180 e 180'}), 400
        try:
            from backend.services.facility_service import FacilityService
        except ImportError:
            from services.facility_service import FacilityService
        facility_service = FacilityService()
        results, data_source_date, is_cache_fallback = facility_service.search_facilities(
            latitude=latitude, longitude=longitude, radius_km=radius_km,
            filter_type=filter_type, is_emergency=is_emergency
        )
        legal_disclaimer = (
            "⚠️ Aviso de Emergência: Em caso de risco imediato à vida da mãe ou do bebê "
            "(sangramento intenso, perda de consciência, convulsão), dirija-se ao Pronto Socorro "
            "mais próximo, seja ele público ou privado. A Lei Federal obriga o atendimento de "
            "emergência para estabilização, independente de convênio ou capacidade de pagamento. "
            "Não aguarde validação do aplicativo em situações críticas."
        )
        if is_cache_fallback and data_source_date:
            legal_disclaimer += (
                f"\n\n⚠️ Dados baseados no registro oficial de {data_source_date}. "
                "API CNES está offline. Confirme informações por telefone."
            )
        return jsonify({
            'meta': {'legal_disclaimer': legal_disclaimer, 'total_results': len(results),
                     'data_source_date': data_source_date, 'is_cache_fallback': is_cache_fallback},
            'results': results
        }), 200
    except FileNotFoundError as e:
        current_app.logger.error("[FACILITIES] Banco não encontrado: %s", e)
        return jsonify({'error': 'Serviço temporariamente indisponível', 'message': 'Banco de dados CNES não foi inicializado.'}), 503
    except ValueError as e:
        return jsonify({'error': 'Erro de validação', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error("[FACILITIES] Erro: %s", e, exc_info=True)
        return jsonify({'error': 'Erro interno', 'message': 'Tente novamente ou ligue 192 em caso de emergência.'}), 500


# ---------- Emergency search ----------
@health_bp.route('/api/v1/emergency/search', methods=['GET', 'OPTIONS'])
def api_emergency_search():
    if request.method == 'OPTIONS':
        r = Response()
        r.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        r.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        r.headers['Access-Control-Allow-Headers'] = 'Accept'
        return r
    try:
        try:
            lat = float(request.args.get('lat'))
            lon = float(request.args.get('lon'))
        except (TypeError, ValueError):
            return jsonify({'error': 'missing_or_invalid_lat_lon'}), 400
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({'error': 'Coordenadas inválidas'}), 400
        radius_km = float(request.args.get('radius_km', 25))
        radius_km = min(50.0, max(0.1, radius_km))  # Limite máximo 50 km no backend
        user_id = str(current_user.id) if getattr(current_user, 'is_authenticated', False) else session.get('user_id', 'anon')
        current_app.logger.info("[LOGIN] Usuário %s acessando de: %s, %s", user_id, lat, lon)
        print("[LOGIN] Usuário {} acessando de: {}, {}".format(user_id, lat, lon))
        expand = _parse_bool_emergency(request.args.get('expand'))
        expand = True if expand is None else bool(expand)
        limit = int(request.args.get('limit', 10))
        min_results = int(request.args.get('min_results', 3))
        sus = _parse_bool_emergency(request.args.get('sus'))
        debug = _parse_bool_emergency(request.args.get('debug')) is True
        try:
            from backend.api.routes import load_geo_df, geo_v2_search_core
        except ImportError:
            from api.routes import load_geo_df, geo_v2_search_core
        import pandas as pd
        df = load_geo_df()
        if df is None:
            return jsonify({'results': [], 'banner_192': False, 'generated_at': pd.Timestamp.utcnow().isoformat(), 'error': 'dataset_geografico_indisponivel'}), 503
        out = geo_v2_search_core(df, lat, lon, sus, radius_km, expand, limit, min_results)
        results = out[0] if len(out) > 0 else []
        banner = out[1] if len(out) > 1 else False
        meta = out[2] if len(out) > 2 else None
        nearby_confirmed = out[3] if len(out) > 3 else []
        try:
            from backend.api.routes import _normalize_esfera
        except ImportError:
            from api.routes import _normalize_esfera
        for r in results:
            esfera_val = r.get("esfera")
            if esfera_val:
                esfera_str = str(esfera_val).strip()
                if esfera_str.lower() == "desconhecido" or esfera_str not in ("Público", "Privado", "Filantrópico"):
                    r["esfera"] = _normalize_esfera(esfera_str, r.get("nome")) or "Privado"
        for r in nearby_confirmed:
            esfera_val = r.get("esfera")
            if esfera_val:
                esfera_str = str(esfera_val).strip()
                if esfera_str.lower() == "desconhecido" or esfera_str not in ("Público", "Privado", "Filantrópico"):
                    r["esfera"] = _normalize_esfera(esfera_str, r.get("nome")) or "Privado"
        body = {
            'results': results[:limit] if results else [],
            'nearby_confirmed': nearby_confirmed if nearby_confirmed else [],
            'banner_192': bool(banner),
            'generated_at': pd.Timestamp.utcnow().isoformat()
        }
        if debug and meta:
            body['debug'] = meta
        body = _sanitize_json_nan(body)
        resp = jsonify(body)
        resp.headers['X-Data-Count'] = str(len(body.get('results', [])))
        resp.headers['X-Query-Lat'] = str(lat)
        resp.headers['X-Query-Lon'] = str(lon)
        resp.headers['X-Query-Radius'] = str(radius_km)
        try:
            from backend.api.routes import get_geo_data_info
        except ImportError:
            from api.routes import get_geo_data_info
        try:
            info = get_geo_data_info()
            if isinstance(info, dict):
                src, mtime = info.get("source_path") or info.get("source"), info.get("mtime")
            elif isinstance(info, (tuple, list)) and len(info) >= 2:
                src, mtime = info[0], info[1]
            else:
                src, mtime = None, None
            if src:
                resp.headers['X-Data-Source'] = str(src)
            if mtime is not None:
                resp.headers['X-Data-Mtime'] = str(int(mtime))
        except Exception:
            pass
        try:
            logs_dir = _PROJECT / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            event = {"ts": pd.Timestamp.utcnow().isoformat(), "lat": lat, "lon": lon, "radius_requested": radius_km,
                     "radius_used": meta.get("radius_used") if meta else None, "expanded": meta.get("expanded") if meta else False,
                     "found_A": meta.get("found_A", 0) if meta else 0, "found_B": meta.get("found_B", 0) if meta else 0,
                     "banner_192": bool(banner), "sus": sus}
            with open(logs_dir / "search_events.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception:
            pass
        return resp
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error("[EMERGENCY] Erro: %s", e, exc_info=True)
        return jsonify({'error': 'Erro ao processar busca. Ligue 192 em caso de emergência.'}), 500


@health_bp.route('/api/v1/emergency/reload', methods=['POST'])
def api_emergency_reload():
    try:
        from backend.api.routes import refresh_geo_cache
    except ImportError:
        from api.routes import refresh_geo_cache
    ok, rows, err = refresh_geo_cache()
    if not ok:
        return jsonify({'ok': False, 'error': err or 'Falha ao recarregar cache'}), 500
    return jsonify({'ok': True, 'rows': rows})


# ---------- Helpers: emergency health details ----------
def _emergency_health_details():
    """Detalhes da base geo (count, source, mtime, ttl)."""
    out = {"status": "ok"}
    info = None
    try:
        from backend.api.geo_info import get_geo_data_info as _get_info
        info = _get_info()
    except Exception:
        info = None
    if info is None:
        try:
            from backend.api.routes import get_geo_data_info as _get_info
            info = _get_info()
        except Exception:
            info = None
    if isinstance(info, dict):
        source_path = info.get("source_path") or info.get("source") or ""
        mtime = info.get("mtime") or info.get("mtime_ts") or None
        count = info.get("count") or None
        loaded_at = info.get("loaded_at") or None
        ttl_seconds = info.get("ttl_seconds") or None
        ttl_remaining = info.get("ttl_remaining") or None
        out.update({
            "count": int(count) if isinstance(count, (int, float)) else None,
            "source": source_path or None,
            "mtime": int(mtime) if isinstance(mtime, (int, float)) else None,
            "mtime_iso": datetime.utcfromtimestamp(int(mtime)).isoformat() + "Z" if isinstance(mtime, (int, float)) else None,
            "loaded_at": int(loaded_at) if isinstance(loaded_at, (int, float)) else None,
            "ttl_seconds": int(ttl_seconds) if isinstance(ttl_seconds, (int, float)) else None,
            "ttl_remaining": int(ttl_remaining) if isinstance(ttl_remaining, (int, float)) else None,
        })
    elif isinstance(info, (tuple, list)) and len(info) >= 2:
        source_path, mtime = info[0], info[1]
        out.update({
            "source": source_path or None,
            "mtime": int(mtime) if isinstance(mtime, (int, float)) else None,
            "mtime_iso": datetime.utcfromtimestamp(int(mtime)).isoformat() + "Z" if isinstance(mtime, (int, float)) else None,
        })
    return out


def _evaluate_emergency_health(details):
    """Regras: EMERGENCY_HEALTH_MIN_COUNT, EMERGENCY_HEALTH_MAX_AGE_HOURS. Retorna (status, reason)."""
    try:
        min_count = int(os.environ.get("EMERGENCY_HEALTH_MIN_COUNT", "0"))
    except Exception:
        min_count = 0
    try:
        max_age_h = float(os.environ.get("EMERGENCY_HEALTH_MAX_AGE_HOURS", "0"))
    except Exception:
        max_age_h = 0.0
    count = details.get("count")
    if isinstance(count, (int, float)) and min_count > 0 and count < min_count:
        return "degraded", f"count<{min_count}"
    ts = None
    if isinstance(details.get("loaded_at"), (int, float)):
        ts = int(details["loaded_at"])
    elif isinstance(details.get("mtime"), (int, float)):
        ts = int(details["mtime"])
    if ts and max_age_h > 0:
        age = time.time() - ts
        if age > (max_age_h * 3600.0):
            return "stale", f"age>{max_age_h}h"
    return "ok", None


# ---------- Health ----------
@health_bp.route('/api/v1/health', methods=['GET'])
def api_v1_health():
    """Health: dataset, geo_health, search_metrics e perf (se PERF_EXPOSE=on)."""
    rs = _read_run_summary_json() or {}
    meta = {
        "status": "ok",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "dataset": _dataset_info_health(),
        "geo_health": rs.get("geo_health"),
        "search_metrics": rs.get("search_metrics"),
        "version": "sophia-emergency-v2",
    }
    perf_expose = os.environ.get("PERF_EXPOSE", "").strip().lower() in ("1", "true", "on")
    if perf_expose:
        ovr = {}
        try:
            from backend.startup.cnes_overrides import get_overrides_count, get_snapshot_used
            ovr = {
                "boot_ms": getattr(current_app, "_perf_ovr_boot_ms", None),
                "boot_at": getattr(current_app, "_perf_ovr_boot_at", None),
                "snapshot": get_snapshot_used(),
                "count": get_overrides_count(),
                "mode": os.getenv("OVERRIDES_BOOT", "lazy"),
            }
        except Exception:
            ovr = {"mode": os.getenv("OVERRIDES_BOOT", "lazy")}
        meta["perf"] = {
            "startup_ms": getattr(current_app, "_perf_import_ms", None),
            "first_request_ms": getattr(current_app, "_perf_first_req_ms", None),
            "first_request_at": getattr(current_app, "_perf_first_req_at", None),
            "overrides": ovr,
        }
    return jsonify(meta), 200


@health_bp.route('/api/v1/health/short', methods=['GET'])
def api_v1_health_short():
    """Health curto para LB/probe."""
    try:
        info = _dataset_info_health()
    except Exception:
        info = {"present": False}
    return jsonify({
        "status": "ok",
        "dataset": {"present": bool(info.get("present"))},
        "version": "sophia-emergency-v2",
    }), 200


@health_bp.route("/api/v1/emergency/health", methods=["GET"])
def emergency_health():
    """Health básico da base de emergência (status ok/degraded/stale)."""
    try:
        details = _emergency_health_details()
        status, reason = _evaluate_emergency_health(details)
        details["status"] = status
        if status == "ok":
            return jsonify(details), 200
        details["reason"] = reason
        return jsonify(details), 503
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@health_bp.route("/api/v1/emergency/health/details", methods=["GET"])
def emergency_health_details():
    """Detalhes da base de emergência (count, source, mtime)."""
    try:
        details = _emergency_health_details()
        status, reason = _evaluate_emergency_health(details)
        details["status"] = status
        if status != "ok":
            details["reason"] = reason
        return jsonify(details), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ---------- Debug (admin) ----------
@health_bp.route('/api/v1/debug/overrides/coverage', methods=['GET'])
def api_v1_debug_overrides_coverage():
    ok, err = _admin_allowed()
    if not ok:
        msg, code = err if err else ("disabled", 404)
        return jsonify({"ok": False, "error": msg}), code
    try:
        from backend.startup.cnes_overrides import get_snapshot_used, get_overrides_count
        return jsonify({
            "total_loaded": get_overrides_count(),
            "snapshot_usado": get_snapshot_used(),
        }), 200
    except Exception as e:
        return jsonify({"total_loaded": 0, "snapshot_usado": None, "error": str(e)}), 200


@health_bp.route('/api/v1/debug/overrides/refresh', methods=['POST'])
def api_v1_debug_overrides_refresh():
    ok, err = _admin_allowed()
    if not ok:
        msg, code = err if err else ("disabled", 404)
        return jsonify({"ok": False, "error": msg}), code
    try:
        from backend.startup.cnes_overrides import boot as ovr_boot, get_snapshot_used, get_overrides_count
        snap = os.getenv("SNAPSHOT", "202512")
        ovr_boot(snap, force=True)
        return jsonify({"ok": True, "snapshot": get_snapshot_used(), "count": get_overrides_count()}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@health_bp.route('/api/v1/debug/geo/refresh', methods=['POST'])
def api_v1_debug_geo_refresh():
    ok, err = _admin_allowed()
    if not ok:
        msg, code = err if err else ("disabled", 404)
        return jsonify({"ok": False, "error": msg}), code
    try:
        from backend.api.routes import refresh_geo_cache
        ok, rows, error = refresh_geo_cache()
        if ok:
            return jsonify({"ok": True, "rows": rows}), 200
        return jsonify({"ok": False, "error": error}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@health_bp.route('/api/v1/debug/overrides/quick_check', methods=['GET'])
def api_v1_debug_overrides_quick_check():
    ok, err = _admin_allowed()
    if not ok:
        msg, code = err if err else ("disabled", 404)
        return jsonify({"ok": False, "error": msg}), code
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
        radius_km = float(request.args.get("radius_km", 25))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "lat/lon inválidos"}), 400
    try:
        from backend.api.routes import load_geo_df, haversine_km
        from backend.startup.cnes_overrides import has_cnes
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 503
    df = load_geo_df()
    if df is None:
        return jsonify({"ok": False, "error": "dataset indisponível"}), 503
    df = df[(df["lat"].notna()) & (df["lon"].notna())].copy()
    if "cnes_id" not in df.columns and "CNES" in df.columns:
        df = df.rename(columns={"CNES": "cnes_id"})
    if "cnes_id" not in df.columns:
        return jsonify({"ok": False, "error": "coluna cnes_id não encontrada"}), 503
    df["dist_km"] = df.apply(
        lambda r: haversine_km(lat, lon, float(r["lat"]), float(r["lon"])),
        axis=1,
    )
    pool = df[df["dist_km"] <= radius_km].head(30)
    total = len(pool)
    hits = sum(1 for _, r in pool.iterrows() if has_cnes(str(r.get("cnes_id", ""))))
    coverage_pct = (hits / total) if total else None
    return jsonify({
        "ok": True,
        "total": total,
        "override_hits": hits,
        "coverage_pct": round(coverage_pct, 4) if coverage_pct is not None else None,
    }), 200


@health_bp.route('/api/v1/debug/qa/list', methods=['GET'])
def api_v1_debug_qa_list():
    ok, err = _admin_allowed()
    if not ok:
        msg, code = err if err else ("disabled", 404)
        return jsonify({"ok": False, "error": msg}), code
    files = []
    for name in sorted(QA_ALLOWED):
        p = os.path.join(REPORTS_DIR, name)
        if os.path.isfile(p):
            try:
                st = os.stat(p)
                files.append({
                    "name": name,
                    "size": st.st_size,
                    "mtime": int(st.st_mtime),
                    "url": f"/api/v1/debug/qa/download?name={name}",
                })
            except Exception:
                pass
    return jsonify({"ok": True, "files": files}), 200


@health_bp.route('/api/v1/debug/qa/download', methods=['GET'])
def api_v1_debug_qa_download():
    ok, err = _admin_allowed()
    if not ok:
        msg, code = err if err else ("disabled", 404)
        return jsonify({"ok": False, "error": msg}), code
    name = (request.args.get("name") or "").strip()
    if name not in QA_ALLOWED:
        return jsonify({"ok": False, "error": "arquivo inválido"}), 400
    p = os.path.join(REPORTS_DIR, name)
    if not os.path.isfile(p):
        return jsonify({"ok": False, "error": "não encontrado"}), 404
    from flask import send_from_directory
    return send_from_directory(REPORTS_DIR, name, as_attachment=True)


# ---------- Vacinas estáticas ----------
@health_bp.route('/api/vacinas/mae')
def api_vacinas_mae():
    vacinas = getattr(current_app, "vacinas_mae", [])
    return jsonify(vacinas)


@health_bp.route('/api/vacinas/bebe')
def api_vacinas_bebe():
    vacinas = getattr(current_app, "vacinas_bebe", [])
    return jsonify(vacinas)


def _db_path():
    return current_app.config.get("DB_PATH", "")


# ---------- Vacinas status / marcar / desmarcar ----------
@health_bp.route('/api/vacinas/status', methods=['GET'])
@login_required
def api_vacinas_status():
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT tipo, vacina_nome, data_tomada FROM vacinas_tomadas WHERE user_id = ?', (current_user.id,))
    vacinas = cursor.fetchall()
    conn.close()
    status = {}
    for vacina in vacinas:
        tipo = vacina[0]
        if tipo not in status:
            status[tipo] = []
        status[tipo].append({"nome": vacina[1], "data": vacina[2]})
    return jsonify(status)


@health_bp.route('/api/vacinas/marcar', methods=['POST'])
@login_required
def api_vacinas_marcar():
    data = request.get_json()
    tipo = (data.get('tipo') or '').strip()
    vacina_nome = (data.get('vacina_nome') or '').strip()
    if not tipo or not vacina_nome:
        return jsonify({"erro": "Tipo e nome da vacina são obrigatórios"}), 400
    if tipo not in ('mae', 'bebe'):
        return jsonify({"erro": "Tipo deve ser 'mae' ou 'bebe'"}), 400
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM vacinas_tomadas WHERE user_id = ? AND tipo = ? AND vacina_nome = ?',
                   (current_user.id, tipo, vacina_nome))
    if cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Esta vacina já foi marcada"}), 400
        # baby_name do banco para saudações personalizadas (ex.: "Parabéns, Petronio!")
    cursor.execute('SELECT name, baby_name FROM users WHERE id = ?', (current_user.id,))
    user_data = cursor.fetchone()
    user_name = user_data[0] if user_data else current_user.name
    baby_name = user_data[1] if user_data and user_data[1] else None
    cursor.execute('INSERT INTO vacinas_tomadas (user_id, tipo, vacina_nome) VALUES (?, ?, ?)',
                   (current_user.id, tipo, vacina_nome))
    conn.commit()
    vacina_id = cursor.lastrowid
    conn.close()
    if tipo == 'bebe' and baby_name:
        mensagem = f"Vacina marcada com sucesso! Parabéns, {baby_name}! E parabéns para você também, {user_name}! 💉✨🎉"
    elif tipo == 'bebe':
        mensagem = "Vacina marcada com sucesso! Parabéns para você e seu bebê! 💉✨🎉"
    else:
        mensagem = f"Vacina marcada com sucesso! Parabéns, {user_name}! 💉✨"
    return jsonify({
        "sucesso": True, "mensagem": mensagem, "vacina_id": vacina_id,
        "tipo": tipo, "baby_name": baby_name, "user_name": user_name
    }), 201


@health_bp.route('/api/vacinas/desmarcar', methods=['POST'])
@login_required
def api_vacinas_desmarcar():
    data = request.get_json()
    tipo = (data.get('tipo') or '').strip()
    vacina_nome = (data.get('vacina_nome') or '').strip()
    if not tipo or not vacina_nome:
        return jsonify({"erro": "Tipo e nome da vacina são obrigatórios"}), 400
    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vacinas_tomadas WHERE user_id = ? AND tipo = ? AND vacina_nome = ?',
                   (current_user.id, tipo, vacina_nome))
    conn.commit()
    conn.close()
    return jsonify({"sucesso": True, "mensagem": "Vacina removida"})


# ---------- Baby profile ----------
@health_bp.route('/api/baby_profile', methods=['POST'])
@login_required
def api_create_baby_profile():
    try:
        try:
            from backend.services.vaccination_service import VaccinationService
        except ImportError:
            from services.vaccination_service import VaccinationService
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        name = (data.get('name') or '').strip()
        birth_date = (data.get('birth_date') or '').strip()
        gender = data.get('gender')
        if not name:
            return jsonify({'error': 'Nome do bebê é obrigatório'}), 400
        if not birth_date:
            return jsonify({'error': 'Data de nascimento é obrigatória'}), 400
        try:
            datetime.strptime(birth_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Data de nascimento inválida. Use o formato YYYY-MM-DD'}), 400
        conn = sqlite3.connect(_db_path())
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM baby_profiles WHERE user_id = ? LIMIT 1', (int(current_user.id),))
        existing_profile = cursor.fetchone()
        conn.close()
        if existing_profile:
            return jsonify({
                'error': 'Você já possui um perfil de bebê cadastrado',
                'message': 'Cada usuário pode ter apenas um perfil de bebê por enquanto.'
            }), 400
        try:
            vaccination_service = VaccinationService(_db_path())
            baby_profile_id = vaccination_service.create_baby_profile(
                user_id=int(current_user.id), name=name, birth_date=birth_date, gender=gender
            )
            current_app.logger.info("[BABY_PROFILE] Perfil criado: ID=%s, Nome=%s, User=%s", baby_profile_id, name, current_user.id)
            return jsonify({
                'success': True,
                'message': 'Perfil do bebê criado com sucesso! O calendário de vacinação foi gerado automaticamente.',
                'baby_profile_id': baby_profile_id
            }), 201
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as service_err:
            current_app.logger.error("[BABY_PROFILE] Erro ao criar perfil: %s", service_err, exc_info=True)
            return jsonify({'error': 'Erro ao criar perfil do bebê', 'message': str(service_err)}), 500
    except Exception as e:
        current_app.logger.error("[BABY_PROFILE] Erro inesperado: %s", e, exc_info=True)
        return jsonify({'error': 'Erro inesperado', 'message': str(e)}), 500


@health_bp.route('/api/baby_profile', methods=['GET'])
def api_get_baby_profile():
    try:
        if not (getattr(current_user, 'is_authenticated', False)):
            return jsonify({'exists': False, 'message': 'Usuário não autenticado'}), 200
        try:
            conn = sqlite3.connect(_db_path())
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, name, birth_date, gender, created_at FROM baby_profiles WHERE user_id = ? LIMIT 1',
                (int(current_user.id),))
            baby_profile = cursor.fetchone()
            conn.close()
            if not baby_profile:
                return jsonify({'exists': False}), 200
            return jsonify({
                'exists': True, 'id': baby_profile[0], 'name': baby_profile[1],
                'birth_date': baby_profile[2], 'gender': baby_profile[3], 'created_at': baby_profile[4]
            }), 200
        except Exception as db_err:
            current_app.logger.error("[BABY_PROFILE] Erro DB: %s", db_err, exc_info=True)
            return jsonify({'exists': False, 'error': 'Erro ao buscar perfil do bebê', 'message': str(db_err)}), 200
    except Exception as e:
        current_app.logger.error("[BABY_PROFILE] Erro: %s", e, exc_info=True)
        return jsonify({'exists': False, 'error': 'Erro ao buscar perfil do bebê', 'message': str(e)}), 200


# ---------- Vaccination (agenda interativa) ----------
@health_bp.route('/api/vaccination/status', methods=['GET'])
def api_vaccination_status():
    try:
        if not (getattr(current_user, 'is_authenticated', False)):
            return jsonify({
                'status': 'ok', 'message': 'Usuário não autenticado',
                'vaccines': [], 'baby_profile_exists': False
            }), 200
        try:
            from backend.services.vaccination_service import VaccinationService
        except ImportError:
            from services.vaccination_service import VaccinationService
        conn = None
        try:
            conn = sqlite3.connect(_db_path())
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM baby_profiles WHERE user_id = ? LIMIT 1', (int(current_user.id),))
            baby_profile = cursor.fetchone()
        except Exception as db_err:
            current_app.logger.error("[VACCINATION] Erro ao buscar perfil: %s", db_err, exc_info=True)
            return jsonify({'status': 'ok', 'message': 'Erro ao buscar perfil do bebê', 'vaccines': [], 'baby_profile_exists': False}), 200
        finally:
            if conn:
                conn.close()
        if not baby_profile:
            return jsonify({'status': 'ok', 'message': 'Nenhum perfil de bebê encontrado', 'vaccines': [], 'baby_profile_exists': False}), 200
        baby_profile_id = baby_profile[0]
        try:
            vaccination_service = VaccinationService(_db_path())
            status = vaccination_service.get_vaccination_status(baby_profile_id)
            if not status:
                return jsonify({'status': 'ok', 'message': 'Erro ao buscar status de vacinação', 'vaccines': [], 'baby_profile_exists': True}), 200
            return jsonify(status), 200
        except Exception as service_err:
            current_app.logger.error("[VACCINATION] Erro service: %s", service_err, exc_info=True)
            return jsonify({'status': 'ok', 'message': 'Erro ao processar dados de vacinação', 'vaccines': [], 'baby_profile_exists': True}), 200
    except Exception as e:
        current_app.logger.error("[VACCINATION] Erro: %s", e, exc_info=True)
        return jsonify({'status': 'ok', 'message': 'Erro inesperado', 'vaccines': [], 'baby_profile_exists': False}), 200


@health_bp.route('/api/vaccination/mark-done', methods=['POST'])
@login_required
def api_vaccination_mark_done():
    try:
        try:
            from backend.services.vaccination_service import VaccinationService
        except ImportError:
            from services.vaccination_service import VaccinationService
        data = request.get_json()
        schedule_id = data.get('schedule_id')
        administered_date = data.get('administered_date')
        administered_location = data.get('administered_location')
        administered_by = data.get('administered_by')
        lot_number = data.get('lot_number')
        notes = data.get('notes')
        if not schedule_id:
            return jsonify({'error': 'schedule_id é obrigatório'}), 400
        conn = sqlite3.connect(_db_path())
        cursor = conn.cursor()
        cursor.execute('''
            SELECT vs.id FROM vaccination_schedule vs
            JOIN baby_profiles bp ON vs.baby_profile_id = bp.id
            WHERE vs.id = ? AND bp.user_id = ?
        ''', (schedule_id, int(current_user.id)))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Agendamento não encontrado ou não pertence ao usuário'}), 404
        cursor.execute(
            'SELECT u.name, u.baby_name FROM users u '
            'JOIN baby_profiles bp ON bp.user_id = u.id '
            'JOIN vaccination_schedule vs ON vs.baby_profile_id = bp.id WHERE vs.id = ?',
            (schedule_id,)
        )
        row = cursor.fetchone()
        user_name = row[0] if row else getattr(current_user, 'name', None)
        baby_name = row[1] if row and len(row) > 1 and row[1] else None
        conn.close()
        vaccination_service = VaccinationService(_db_path())
        success = vaccination_service.mark_vaccine_done(
            schedule_id=schedule_id, administered_date=administered_date,
            administered_location=administered_location, administered_by=administered_by,
            lot_number=lot_number, notes=notes
        )
        if success:
            return jsonify({
                'success': True,
                'message': 'Vacina marcada como aplicada com sucesso! 💉✨',
                'user_name': user_name,
                'baby_name': baby_name,
            }), 200
        return jsonify({'error': 'Erro ao marcar vacina como aplicada'}), 500
    except Exception as e:
        current_app.logger.error("Erro ao marcar vacina: %s", e, exc_info=True)
        return jsonify({'error': f'Erro: {str(e)}'}), 500


# ---------- Lembretes de vacinação (Agenda de Vacinação - adicionar lembrete) ----------
def _ensure_reminders_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vaccination_reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vacina TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            local TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


@health_bp.route('/api/v1/vaccination/add', methods=['POST'])
@login_required
def api_vaccination_add():
    """Adiciona um lembrete de vacinação (Vacina, Data, Hora, Local)."""
    try:
        data = request.get_json() or {}
        vacina = (data.get('vacina') or '').strip()
        data_str = (data.get('data') or '').strip()
        hora = (data.get('hora') or '').strip()
        local = (data.get('local') or '').strip()
        if not vacina:
            return jsonify({'error': 'Campo vacina é obrigatório'}), 400
        if not data_str:
            return jsonify({'error': 'Campo data é obrigatório'}), 400
        db_path = _db_path()
        if not db_path:
            return jsonify({'error': 'Banco de dados não configurado'}), 503
        conn = sqlite3.connect(db_path)
        try:
            _ensure_reminders_table(conn)
            conn.execute(
                'INSERT INTO vaccination_reminders (user_id, vacina, data, hora, local) VALUES (?, ?, ?, ?, ?)',
                (int(current_user.id), vacina, data_str, hora, local)
            )
            conn.commit()
            row_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            return jsonify({
                'success': True,
                'message': 'Lembrete adicionado à agenda.',
                'id': row_id,
                'vacina': vacina,
                'data': data_str,
                'hora': hora,
                'local': local,
            }), 201
        finally:
            conn.close()
    except Exception as e:
        current_app.logger.error("Erro ao adicionar lembrete de vacinação: %s", e, exc_info=True)
        return jsonify({'error': 'Erro ao salvar lembrete', 'message': str(e)}), 500


@health_bp.route('/api/v1/vaccination/reminders', methods=['GET'])
@login_required
def api_vaccination_reminders():
    """Lista os lembretes de vacinação do usuário. Retorna upcoming (data >= hoje) e taken (arquivados: data < hoje)."""
    try:
        db_path = _db_path()
        if not db_path:
            return jsonify({'upcoming': [], 'taken': []}), 200
        conn = sqlite3.connect(db_path)
        try:
            _ensure_reminders_table(conn)
            rows = conn.execute(
                'SELECT id, vacina, data, hora, local, created_at FROM vaccination_reminders WHERE user_id = ? ORDER BY data ASC, hora ASC',
                (int(current_user.id),)
            ).fetchall()
            today = datetime.utcnow().date().isoformat()
            upcoming = []
            taken = []
            for r in rows:
                item = {'id': r[0], 'vacina': r[1], 'data': r[2], 'hora': r[3], 'local': r[4], 'created_at': r[5]}
                if (r[2] or '') >= today:
                    upcoming.append(item)
                else:
                    taken.append(item)
            return jsonify({'upcoming': upcoming, 'taken': taken}), 200
        finally:
            conn.close()
    except Exception as e:
        current_app.logger.error("Erro ao listar lembretes: %s", e, exc_info=True)
        return jsonify({'upcoming': [], 'taken': []}), 200
