# -*- coding: utf-8 -*-
"""
Blueprint: Auth (Login, Cadastro, Esqueci Senha, Verificação, Logout, User).
Rotas: /api/login, /api/register (cadastro), /api/user, /api/user-data, /api/logout,
/forgot-password, /api/forgot-password, /reset-password, /api/reset-password,
/api/verify-email, /api/resend-verification, /api/auto-verify, /api/verificacao,
/auth/login, /api/delete-user.
Usa current_app.config["DB_PATH"] e User de backend.auth.user_model.
E-mail: funções expostas em current_app (send_verification_email, send_password_reset_email).
"""
import os
import base64
import secrets
import sqlite3
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, current_app
from flask_login import login_user, logout_user, login_required, current_user
import bcrypt

from backend.auth.user_model import User

auth_bp = Blueprint("auth", __name__, url_prefix="")


def _db_path():
    return current_app.config.get("DB_PATH", "")


def _normalize_email(s):
    if s is None:
        return ""
    return str(s).strip().lower()


def _get_app_helper(name, default=None):
    return getattr(current_app, name, default)


# ---------- Página forgot-password ----------
@auth_bp.route("/forgot-password")
def forgot_password():
    """Página de recuperação de senha."""
    try:
        from backend.version import get_build_version
    except Exception:
        get_build_version = lambda: "dev"
    return render_template("forgot_password.html", timestamp=get_build_version())


# ---------- API forgot-password ----------
@auth_bp.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    """Solicita recuperação de senha - envia email com token."""
    data = request.get_json() or {}
    norm = _get_app_helper("_normalize_email", _normalize_email)
    email = norm(data.get("email"))

    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400

    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({
            "sucesso": True,
            "mensagem": "Se o email existir, um link de recuperação foi enviado."
        }), 200

    user_id, name = user
    gen_token = _get_app_helper("generate_token")
    if not gen_token:
        gen_token = lambda length=32: secrets.token_urlsafe(length)
    reset_token = gen_token()
    expires = datetime.now() + timedelta(hours=1)

    cursor.execute(
        "UPDATE users SET reset_password_token = ?, reset_password_expires = ? WHERE id = ?",
        (reset_token, expires.isoformat(), user_id),
    )
    conn.commit()
    conn.close()

    email_configured = _get_app_helper("_email_configured")
    if callable(email_configured):
        email_configured = email_configured()
    if not email_configured:
        current_app.logger.warning("[FORGOT] Email não configurado")
        return jsonify({
            "sucesso": False,
            "erro": "O servidor não está configurado para enviar emails. Entre em contato com o administrador do site para redefinir sua senha."
        }), 503

    send_reset = _get_app_helper("send_password_reset_email")
    if send_reset:
        try:
            enviado = send_reset(email, name, reset_token)
            if enviado:
                return jsonify({
                    "sucesso": True,
                    "mensagem": "Email de recuperação enviado! Verifique sua caixa de entrada (e a pasta de spam). O link abre uma página do site para você definir uma nova senha. 💕"
                }), 200
        except Exception as e:
            current_app.logger.error("[FORGOT] %s", e, exc_info=True)
    return jsonify({
        "sucesso": False,
        "erro": "Não foi possível enviar o email. Tente novamente mais tarde ou entre em contato com o suporte."
    }), 503


# ---------- Página reset-password ----------
@auth_bp.route("/reset-password")
def reset_password():
    """Página de redefinição de senha com token."""
    token = request.args.get("token", "")
    if not token:
        return redirect(url_for("auth.forgot_password"))

    try:
        from backend.version import get_build_version
    except Exception:
        get_build_version = lambda: "dev"
    timestamp = get_build_version()

    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, reset_password_expires FROM users WHERE reset_password_token = ?",
        (token,),
    )
    user = cursor.fetchone()
    conn.close()

    token_valid = False
    if user:
        user_id, email, expires_str = user[0], user[1], user[2]
        if expires_str:
            try:
                expires = datetime.fromisoformat(expires_str)
                if datetime.now() <= expires:
                    token_valid = True
            except Exception:
                pass

    return render_template("forgot_password.html", timestamp=timestamp, token=token, token_valid=token_valid)


