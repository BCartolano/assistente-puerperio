# -*- coding: utf-8 -*-
import os
import json
import time
import uuid
from flask import Blueprint, request, jsonify, session, current_app, render_template, redirect, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from backend.utils.tokens import sign_token, verify_token
from backend.utils.mail import send_email

auth_bp = Blueprint("auth", __name__)

_bd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_PATH = os.path.join(_bd, "static", "data", "users.json")


def _load_users():
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "users" in data:
            return data
        elif isinstance(data, list):
            return {"users": data}
    except Exception:
        pass
    return {"users": []}


def _save_users(data):
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _find_user_by_email(users, email):
    e = (email or "").strip().lower()
    for u in users:
        if (u.get("email") or "").lower() == e:
            return u
    return None


def _find_user_by_id(users, uid):
    for u in users:
        if u.get("id") == uid:
            return u
    return None


def _verification_link(token):
    base = os.environ.get("FRONTEND_BASE_URL") or request.url_root.rstrip("/")
    return f"{base}/api/verify?token={token}"


def _reset_link(token):
    base = os.environ.get("FRONTEND_BASE_URL") or request.url_root.rstrip("/")
    return f"{base}/reset-password?token={token}"


# DESABILITADO: /api/register é tratado por app.py usando SQLite (users.db)
# O auth blueprint usava users.json; removido para evitar conflito.
# @auth_bp.route("/api/register", methods=["POST"])
# def api_register(): ...


@auth_bp.route("/api/verify", methods=["GET"])
def api_verify():
    token = request.args.get("token", "")
    payload = verify_token(token, current_app.config.get("SECRET_KEY", "dev"))
    if not payload or payload.get("purpose") != "verify":
        return render_template("errors/404.html"), 400
    data = _load_users()
    user = _find_user_by_id(data["users"], payload.get("uid"))
    if not user or (user.get("email") or "").lower() != (payload.get("email") or "").lower():
        return render_template("errors/404.html"), 400
    user["verified"] = True
    _save_users(data)
    session["user_id"] = user["id"]
    r = redirect("/")
    r.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Vary"] = "Cookie"
    return r


# DESABILITADO: Esta rota está conflitando com a implementação em app.py que usa SQLite/bcrypt
# A rota /api/login agora é gerenciada diretamente em backend/app.py (linha 5989)
# @auth_bp.route("/api/login", methods=["POST"])
# def api_login():
#     try:
#         payload = request.get_json(force=True) or {}
#     except Exception:
#         payload = {}
#     email = (payload.get("email") or "").strip().lower()
#     password = payload.get("password") or ""
#     data = _load_users()
#     user = _find_user_by_email(data["users"], email)
#     if not user or not check_password_hash(user.get("password_hash", ""), password):
#         return jsonify({"ok": False, "error": "invalid_credentials"}), 401
#     if not user.get("verified"):
#         secret = current_app.config.get("SECRET_KEY", "dev")
#         token = sign_token({"uid": user["id"], "email": email, "purpose": "verify"}, secret, expires_sec=3 * 24 * 3600)
#         link = _verification_link(token)
#         html = render_template("email/verify.html", name=user["name"], link=link)
#         text = render_template("email/verify.txt", name=user["name"], link=link)
#         send_email("Confirme seu cadastro", email, html=html, text=text)
#         return jsonify({"ok": False, "error": "unverified", "resent": True}), 403
#     session["user_id"] = user["id"]
#     resp = make_response(jsonify({"ok": True, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}), 200)
#     resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
#     resp.headers["Pragma"] = "no-cache"
#     resp.headers["Vary"] = "Cookie"
#     return resp


@auth_bp.route("/api/logout", methods=["POST"])
def api_logout():
    try:
        session.pop("user_id", None)
    except Exception:
        pass
    resp = make_response(jsonify({"ok": True}), 200)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Vary"] = "Cookie"
    return resp


@auth_bp.route("/api/me", methods=["GET"])
def api_me():
    uid = session.get("user_id")
    if not uid:
        resp = make_response(jsonify({}), 200)
    else:
        data = _load_users()
        user = _find_user_by_id(data["users"], uid)
        payload = {} if not user else {
            "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
            "verified": bool(user.get("verified"))
        }
        resp = make_response(jsonify(payload), 200)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Vary"] = "Cookie"
    return resp


# ---------- Reset de senha ----------
@auth_bp.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    """Recebe {"email": "..."} e envia link de reset se existir usuário. Sempre retorna ok (evitar enumeração)."""
    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        payload = {}
    email = (payload.get("email") or "").strip().lower()
    if not email:
        return jsonify({"ok": False, "error": "missing_email"}), 400
    data = _load_users()
    user = _find_user_by_email(data["users"], email)
    if user:
        secret = current_app.config.get("SECRET_KEY", "dev")
        tok = sign_token({"uid": user["id"], "email": email, "purpose": "reset"}, secret, expires_sec=3600)
        link = _reset_link(tok)
        html = render_template("email/reset.html", name=user["name"], link=link)
        text_body = render_template("email/reset.txt", name=user["name"], link=link)
        send_email("Redefinir sua senha", email, html=html, text=text_body)
    resp = make_response(jsonify({"ok": True, "mensagem": "Se o e-mail existir, um link foi enviado para sua caixa de entrada."}), 200)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Vary"] = "Cookie"
    return resp


@auth_bp.route("/reset-password", methods=["GET"])
def page_reset_password():
    """Página com formulário para nova senha. Valida token na submissão; exibe aviso se inválido."""
    token = request.args.get("token", "").strip()
    valid = False
    if token:
        payload = verify_token(token, current_app.config.get("SECRET_KEY", "dev"))
        valid = bool(payload and payload.get("purpose") == "reset")
    return render_template("reset_password.html", token=token, valid=valid)


@auth_bp.route("/api/reset-password", methods=["POST"])
def api_reset_password():
    """Troca a senha usando token. Aceita JSON ou form (token, password). Mantém sessão logada."""
    token = None
    new_password = None
    if request.is_json:
        try:
            payload = request.get_json(force=True) or {}
        except Exception:
            payload = {}
        token = (payload.get("token") or "").strip()
        new_password = payload.get("password") or ""
    else:
        token = (request.form.get("token") or "").strip()
        new_password = request.form.get("password") or ""
    if not token or not new_password:
        if request.is_json:
            return jsonify({"ok": False, "error": "missing_fields"}), 400
        return render_template("reset_password.html", token=token or "", valid=False, error="Dados ausentes"), 400
    payload = verify_token(token, current_app.config.get("SECRET_KEY", "dev"))
    if not payload or payload.get("purpose") != "reset":
        if request.is_json:
            return jsonify({"ok": False, "error": "invalid_or_expired"}), 400
        return render_template("reset_password.html", token=token, valid=False, error="Link inválido ou expirado"), 400
    data = _load_users()
    user = _find_user_by_id(data["users"], payload.get("uid"))
    if not user or (user.get("email") or "").lower() != (payload.get("email") or "").lower():
        if request.is_json:
            return jsonify({"ok": False, "error": "user_not_found"}), 404
        return render_template("reset_password.html", token=token, valid=False, error="Usuário não encontrado"), 404
    user["password_hash"] = generate_password_hash(new_password)
    _save_users(data)
    session["user_id"] = user["id"]
    if request.is_json:
        resp = make_response(jsonify({"ok": True}), 200)
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Vary"] = "Cookie"
        return resp
    r = redirect(url_for("edu.conteudos_page") if "edu.conteudos_page" in current_app.view_functions else "/#conteudos")
    r.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Vary"] = "Cookie"
    return r
