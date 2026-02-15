# -*- coding: utf-8 -*-
"""
Blueprint: Cards educativos e página /conteudos.
Rotas: /api/educational, /conteudos.
"""
import os
from flask import Blueprint, jsonify, redirect, url_for, current_app

edu_bp = Blueprint("edu", __name__)


@edu_bp.route("/conteudos")
def conteudos_page():
    """Redireciona para a home na âncora da seção (página removida por decisão de produto)."""
    try:
        if "index" in current_app.view_functions:
            return redirect(url_for("index") + "#conteudos", code=302)
    except Exception:
        pass
    return redirect("/#conteudos", code=302)


@edu_bp.route("/api/educational", methods=["GET"])
def api_educational():
    try:
        from backend.utils.educational import load_educational_items
        _backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.environ.get(
            "EDU_JSON_PATH",
            os.path.join(_backend, "static", "data", "educational.json")
        )
        items = load_educational_items(json_path)
    except Exception:
        items = []
        json_path = None
    if not items:
        items = [
            {
                "id": "card-cancer-mama-welcome",
                "title": "Saúde Preventiva",
                "subtitle": "Câncer de Mama",
                "url": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/c/cancer-de-mama",
                "read_min": 4,
                "icon": "ribbon",
            },
            {
                "id": "card-doacao-leite-welcome",
                "title": "Rede de Apoio",
                "subtitle": "Doação de Leite",
                "url": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/d/doacao-de-leite",
                "read_min": 3,
                "icon": "bottles",
            },
        ]
    resp = jsonify({"items": items, "count": len(items)})
    try:
        if json_path and os.path.exists(json_path):
            st = os.stat(json_path)
            etag = f'{int(st.st_mtime)}-{st.st_size}'
            resp.headers["ETag"] = etag
            resp.headers["Cache-Control"] = "public, max-age=60"
        else:
            resp.headers["Cache-Control"] = "no-cache"
    except Exception:
        resp.headers["Cache-Control"] = "no-cache"
    return resp