# ---------- API reset-password ----------
@auth_bp.route("/api/reset-password", methods=["POST"])
def api_reset_password():
    """Redefine a senha usando token."""
    data = request.get_json()
    token = (data.get("token") or "").strip()
    new_password = data.get("password", "")

    if not token or not new_password:
        return jsonify({"erro": "Token e nova senha são obrigatórios"}), 400
    if len(new_password) < 6:
        return jsonify({"erro": "A senha deve ter no mínimo 6 caracteres"}), 400

    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, reset_password_expires FROM users WHERE reset_password_token = ?",
        (token,),
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"erro": "Token inválido ou expirado"}), 400

    user_id, email, expires_str = user[0], user[1], user[2]
    if expires_str:
        try:
            expires = datetime.fromisoformat(expires_str)
            if datetime.now() > expires:
                conn.close()
                return jsonify({"erro": "Token expirado. Solicite uma nova recuperação."}), 400
        except Exception:
            pass

    password_hash_bytes = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    password_hash = base64.b64encode(password_hash_bytes).decode("utf-8")
    cursor.execute(
        "UPDATE users SET password_hash = ?, reset_password_token = NULL, reset_password_expires = NULL, email_verified = 1 WHERE id = ?",
        (password_hash, user_id),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "sucesso": True,
        "mensagem": "Senha redefinida com sucesso! Agora você pode fazer login. 💕"
    }), 200


# ---------- Cadastro (register) ----------
@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    """Cadastro de usuário (SQLite + verificação por email)."""
    try:
        data = request.get_json(force=True, silent=True) or {}
    except Exception as e:
        current_app.logger.warning("[REGISTER] Erro ao parsear JSON: %s", e)
        return jsonify({"erro": "Dados de cadastro inválidos. Verifique o formulário."}), 400
    if not isinstance(data, dict):
        return jsonify({"erro": "Dados de cadastro inválidos."}), 400

    norm = _get_app_helper("_normalize_email", _normalize_email)
    gen_token = _get_app_helper("generate_token") or (lambda length=32: secrets.token_urlsafe(length))
    email_configured = _get_app_helper("_email_configured")
    if callable(email_configured):
        email_configured = email_configured()
    send_verification = _get_app_helper("send_verification_email")

    name = (str(data.get("name") or "")).strip()
    email = norm(data.get("email"))
    password = str(data.get("password") or "")
    baby_name = (str(data.get("baby_name") or "")).strip() or None

    if not name or not email or not password:
        return jsonify({"erro": "Todos os campos obrigatórios devem ser preenchidos"}), 400
    if len(password) < 6:
        return jsonify({"erro": "A senha deve ter no mínimo 6 caracteres"}), 400
    if "@" not in email or "." not in email.split("@")[1]:
        return jsonify({"erro": "Email inválido"}), 400

    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, email_verified, password_hash FROM users WHERE email = ?", (email,))
        existing = cursor.fetchone()

        if existing:
            user_id_existing, email_verified_existing, existing_hash = existing
            if email_verified_existing == 1:
                conn.close()
                return jsonify({"erro": "Este email já está cadastrado e verificado. Faça login ou use 'Esqueci minha senha'."}), 409
            # Reenviar verificação
            password_hash_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            password_hash = base64.b64encode(password_hash_bytes).decode("utf-8")
            verification_token = gen_token()
            cursor.execute(
                "UPDATE users SET name = ?, password_hash = ?, baby_name = ?, email_verification_token = ? WHERE id = ?",
                (name, password_hash, baby_name, verification_token, user_id_existing),
            )
            conn.commit()
            conn.close()
            verification_sent = False
            mensagem = "Link de verificação reenviado! Verifique seu email para ativar sua conta. 💕"
            if email_configured and send_verification:
                try:
                    send_verification(email, name, verification_token)
                    verification_sent = True
                except Exception:
                    mensagem = "Senha atualizada. O email de verificação não pôde ser enviado. Use 'Reenviar link de verificação'."
            else:
                mensagem = "Senha atualizada. Configure RESEND ou MAIL_* no .env para receber o email de verificação."
            return jsonify({
                "sucesso": True, "mensagem": mensagem, "user_id": user_id_existing,
                "email": email, "verification_sent": verification_sent, "email_verified": False
            }), 201

        password_hash_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        password_hash = base64.b64encode(password_hash_bytes).decode("utf-8")
        verification_token = gen_token()
        email_verified_value = 0
        cursor.execute(
            """INSERT INTO users (name, email, password_hash, baby_name, email_verified, email_verification_token)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, email, password_hash, baby_name, email_verified_value, verification_token),
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        mensagem = ""
        verification_sent = False
        if email_configured and send_verification:
            try:
                send_verification(email, name, verification_token)
                mensagem = "Cadastro realizado! Verifique seu email para ativar sua conta. 💕"
                verification_sent = True
            except Exception as e:
                current_app.logger.exception("[REGISTER] Erro ao enviar email")
                conn_update = sqlite3.connect(_db_path())
                conn_update.cursor().execute("UPDATE users SET email_verified = 0 WHERE id = ?", (user_id,))
                conn_update.commit()
                conn_update.close()
                mensagem = "Cadastro realizado! O email de verificação não pôde ser enviado. Use 'Reenviar link de verificação'."
        else:
            conn_update = sqlite3.connect(_db_path())
            conn_update.cursor().execute("UPDATE users SET email_verified = 1 WHERE id = ?", (user_id,))
            conn_update.commit()
            conn_update.close()
            mensagem = "Cadastro realizado! Você já pode fazer login. (Configure RESEND ou MAIL_* no .env para envio de email.)"

        return jsonify({
            "sucesso": True, "mensagem": mensagem or "Cadastro realizado! Verifique seu email para ativar sua conta.",
            "user_id": user_id, "email": email, "verification_sent": verification_sent, "email_verified": verification_sent
        }), 201

    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        conn_check = sqlite3.connect(_db_path())
        cur = conn_check.cursor()
        cur.execute("SELECT id, email_verified FROM users WHERE email = ?", (email,))
        ex = cur.fetchone()
        conn_check.close()
        if ex and ex[1] == 1:
            erro_msg = "Este email já está cadastrado e verificado"
        else:
            erro_msg = "Este email já está cadastrado. Verifique seu email ou use 'Esqueci minha senha'"
        return jsonify({"erro": erro_msg}), 400
    except Exception as e:
        conn.rollback()
        conn.close()
        current_app.logger.exception("[REGISTER] Erro inesperado")
        return jsonify({"erro": "Erro ao processar cadastro. Tente novamente."}), 500


# ---------- Login ----------
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    """Login (rate limit por IP)."""
    client_ip = request.remote_addr or "unknown"
    rate_check = _get_app_helper("_login_rate_limit_check")
    if rate_check and callable(rate_check) and not rate_check(client_ip):
        current_app.logger.warning("[LOGIN] Rate limit excedido para IP: %s", client_ip)
        return jsonify({"erro": "Muitas tentativas de login. Tente novamente em 15 minutos."}), 429

    norm = _get_app_helper("_normalize_email", _normalize_email)
    password_correct = False
    stored_hash_str = None
    stored_hash = None
    hash_format = "desconhecido"
    try:
        data = request.get_json()
        if not data:
            return jsonify({"erro": "Dados de login não fornecidos"}), 400
        email = norm(data.get("email"))
        password = (data.get("password") or "").strip()
        remember_me = data.get("remember_me", False)

        if not email or not password:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        conn = sqlite3.connect(_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, password_hash, baby_name, email_verified FROM users WHERE email = ?",
            (email,),
        )
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return jsonify({"erro": "Email ou senha incorretos"}), 401
        conn.close()

        user_id, user_name, user_email, stored_hash_str, baby_name = user_data[0], user_data[1], user_data[2], user_data[3], user_data[4]
        email_verified = user_data[5] if len(user_data) > 5 else 1

        if not stored_hash_str:
            return jsonify({"erro": "Conta com problema. Use 'Esqueci minha senha' para corrigir."}), 401

        try:
            stored_hash = base64.b64decode(stored_hash_str.encode("utf-8"))
            hash_format = "base64"
        except Exception:
            if isinstance(stored_hash_str, str) and stored_hash_str.startswith("$2"):
                stored_hash = stored_hash_str.encode("utf-8")
                hash_format = "string bcrypt"
            elif isinstance(stored_hash_str, bytes):
                stored_hash = stored_hash_str
            else:
                return jsonify({"erro": "Conta com problema. Use 'Esqueci minha senha' para corrigir."}), 401

        if stored_hash:
            try:
                password_correct = bcrypt.checkpw(password.encode("utf-8"), stored_hash)
            except Exception:
                password_correct = False
    except Exception as e:
        current_app.logger.exception("[LOGIN] Erro inesperado")
        return jsonify({"erro": "Erro interno ao processar login. Tente novamente."}), 500

    if not password_correct:
        rate_clear = _get_app_helper("_login_rate_limit_clear")
        if rate_clear and callable(rate_clear):
            pass  # não limpa em falha
        return jsonify({"erro": "Email ou senha incorretos"}), 401

    if email_verified == 0:
        return jsonify({
            "erro": "Email não verificado",
            "mensagem": "Verifique seu email antes de fazer login. Procure por um email da Sophia. Se não recebeu, verifique a pasta de spam ou clique em 'Reenviar link de verificação'.",
            "pode_login": False, "email_nao_verificado": True, "email": email
        }), 403

    try:
        user = User(user_id, user_name, user_email, baby_name)
        login_user(user, remember=remember_me)
        rate_clear = _get_app_helper("_login_rate_limit_clear")
        if rate_clear and callable(rate_clear):
            rate_clear(client_ip)
    except Exception as e:
        current_app.logger.exception("[LOGIN] Erro ao fazer login_user")
        return jsonify({"erro": "Erro interno ao criar sessão"}), 500

    return jsonify({
        "sucesso": True,
        "mensagem": "Login realizado com sucesso! Bem-vinda de volta 💕",
        "user": {"id": user_id, "name": user_name, "email": user_email, "baby_name": baby_name}
    })


# ---------- Login por form (fallback) ----------
@auth_bp.route("/auth/login", methods=["POST"])
def auth_login_form():
    """Login por form POST. Redireciona para / em sucesso ou /?login_error=1 em falha."""
    norm = _get_app_helper("_normalize_email", _normalize_email)
    email = norm(request.form.get("email"))
    password = (request.form.get("password") or "").strip()
    remember_me = request.form.get("remember_me") in ("1", "on", "true", "yes")
    if not email or not password:
        return redirect(url_for("index", login_error=1))
    try:
        conn = sqlite3.connect(_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password_hash, baby_name FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return redirect(url_for("index", login_error=1))
        user_id, user_name, user_email, stored_hash_str, baby_name = row
        if not stored_hash_str:
            return redirect(url_for("index", login_error=1))
        try:
            stored_hash = base64.b64decode(stored_hash_str.encode("utf-8"))
        except Exception:
            stored_hash = stored_hash_str.encode("utf-8") if isinstance(stored_hash_str, str) else stored_hash_str
        if not stored_hash or not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            return redirect(url_for("index", login_error=1))
        user = User(user_id, user_name, user_email, baby_name)
        login_user(user, remember=remember_me)
        return redirect(url_for("index"))
    except Exception as e:
        current_app.logger.exception("auth_login_form: %s", e)
        return redirect(url_for("index", login_error=1))


# ---------- Logout ----------
@auth_bp.route("/api/logout", methods=["POST"])
def api_logout():
    try:
        logout_user()
        session.clear()
    except Exception:
        session.clear()
    return jsonify({"sucesso": True, "mensagem": "Logout realizado com sucesso"})


# ---------- User / User-data ----------
@auth_bp.route("/api/user", methods=["GET"])
def api_user():
    try:
        if getattr(current_user, "is_authenticated", False):
            return jsonify({
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "baby_name": getattr(current_user, "baby_name", None)
            }), 200
        return jsonify({"erro": "Não autenticado"}), 401
    except Exception as e:
        current_app.logger.debug("[AUTH] api_user: %s", e)
        return jsonify({"erro": "Não autenticado"}), 401


@auth_bp.route("/api/user-data", methods=["GET"])
def api_user_data():
    try:
        if getattr(current_user, "is_authenticated", False):
            payload = {"user": {"name": current_user.name or "Mamãe"}}
            baby_name = getattr(current_user, "baby_name", None)
            if baby_name:
                payload["baby_profile"] = {"name": baby_name}
            return jsonify(payload), 200
        return jsonify({}), 200
    except Exception as e:
        current_app.logger.debug("[AUTH] user-data: %s", e)
        return jsonify({}), 200


@auth_bp.route("/api/me", methods=["GET"])
def api_me():
    """Compatível com frontend (ex.: privacy-storage-guard.js). Retorna user + verified."""
    try:
        if getattr(current_user, "is_authenticated", False):
            return jsonify({
                "user": {"id": current_user.id, "name": current_user.name, "email": current_user.email},
                "verified": True
            }), 200
        return jsonify({}), 200
    except Exception as e:
        current_app.logger.debug("[AUTH] api_me: %s", e)
        return jsonify({}), 200


# ---------- Verify email ----------
@auth_bp.route("/api/verify-email", methods=["GET"])
def api_verify_email():
    token = request.args.get("token", "")
    if not token:
        base_url = os.environ.get("BASE_URL", request.host_url.rstrip("/"))
        return render_template("email_verified.html", base_url=base_url, error=True, message="Token não fornecido"), 400

    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name FROM users WHERE email_verification_token = ?", (token,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        base_url = os.environ.get("BASE_URL", request.host_url.rstrip("/"))
        return render_template("email_verified.html", base_url=base_url, error=True, message="Token inválido ou expirado"), 400

    user_id, email, name = user
    cursor.execute("SELECT email_verified FROM users WHERE id = ?", (user_id,))
    already_verified = (cursor.fetchone() or (0,))[0]
    cursor.execute("UPDATE users SET email_verified = 1, email_verification_token = NULL WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    base_url = os.environ.get("BASE_URL", request.host_url.rstrip("/"))
    return render_template("email_verified.html", base_url=base_url, error=False, email=email, name=name)


# ---------- Resend verification ----------
@auth_bp.route("/api/resend-verification", methods=["POST"])
def api_resend_verification():
    data = request.get_json() or {}
    norm = _get_app_helper("_normalize_email", _normalize_email)
    email = norm(data.get("email"))
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400

    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email_verified, email_verification_token FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return jsonify({"erro": "Email não encontrado"}), 404
    user_id, name, email_verified, token = user

    if email_verified == 1:
        return jsonify({"sucesso": True, "mensagem": "Seu email já está verificado! Você pode fazer login normalmente."}), 200

    gen_token = _get_app_helper("generate_token") or (lambda length=32: secrets.token_urlsafe(length))
    if not token:
        token = gen_token()
        conn = sqlite3.connect(_db_path())
        conn.cursor().execute("UPDATE users SET email_verification_token = ? WHERE id = ?", (token, user_id))
        conn.commit()
        conn.close()

    email_configured = _get_app_helper("_email_configured")
    if callable(email_configured):
        email_configured = email_configured()
    if not email_configured:
        conn = sqlite3.connect(_db_path())
        conn.cursor().execute("UPDATE users SET email_verified = 1 WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return jsonify({"sucesso": True, "mensagem": "Email não configurado no servidor. Sua conta foi ativada automaticamente. Você pode fazer login agora! 💕"}), 200

    send_verification = _get_app_helper("send_verification_email")
    if send_verification:
        try:
            send_verification(email, name, token)
            return jsonify({"sucesso": True, "mensagem": f"Email de verificação reenviado para {email}! Verifique sua caixa de entrada e também a pasta de spam. 💕"}), 200
        except Exception as e:
            current_app.logger.exception("[RESEND] Erro")
            return jsonify({"sucesso": False, "erro": f"Não foi possível reenviar o email. Erro: {str(e)}."}), 500
    return jsonify({"sucesso": False, "erro": "Serviço de email indisponível."}), 503


# ---------- Auto-verify (dev) ----------
@auth_bp.route("/api/auto-verify", methods=["POST"])
def api_auto_verify():
    data = request.get_json() or {}
    norm = _get_app_helper("_normalize_email", _normalize_email)
    email = norm(data.get("email"))
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400
    email_configured = _get_app_helper("_email_configured")
    if callable(email_configured):
        email_configured = email_configured()
    if email_configured:
        return jsonify({"erro": "Email está configurado. Use a verificação normal por email."}), 400

    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, email_verified FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"erro": "Email não encontrado"}), 404
    cursor.execute("UPDATE users SET email_verified = 1 WHERE id = ?", (user[0],))
    conn.commit()
    conn.close()
    return jsonify({"sucesso": True, "mensagem": "Conta marcada como verificada! Agora você pode fazer login. 💕"}), 200


# ---------- Verificação (hash) ----------
@auth_bp.route("/api/verificacao", methods=["POST"])
def api_verificacao():
    data = request.get_json()
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400

    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
    user_data = cursor.fetchone()
    conn.close()
    if not user_data:
        return jsonify({"encontrado": False, "mensagem": "Usuário não encontrado"}), 200
    user_id, user_name, user_email, stored_hash = user_data
    hash_valido = False
    if stored_hash:
        try:
            h = base64.b64decode(stored_hash.encode("utf-8"))
            hash_valido = bool(h and len(h) > 0)
        except Exception:
            if isinstance(stored_hash, str) and stored_hash.startswith("$2"):
                hash_valido = True
    return jsonify({
        "encontrado": True,
        "user_id": user_id,
        "nome": user_name,
        "email": user_email,
        "formato_hash": "base64" if stored_hash and not (isinstance(stored_hash, str) and stored_hash.startswith("$2")) else "legado",
        "hash_valido": hash_valido,
        "mensagem": "Usuário encontrado. " + ("Hash parece estar correto." if hash_valido else "Hash pode estar corrompido. Use 'Redefinir Senha' ou delete a conta.")
    })


# ---------- Delete user ----------
@auth_bp.route("/api/delete-user", methods=["POST"])
@login_required
def api_delete_user():
    if not current_user.is_authenticated:
        return jsonify({"erro": "Usuário não autenticado"}), 401
    data = request.get_json()
    norm = _get_app_helper("_normalize_email", _normalize_email)
    email_from_request = norm(data.get("email") if data else "")
    if email_from_request and email_from_request != norm(current_user.email):
        return jsonify({"erro": "Você só pode deletar sua própria conta."}), 403
    email = norm(current_user.email)

    conn = sqlite3.connect(_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"sucesso": True, "mensagem": "Usuário não encontrado (pode fazer novo cadastro)"}), 200
    user_id = user[0]
    if str(user_id) != str(current_user.id):
        conn.close()
        return jsonify({"erro": "Erro de segurança ao deletar conta"}), 500

    cursor.execute("DELETE FROM vacinas_tomadas WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM conversas WHERE user_id = ?", (str(user_id),))
    cursor.execute("DELETE FROM user_info WHERE user_id = ?", (str(user_id),))
    try:
        cursor.execute("DELETE FROM memoria_sophia WHERE user_id = ?", (str(user_id),))
    except Exception:
        pass
    cursor.execute("DELETE FROM baby_profiles WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    try:
        logout_user()
        session.clear()
    except Exception:
        pass
    current_app.logger.info("[DELETE_USER] Conta deletada: email=%s, user_id=%s", email, user_id)
    return jsonify({"sucesso": True, "mensagem": "Conta deletada com sucesso! Agora você pode fazer um novo cadastro. 💕"}), 200
