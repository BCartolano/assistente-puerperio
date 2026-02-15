# -*- coding: utf-8 -*-
# pyright: reportAttributeAccessIssue=false
# pyright: reportArgumentType=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportOptionalSubscript=false
# pyright: reportIndexIssue=false
# pyright: reportOperatorIssue=false
# pyright: reportCallIssue=false
# pyright: reportUndefinedVariable=false
# pyright: reportMissingImports=false
import os
import sys

# Configura encoding UTF-8 para Windows (melhorado para PowerShell)
if sys.platform == 'win32':
    # Define variável de ambiente ANTES de qualquer operação de I/O
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'  # Usa UTF-8 nativo no Windows
    
    # Tenta configurar o console para UTF-8 (se disponível)
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        # Se não conseguir reconfigurar, apenas usa a variável de ambiente
        pass
    
    # Tenta configurar o console do Windows diretamente (Python 3.7+)
    try:
        import io
        if hasattr(sys.stdout, 'buffer') and (not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if hasattr(sys.stderr, 'buffer') and (not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, ValueError, OSError):
        # Se não conseguir, continua com a configuração padrão
        pass

# Suprime avisos Pydantic V2 que poluem o log (opcional: remover em debug)
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic.*")

# Carrega .env o mais cedo possível (antes de qualquer cliente/chaves)
from dotenv import load_dotenv
_bd = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_bd) if _bd else os.getcwd()
for _p in [os.path.join(_root, ".env"), os.path.join(_bd, ".env"), ".env"]:
    if os.path.exists(_p):
        load_dotenv(_p, override=True)
        break
else:
    load_dotenv()

import time
import uuid
import json
import random
import re
import difflib
import sqlite3
import bcrypt
import base64
import secrets
import string
import logging
from logging.handlers import RotatingFileHandler
import unicodedata
from datetime import datetime, timedelta, date
from flask import Flask, request, jsonify, render_template, session, url_for, redirect, Response, g, make_response, abort, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from dateutil.relativedelta import relativedelta
from collections import defaultdict, Counter
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
from itertools import islice

# Tenta importar NLTK para stemming (opcional)
NLTK_AVAILABLE = False
try:
    import nltk
    from nltk.stem import RSLPStemmer
    NLTK_AVAILABLE = True
    # Baixa dados necessários se não estiverem disponíveis
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except:
            pass
    # Baixa RSLP stemmer se necessário
    try:
        nltk.data.find('stemmers/rslp')
    except LookupError:
        try:
            nltk.download('rslp', quiet=True)
        except:
            pass
except ImportError:
    NLTK_AVAILABLE = False
except Exception as e:
    NLTK_AVAILABLE = False
    # Logger ainda não está configurado aqui, usa print temporariamente
    print(f"[NLTK] ⚠️ NLTK não disponível: {e}")

# Configuração de logging (após imports básicos; nível via LOG_LEVEL no .env)
_log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
_log_level = getattr(logging, _log_level_name, logging.INFO)
logging.basicConfig(level=_log_level)

logger = logging.getLogger(__name__)

if not logger.handlers:  # Evita reconfigurar se já foi configurado
    logger.setLevel(_log_level)

    # Cria pasta logs se não existir
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(backend_dir) if backend_dir else os.getcwd()
    logs_dir = os.path.join(project_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Handler para arquivo com rotação (RotatingFileHandler) - LIMITE: 10MB por arquivo, 5 backups
    log_file = os.path.join(logs_dir, 'error_debug.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB por arquivo
        backupCount=5,  # Mantém 5 arquivos de backup (total máximo: ~60MB)
        encoding='utf-8'
    )
    file_handler.setLevel(_log_level)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Handler para console: opcional via LOG_CONSOLE (1=on). Se 0, só arquivo (reduz buffer do terminal/Cursor)
    _log_console = os.getenv("LOG_CONSOLE", "1").strip().lower() in ("1", "true", "on", "yes")
    if _log_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(_log_level)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(console_handler)
    
    logger.addHandler(file_handler)
    
    # Previne propagação para o logger root (evita duplicação)
    logger.propagate = False
    
    # Se LOG_CONSOLE=0, remove handler de console do root (reduz buffer do terminal/Cursor)
    if not _log_console:
        _root = logging.getLogger()
        for _h in list(_root.handlers):
            if isinstance(_h, logging.StreamHandler):
                _root.removeHandler(_h)

# Agora pode usar logger para NLTK
if NLTK_AVAILABLE:
    logger.info("[NLTK] ✅ NLTK importado com sucesso")
else:
    logger.info("[NLTK] ℹ️ NLTK não disponível (opcional - usando fallback)")

# Clientes de IA: inicializados só se houver chave ( .env já carregado no topo )
from backend.llm_clients import (
    openai_client,
    groq_client,
    gemini_client,
    gemini_model,
    genai,
    OPENAI_AVAILABLE,
    GEMINI_AVAILABLE,
    GROQ_AVAILABLE,
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    GROQ_API_KEY,
    OPENAI_ASSISTANT_ID,
)

# Geo: não carrega no import; inicia em thread após o site abrir (evita travar startup)
def _start_geo_lazy():
    import threading
    def _run():
        import time
        time.sleep(2.0)  # dá tempo do site abrir
        try:
            from backend.startup.download_geo import ensure_geo
            ensure_geo()
        except Exception as e:
            logger.info("[GEO] Download opcional (lazy) falhou: %s", e)
    threading.Thread(target=_run, daemon=True).start()
_start_geo_lazy()

# CNES Overrides: lazy boot (carrega na primeira rota que precisar; use ensure_boot() ou get_overrides())
# Não chama boot() na importação para start rápido; cache .pkl acelera cargas subsequentes.

# Verifica se as variáveis de email foram carregadas (após load_dotenv)
mail_username_env = os.getenv('MAIL_USERNAME')
mail_password_env = os.getenv('MAIL_PASSWORD')
resend_key_env = os.getenv('RESEND_API_KEY', '').strip()

if resend_key_env:
    logger.info("[ENV] ✅ Email configurado via Resend (RESEND_API_KEY)")
    print("[ENV] ✅ Email configurado via Resend (3.000/mês grátis)")
elif mail_username_env and mail_password_env:
    logger.info(f"[ENV] ✅ Variáveis de email carregadas: MAIL_USERNAME={mail_username_env[:5]}...")
    print(f"[ENV] ✅ Variáveis de email carregadas: MAIL_USERNAME={mail_username_env}")
else:
    logger.warning("[ENV] ⚠️ Email não configurado. Use RESEND_API_KEY ou MAIL_USERNAME/MAIL_PASSWORD no .env")
    print("[ENV] ⚠️ Email não configurado. Use RESEND_API_KEY (Resend) ou MAIL_USERNAME/MAIL_PASSWORD (Gmail) no .env")

# Blueprint de geolocalização /api/nearby (tolerante a falhas)
try:
    from backend.geo.nearby import geo_bp
except Exception as _geo_err:
    geo_bp = None

try:
    from backend.blueprints.auth_routes import auth_bp
except Exception as _auth_err:
    auth_bp = None

try:
    from backend.seo import seo_bp
except Exception as _seo_err:
    seo_bp = None

# Inicializa o Flask com os caminhos corretos
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            static_url_path='/static')

# Cookies de sessão (segurança) – seguros em prod, flex em dev
try:
    is_prod = (os.environ.get("FLASK_ENV", "").lower() == "production") or (
        os.environ.get("SESSION_SECURE", "1").lower() in ("1", "true", "yes")
    )
    same = os.environ.get("SESSION_SAMESITE", "Lax")
    ttl_days = int(os.environ.get("SESSION_TTL_DAYS", "30"))
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE=same,
        SESSION_COOKIE_SECURE=is_prod,
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SAMESITE=same,
        REMEMBER_COOKIE_SECURE=is_prod,
        PERMANENT_SESSION_LIFETIME=timedelta(days=ttl_days)
    )
except Exception:
    pass


@app.context_processor
def inject_config():
    """Expõe app.config no Jinja (ex.: {% if config.DEBUG %} para skeleton-toggle)."""
    return dict(config=app.config)


# CORS opcional por FRONT_ORIGIN
try:
    from flask_cors import CORS  # pyright: ignore[reportMissingModuleSource]
    _front = os.environ.get("FRONT_ORIGIN")
    if _front:
        CORS(app, resources={r"/api/*": {"origins": [_front], "supports_credentials": True}})
        try:
            app.logger.info("[CORS] Habilitado para %s", _front)
        except Exception:
            pass
except Exception:
    pass


# Monitoring (opcional)
try:
    from backend.monitoring.appinsights import init_appinsights
    init_appinsights(app)
except Exception:
    pass


if geo_bp is not None:
    try:
        app.register_blueprint(geo_bp)
        app.logger.info("[GEO] Blueprint /api/nearby registrado")
    except Exception as _e:
        try:
            app.logger.warning("[GEO] Falha ao registrar blueprint: %s", _e)
        except Exception:
            pass

# Blueprint de hospitais com PostgreSQL + PostGIS (tolerante a falhas)
try:
    from backend.api.routes_hospitais import hospitais_bp
    app.register_blueprint(hospitais_bp)
    app.logger.info("[HOSPITAIS] Blueprint /api/hospitais-proximos registrado")
except Exception as _e:
    try:
        app.logger.warning("[HOSPITAIS] Falha ao registrar blueprint: %s", _e)
    except Exception:
        pass


@app.context_processor
def inject_static_version():
    """Injeta timestamp (cache busting) em todos os templates. Usa get_build_version() para que cada deploy gere URLs novas."""
    try:
        return {"timestamp": get_build_version()}
    except Exception:
        return {"timestamp": "1"}


@app.errorhandler(404)
def _not_found(e):
    try:
        return render_template("errors/404.html"), 404
    except Exception:
        return "Not found", 404


@app.errorhandler(500)
def _server_error(e):
    try:
        return render_template("errors/500.html"), 500
    except Exception:
        return "Server error", 500


if auth_bp is not None:
    try:
        app.register_blueprint(auth_bp, url_prefix="")
        app.logger.info("[AUTH] Blueprint auth_bp registrado (/api/login, /api/register, /api/user, /api/logout, /forgot-password, etc.)")
    except Exception as _e:
        try:
            app.logger.warning("[AUTH] Falha ao registrar blueprint: %s", _e)
        except Exception:
            pass

if seo_bp is not None:
    try:
        app.register_blueprint(seo_bp)
        app.logger.info("[SEO] Blueprint robots/sitemap registrado")
    except Exception:
        pass

# Blueprints modulares (arquitetura "Mansão") – edu ativo; auth/health/chat em migração gradual
try:
    from backend.blueprints import edu_bp
    app.register_blueprint(edu_bp, url_prefix="")
    app.logger.info("[BLUEPRINTS] edu_bp registrado (/conteudos, /api/educational)")
except Exception as _e:
    app.logger.warning("[BLUEPRINTS] edu_bp falhou: %s", _e)
try:
    from backend.blueprints import health_bp
    app.register_blueprint(health_bp, url_prefix="")
    app.logger.info("[BLUEPRINTS] health_bp registrado (/api/v1/emergency, /api/v1/health, /api/vacinas, /api/baby_profile, /api/vaccination)")
except Exception as _e:
    app.logger.warning("[BLUEPRINTS] health_bp falhou: %s", _e)
try:
    from backend.blueprints import chat_bp
    app.register_blueprint(chat_bp, url_prefix="")
    app.logger.info("[BLUEPRINTS] chat_bp registrado (/api/chat, /api/historico, /api/categorias, /api/alertas, /api/guias, /api/cuidados, /api/triagem-emocional, /api/limpar-memoria-ia)")
except Exception as _e:
    app.logger.warning("[BLUEPRINTS] chat_bp falhou: %s", _e)


# Rate limit login: máx 10 tentativas por IP a cada 15 min (evita brute force)
_LOGIN_RATE_LIMIT = {}  # {ip: {"count": int, "window_start": float}}
_LOGIN_RATE_LIMIT_LOCK = Lock()
LOGIN_RATE_LIMIT_MAX = 10
LOGIN_RATE_LIMIT_WINDOW_SEC = 900  # 15 min

def _login_rate_limit_check(ip):
    """Retorna True se dentro do limite; False se excedeu (deve retornar 429)."""
    with _LOGIN_RATE_LIMIT_LOCK:
        now = time.time()
        if ip not in _LOGIN_RATE_LIMIT:
            _LOGIN_RATE_LIMIT[ip] = {"count": 0, "window_start": now}
        rec = _LOGIN_RATE_LIMIT[ip]
        if now - rec["window_start"] > LOGIN_RATE_LIMIT_WINDOW_SEC:
            rec["count"] = 0
            rec["window_start"] = now
        rec["count"] += 1
        return rec["count"] <= LOGIN_RATE_LIMIT_MAX

def _login_rate_limit_clear(ip):
    with _LOGIN_RATE_LIMIT_LOCK:
        _LOGIN_RATE_LIMIT.pop(ip, None)

# PERF: log e exposição no /health (PERF_LOG=on, PERF_EXPOSE=on no .env)
PERF_LOG = os.getenv("PERF_LOG", "").lower() in ("1", "true", "on", "yes")
PERF_EXPOSE = os.getenv("PERF_EXPOSE", "true").lower() in ("1", "true", "on", "yes")
_T_IMPORT_START = time.perf_counter()
_PERF_FIRST_REQ_LOGGED = False
_PERF_BOOT_DONE = False
_perf_logger = logging.getLogger("sophia.perf")
# Métricas acumuladas para /api/v1/health (perf)
_PERF_IMPORT_MS = None
_PERF_FIRST_REQ_MS = None
_PERF_FIRST_REQ_AT = None
_PERF_OVR_BOOT_MS = None
_PERF_OVR_BOOT_AT = None

# OVERRIDES_BOOT=background: pré-aquece overrides em thread (não bloqueia o start)
if os.getenv("OVERRIDES_BOOT", "lazy").lower() in ("bg", "background"):
    import threading
    def _bg_boot(app_ref):
        global _PERF_OVR_BOOT_MS, _PERF_OVR_BOOT_AT, _PERF_BOOT_DONE
        try:
            from backend.startup.cnes_overrides import ensure_boot, get_snapshot_used, get_overrides_count
            t0 = time.perf_counter()
            ensure_boot()
            dt = (time.perf_counter() - t0) * 1000
            _PERF_OVR_BOOT_MS = round(dt, 0)
            _PERF_OVR_BOOT_AT = (datetime.utcnow().isoformat() + "Z")
            _PERF_BOOT_DONE = True
            if app_ref is not None:
                app_ref._perf_ovr_boot_ms = _PERF_OVR_BOOT_MS
                app_ref._perf_ovr_boot_at = _PERF_OVR_BOOT_AT
            _perf_logger.info(
                "[PERF] overrides boot (bg) ok: %.0f ms snapshot=%s count=%s",
                dt, get_snapshot_used(), get_overrides_count(),
            )
        except Exception as e:
            _perf_logger.warning("[PERF] overrides boot (bg) fail: %s", e)
    threading.Thread(target=_bg_boot, args=(app,), daemon=True).start()

# GEO_PREWARM=1: pré-aquece cache do parquet de hospitais em background (evita timeout na 1ª busca)
if os.getenv("GEO_PREWARM", "0").strip() in ("1", "true", "on", "yes"):
    import threading
    def _bg_geo_prewarm():
        try:
            from backend.api.routes import load_geo_df
            t0 = time.perf_counter()
            df = load_geo_df()
            dt = (time.perf_counter() - t0) * 1000
            rows = len(df) if df is not None else 0
            _perf_logger.info("[GEO] prewarm ok: %d linhas em %.0f ms", rows, dt)
        except Exception as e:
            _perf_logger.warning("[GEO] prewarm fail: %s", e)
    threading.Thread(target=_bg_geo_prewarm, daemon=True).start()

# Admin /debug/*: token e/ou IP (produção: ADMIN_DEBUG=off)
ADMIN_DEBUG = os.getenv("ADMIN_DEBUG", "on").lower() in ("1", "true", "on", "yes")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN") or None
_admin_ips_raw = os.getenv("ADMIN_ALLOWED_IPS", "127.0.0.1,::1")
ADMIN_ALLOWED_IPS = {ip.strip() for ip in _admin_ips_raw.split(",") if ip.strip()}


def _admin_allowed():
    """Retorna (True, None) se permitido; (False, (msg, code)) se bloqueado."""
    if not ADMIN_DEBUG:
        return False, ("disabled", 404)
    remote_ip = (request.headers.get("X-Forwarded-For") or "").split(",")[0].strip() or (request.remote_addr or "")
    if ADMIN_ALLOWED_IPS and not any(remote_ip.startswith(ip) for ip in ADMIN_ALLOWED_IPS if ip):
        return False, ("forbidden", 403)
    if ADMIN_TOKEN:
        tok = request.headers.get("X-Admin-Token") or request.args.get("admin_token")
        if tok != ADMIN_TOKEN:
            return False, ("forbidden", 403)
    return True, None


# CORS: origens permitidas (ALLOW_ORIGINS no .env, ex.: http://localhost:5173,http://localhost:5000)
_allow_origins_raw = os.getenv("ALLOW_ORIGINS", "")
ALLOW_ORIGINS_SET = {o.strip() for o in _allow_origins_raw.split(",")} if _allow_origins_raw else set()
api_logger = logging.getLogger("sophia.api")

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sua-chave-secreta-super-segura-mude-isso-em-producao')
BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "dados")
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")
DB_PATH_ABS = os.path.abspath(DB_PATH)
app.config["DB_PATH"] = DB_PATH  # Para blueprints acessarem via current_app.config["DB_PATH"]
logger.info(f"[DB] Banco de usuários: {DB_PATH_ABS}")
print(f"[DB] Banco de usuários: {DB_PATH_ABS}")
# Flag para controlar uso de IA (permite desabilitar completamente)
USE_AI = os.getenv("USE_AI", "true").lower() == "true"
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()  # openai, gemini ou groq
logger.info("[IA] USE_AI=%s AI_PROVIDER=%s", USE_AI, AI_PROVIDER)

# Aviso claro quando o provider escolhido não tem chave (ex.: Render sem GROQ_API_KEY)
if USE_AI:
    if AI_PROVIDER == "groq" and not GROQ_AVAILABLE:
        _msg = "[IA] AI_PROVIDER=groq mas GROQ_API_KEY não está definido. Defina GROQ_API_KEY no Render (Environment) para o chat com IA; senão o app usa respostas locais (fallback)."
        logger.warning(_msg)
        print(_msg)
    elif AI_PROVIDER == "openai" and not OPENAI_AVAILABLE:
        _msg = "[IA] AI_PROVIDER=openai mas OPENAI_API_KEY não está definido. Defina OPENAI_API_KEY no Render (Environment) para o chat com IA."
        logger.warning(_msg)
        print(_msg)
    elif AI_PROVIDER == "gemini" and not GEMINI_AVAILABLE:
        _msg = "[IA] AI_PROVIDER=gemini mas GEMINI_API_KEY não está definido. Defina GEMINI_API_KEY no Render (Environment) para o chat com IA."
        logger.warning(_msg)
        print(_msg)

# Chaves e clientes vêm de llm_clients (já carregados com .env do topo)

# YouTube API Key (opcional - para busca dinâmica de vídeos, independente de USE_AI)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if YOUTUBE_API_KEY:
    logger.info(f"[YOUTUBE] YOUTUBE_API_KEY encontrada (length: {len(YOUTUBE_API_KEY)})")
    print(f"[YOUTUBE] YOUTUBE_API_KEY encontrada (opcional para busca dinâmica)")
else:
    logger.info("[YOUTUBE] YOUTUBE_API_KEY não encontrada - busca dinâmica desabilitada, usando vídeos estáticos")
    print("[YOUTUBE] YOUTUBE_API_KEY não encontrada - busca dinâmica desabilitada, usando vídeos estáticos")

# Configurações de sessão para funcionar com IP/localhost e mobile
# Detecta se está em produção (HTTPS) ou desenvolvimento
# Render define várias variáveis: RENDER, RENDER_EXTERNAL_URL, etc.
# Heroku define DYNO
# Outras plataformas podem definir outras variáveis
is_production = (
    os.getenv('RENDER') is not None or 
    os.getenv('RENDER_EXTERNAL_URL') is not None or
    os.getenv('DYNO') is not None or
    os.getenv('FLASK_ENV') == 'production'
)
app.config['SESSION_COOKIE_SECURE'] = is_production  # True em produção (HTTPS), False em desenvolvimento
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Permite cookies entre localhost e IP, funciona melhor em mobile

# Compressão Gzip/Brotli para melhorar performance
try:
    from flask_compress import Compress
    compress = Compress()
    compress.init_app(app)
    logger.info("[PERFORMANCE] ✅ Compressão Gzip/Brotli ativada")
    print("[PERFORMANCE] ✅ Compressão Gzip/Brotli ativada")
except ImportError:
    logger.warning("[PERFORMANCE] ⚠️ flask-compress não instalado - compressão desabilitada")
    print("[PERFORMANCE] ⚠️ flask-compress não instalado - compressão desabilitada")
    compress = None

# Headers de cache e performance para recursos estáticos
@app.before_request
def handle_preflight():
    """Handle CORS preflight (OPTIONS); usa ALLOW_ORIGINS se definido."""
    if request.method != 'OPTIONS':
        return None
    origin = request.headers.get('Origin', '')
    if ALLOW_ORIGINS_SET:
        if '' in ALLOW_ORIGINS_SET or '*' in ALLOW_ORIGINS_SET:
            allowed_origin = origin or '*'
        elif origin in ALLOW_ORIGINS_SET:
            allowed_origin = origin
        else:
            allowed_origin = '*'
    else:
        if origin and any(k in origin.lower() for k in ('ngrok', 'localhost', '127.0.0.1')):
            allowed_origin = origin
        else:
            allowed_origin = origin or '*'
    response = Response(status=204)
    response.headers['Access-Control-Allow-Origin'] = allowed_origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, POST, PUT, DELETE, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Max-Age'] = '3600'
    if allowed_origin != '*':
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    else:
        response.headers['Access-Control-Allow-Credentials'] = 'false'
    return response

# REQUEST_DEBUG=1 no .env para logar cada requisição no console (desativado por padrão para não travar o Cursor)
_REQUEST_DEBUG = os.getenv("REQUEST_DEBUG", "0").strip() in ("1", "true", "on", "yes")

@app.before_request
def log_all_requests():
    """Loga requisições no console apenas se REQUEST_DEBUG=1 (evita excesso no terminal)."""
    if not _REQUEST_DEBUG:
        return
    try:
        import sys
        print(f"[REQUEST DEBUG] {request.method} {request.path} | {request.remote_addr}", flush=True)
        sys.stdout.flush()
    except Exception as e:
        logger.debug("log_all_requests: %s", e)


@app.before_request
def _req_log():
    """Log compacto REQ para diagnóstico (sophia.api)."""
    qs = request.query_string.decode() if request.query_string else ''
    api_logger.info("REQ %s %s?%s", request.method, request.path, qs)


@app.before_request
def _perf_boot_and_start():
    """Marca início do request para PERF. CNES overrides NÃO são carregados aqui (só na 1ª busca por hospital)."""
    global _PERF_FIRST_REQ_LOGGED
    if PERF_LOG or PERF_EXPOSE:
        g._perf_started = time.perf_counter()


@app.after_request
def _perf_first_req(resp):
    """Loga e registra tempo da primeira resposta (PERF_LOG / PERF_EXPOSE)."""
    global _PERF_FIRST_REQ_LOGGED, _PERF_FIRST_REQ_MS, _PERF_FIRST_REQ_AT
    if (PERF_LOG or PERF_EXPOSE) and not _PERF_FIRST_REQ_LOGGED and getattr(g, "_perf_started", None) is not None:
        dt = (time.perf_counter() - g._perf_started) * 1000
        _PERF_FIRST_REQ_MS = round(dt, 0)
        _PERF_FIRST_REQ_AT = (datetime.utcnow().isoformat() + "Z")
        try:
            app._perf_first_req_ms = _PERF_FIRST_REQ_MS
            app._perf_first_req_at = _PERF_FIRST_REQ_AT
        except Exception:
            pass
        _perf_logger.info(
            "[PERF] first request %s %s -> %s in %.0f ms",
            request.method, request.path, resp.status_code, dt
        )
        _PERF_FIRST_REQ_LOGGED = True
    return resp


@app.errorhandler(500)
def handle_internal_error(e):
    """Handler para erros 500 - salva traceback completo em error_debug.log"""
    import traceback
    
    print(f"[ERROR_500] ════════════════════════════════════")
    print(f"[ERROR_500] ERRO 500 DETECTADO!")
    print(f"[ERROR_500] Path: {request.path}")
    print(f"[ERROR_500] Method: {request.method}")
    print(f"[ERROR_500] ════════════════════════════════════")
    
    # Cria pasta logs se não existir
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(backend_dir) if backend_dir else os.getcwd()
    logs_dir = os.path.join(project_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    error_log_file = os.path.join(logs_dir, 'error_debug.log')
    
    # Obtém traceback completo
    tb_str = traceback.format_exc()
    print(f"[ERROR_500] TRACEBACK:\n{tb_str}")
    
    # Log completo com contexto
    error_entry = f"""
{'='*80}
ERRO 500 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
Endpoint: {request.method} {request.path}
User-Agent: {request.headers.get('User-Agent', 'N/A')}
Remote Address: {request.remote_addr}
Query String: {request.query_string.decode('utf-8') if request.query_string else 'N/A'}
Content-Type: {request.content_type or 'N/A'}

TRACEBACK:
{tb_str}
{'='*80}

"""
    
    # Salva no arquivo de log
    try:
        with open(error_log_file, 'a', encoding='utf-8') as f:
            f.write(error_entry)
        logger.error(f"[ERROR_500] ✅ Traceback salvo em: {error_log_file}")
    except Exception as log_error:
        logger.error(f"[ERROR_DEBUG] ❌ Erro ao salvar log de erro 500: {log_error}")
    
    # Log no console também
    logger.error(f"[ERROR_500] ❌ Erro interno no servidor: {request.path}")
    logger.error(f"[ERROR_500] Traceback completo salvo em: {error_log_file}")
    print(f"[ERROR_500] ❌ Erro 500: {request.path}")
    print(f"[ERROR_500] Traceback salvo em: {error_log_file}")
    
    # Retorna resposta amigável ao cliente
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Ocorreu um erro ao processar sua solicitação. Nossa equipe foi notificada.',
        'timestamp': datetime.now().isoformat()
    }), 500

@app.after_request
def add_cors_headers(response):
    """CORS: usa ALLOW_ORIGINS do .env; senão permite localhost/ngrok."""
    try:
        origin = request.headers.get('Origin', '')
        if ALLOW_ORIGINS_SET:
            if '' in ALLOW_ORIGINS_SET or '*' in ALLOW_ORIGINS_SET:
                response.headers['Access-Control-Allow-Origin'] = origin or '*'
            elif origin in ALLOW_ORIGINS_SET:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Vary'] = 'Origin'
            else:
                response.headers['Access-Control-Allow-Origin'] = origin or '*'
        else:
            if origin and any(k in origin.lower() for k in ('ngrok', 'localhost', '127.0.0.1')):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, POST, PUT, DELETE, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        if response.headers.get('Access-Control-Allow-Origin') != '*':
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        else:
            response.headers['Access-Control-Allow-Credentials'] = 'false'
        expose = set(h.strip() for h in response.headers.get('Access-Control-Expose-Headers', '').split(',') if h.strip())
        expose.update(['Content-Length', 'Content-Type'])
        response.headers['Access-Control-Expose-Headers'] = ', '.join(sorted(expose))
    except Exception as e:
        logger.warning("[CORS] Erro: %s", e, exc_info=True)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, POST, PUT, DELETE, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    return response


@app.after_request
def _res_log(resp):
    """Log compacto RES para diagnóstico (sophia.api)."""
    api_logger.info("RES %s %s -> %s", request.method, request.path, resp.status_code)
    return resp


@app.after_request
def add_cache_headers(response):
    """Adiciona headers de cache e compressão para melhorar performance"""
    # Trata erros de Broken Pipe graciosamente (requisições canceladas pelo cliente)
    try:
        # API endpoints de dados JSON não devem ser cacheados (sempre atualizados)
        if request.path.startswith('/api/'):
            response.cache_control.no_cache = True
            response.cache_control.no_store = True
            response.cache_control.must_revalidate = True
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        # HTML (index e demais páginas): no-store para evitar shell velha
        elif response.content_type and 'text/html' in (response.content_type or ''):
            response.cache_control.no_store = True
            response.cache_control.no_cache = True
            response.cache_control.must_revalidate = True
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        # Modo estrito: no-store para /static/ quando STRICT_NO_CACHE=1 (depurar produção)
        if os.environ.get("STRICT_NO_CACHE", "0").lower() in ("1", "true", "yes"):
            try:
                if request.path.startswith("/static/"):
                    response.cache_control.no_store = True
                    response.cache_control.no_cache = True
                    response.cache_control.must_revalidate = True
                    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
            except Exception:
                pass
        # Cache para recursos estáticos (CSS, JS, imagens)
        elif request.endpoint == 'static' or request.path.startswith('/static/'):
            # STATIC_CACHE_MAX_AGE em segundos (dev: 60–300; prod: 3600 ou 31536000)
            _static_max_age = int(os.environ.get("STATIC_CACHE_MAX_AGE", "3600"))
            if _static_max_age <= 0:
                response.cache_control.no_store = True
                response.cache_control.max_age = 0
            elif '?v=' in request.path or request.path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.woff', '.woff2')):
                response.cache_control.max_age = min(_static_max_age, 31536000)
                response.cache_control.public = True
                if _static_max_age >= 86400:
                    response.cache_control.immutable = True
            else:
                response.cache_control.max_age = min(_static_max_age, 3600)
                response.cache_control.public = True
        
        # Build version em todas as respostas (diagnóstico rápido)
        try:
            response.headers['X-Build-Version'] = get_build_version()
        except Exception:
            pass
        # Headers de segurança e performance
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Compressão e encoding
        if request.path.endswith(('.css', '.js', '.html', '.json', '.xml', '.txt')):
            response.headers['Vary'] = 'Accept-Encoding'
            # Força compressão se disponível
            if compress is None and 'gzip' in request.headers.get('Accept-Encoding', ''):
                # Compressão manual básica se flask-compress não estiver disponível
                import gzip
                if response.content_length and response.content_length > 1024:  # Só comprime arquivos > 1KB
                    try:
                        content = response.get_data()
                        compressed = gzip.compress(content)
                        if len(compressed) < len(content):
                            response.set_data(compressed)
                            response.headers['Content-Encoding'] = 'gzip'
                            response.headers['Content-Length'] = len(compressed)
                    except:
                        pass  # Se falhar, retorna sem compressão
        
        return response
        
    except (BrokenPipeError, ConnectionResetError, OSError) as e:
        # Erro de conexão fechada pelo cliente (requisição cancelada)
        # Log silencioso para não poluir logs durante testes mobile
        logger.debug(f"[BROKEN_PIPE] Conexão fechada pelo cliente: {request.path} - {str(e)}")
        # Retorna resposta vazia para evitar erro no servidor
        return Response(status=499, mimetype='application/json')  # 499 = Client Closed Request


@app.after_request
def ensure_emergency_headers(resp):
    """Garante headers completos e Access-Control-Expose-Headers em /api/v1/emergency/search e /api/nearby (0090/0095)."""
    try:
        path = request.path or ''
        if re.search(r'^/api/v1/emergency/search', path, re.I) or re.search(r'^/api/nearby', path, re.I):
            expose_set = set([h.strip() for h in resp.headers.get('Access-Control-Expose-Headers', '').split(',') if h.strip()])
            for h in ('X-Data-Source', 'X-Data-Mtime', 'X-Data-Count', 'X-Query-Lat', 'X-Query-Lon', 'X-Query-Radius'):
                expose_set.add(h)
            resp.headers['Access-Control-Expose-Headers'] = ', '.join(sorted(expose_set))
            if request.args.get('lat'):
                resp.headers.setdefault('X-Query-Lat', request.args.get('lat'))
            if request.args.get('lon'):
                resp.headers.setdefault('X-Query-Lon', request.args.get('lon'))
            if request.args.get('radius_km'):
                resp.headers.setdefault('X-Query-Radius', request.args.get('radius_km'))
            if not resp.headers.get('X-Data-Source') or not resp.headers.get('X-Data-Mtime'):
                try:
                    details = _emergency_health_details()
                    if details.get('source') and not resp.headers.get('X-Data-Source'):
                        resp.headers['X-Data-Source'] = details['source']
                    if details.get('mtime') and not resp.headers.get('X-Data-Mtime'):
                        resp.headers['X-Data-Mtime'] = str(details['mtime'])
                except Exception:
                    pass
            if not resp.headers.get('X-Data-Count') and 'application/json' in (resp.headers.get('Content-Type') or ''):
                try:
                    body = resp.get_data(as_text=True) or ''
                    j = json.loads(body)
                    count = j.get('count')
                    if count is None and isinstance(j.get('results'), list):
                        count = len(j['results'])
                    if count is None and isinstance(j.get('items'), list):
                        count = len(j['items'])
                    if isinstance(count, int):
                        resp.headers['X-Data-Count'] = str(count)
                except Exception:
                    pass
            try:
                if log_emergency_search:
                    props = {
                        "count": int(resp.headers.get('X-Data-Count')) if resp.headers.get('X-Data-Count') else None,
                        "source": resp.headers.get('X-Data-Source'),
                        "mtime": int(resp.headers.get('X-Data-Mtime')) if resp.headers.get('X-Data-Mtime') and str(resp.headers.get('X-Data-Mtime')).isdigit() else resp.headers.get('X-Data-Mtime'),
                        "lat": resp.headers.get('X-Query-Lat'),
                        "lon": resp.headers.get('X-Query-Lon'),
                        "radius_km": resp.headers.get('X-Query-Radius'),
                        "endpoint": "/api/nearby" if re.search(r'^/api/nearby', path, re.I) else "/api/v1/emergency/search"
                    }
                    props = {k: v for k, v in props.items() if v is not None}
                    if props:
                        log_emergency_search(props)
            except Exception:
                pass
    except Exception:
        pass
    return resp


# Configurações de Email
# Carrega configurações de email do .env
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@chatbot-puerperio.com')

# Log das configurações carregadas (sem mostrar senha completa)
mail_config_status = {
    'MAIL_SERVER': app.config['MAIL_SERVER'],
    'MAIL_PORT': app.config['MAIL_PORT'],
    'MAIL_USE_TLS': app.config['MAIL_USE_TLS'],
    'MAIL_USERNAME': app.config['MAIL_USERNAME'] or '(não configurado)',
    'MAIL_PASSWORD': '***' if app.config['MAIL_PASSWORD'] else '(não configurado)',
    'MAIL_DEFAULT_SENDER': app.config['MAIL_DEFAULT_SENDER']
}
logger.info(f"[EMAIL CONFIG] Configurações carregadas: {mail_config_status}")
print(f"[EMAIL CONFIG] Servidor: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
print(f"[EMAIL CONFIG] TLS: {app.config['MAIL_USE_TLS']}")
print(f"[EMAIL CONFIG] Username: {app.config['MAIL_USERNAME'] or '(não configurado)'}")
print(f"[EMAIL CONFIG] Password: {'***' if app.config['MAIL_PASSWORD'] else '(não configurado)'}")
print(f"[EMAIL CONFIG] Sender: {app.config['MAIL_DEFAULT_SENDER']}")

mail = Mail(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
login_manager.session_protection = 'basic'  # Usa "basic" para melhor compatibilidade com mobile e diferentes IPs
# "strong" pode causar problemas em dispositivos móveis com mudança de rede

# Handler para quando login é necessário em requisições AJAX
@login_manager.unauthorized_handler
def unauthorized():
    """Retorna 401 JSON para requisições AJAX não autenticadas"""
    try:
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({"erro": "Não autenticado", "redirect": "/"}), 401
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"[AUTH] Erro no unauthorized handler: {e}")
        return jsonify({"erro": "Não autenticado"}), 401

# ========================================================================
# Integração FastAPI desabilitada
# ========================================================================
# Mantemos apenas Flask na porta 5000. Se precisar do FastAPI,
# rode-o em processo/porta separados (ex.: uvicorn backend.api.main:app --port 8000).
logger.info("ℹ️ FastAPI desabilitado neste processo. Apenas Flask responde em /api/*")
print("ℹ️ FastAPI desabilitado neste processo. Apenas Flask responde em /api/*")

# ========================================================================
# Clientes de IA vêm de backend.llm_clients (inicializados só se houver chave).

# Classe User para Flask-Login (definida em backend.auth.user_model para uso também no blueprint auth)
from backend.auth.user_model import User

# Função para inicializar banco de dados
def init_db():
    print("DEBUG - INIT_DB EXECUTANDO")
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    # Ativa WAL mode para melhor performance com múltiplas conexões simultâneas
    # Importante para Beta Fechado (10-20 usuárias simultâneas)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA synchronous=NORMAL;')  # Balance entre segurança e performance
    conn.execute('PRAGMA cache_size=-64000;')  # 64MB cache (melhora performance)
    cursor = conn.cursor()
    
    # Cria tabela users com todos os campos (se não existir)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            baby_name TEXT,
            email_verified INTEGER DEFAULT 0,
            email_verification_token TEXT,
            reset_password_token TEXT,
            reset_password_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Migração: adiciona colunas só se não existirem (evita duplicação/erro)
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "email_verified" not in columns:
        print("DEBUG - TENTANDO ADICIONAR email_verified")
        cursor.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
    if "email_verification_token" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email_verification_token TEXT")
    if "reset_password_token" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_password_token TEXT")
    if "reset_password_expires" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_password_expires TIMESTAMP")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacinas_tomadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            vacina_nome TEXT NOT NULL,
            data_tomada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Tabela para histórico de conversas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            pergunta TEXT NOT NULL,
            resposta TEXT NOT NULL,
            categoria TEXT,
            fonte TEXT,
            alertas TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Índice para melhorar performance nas buscas por user_id
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_conversas_user_id ON conversas(user_id)
    ''')
    
    # Tabela para informações pessoais extraídas das conversas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            nome_usuario TEXT,
            nome_bebe TEXT,
            informacoes_pessoais TEXT,
            preferencias TEXT,
            ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def _populate_vaccine_reference(cursor):
    """
    Popula tabela de referência de vacinas com dados do calendário PNI 2026
    Baseado em docs/calendario-vacinacao-pni-2026.md
    """
    vaccines = [
        # Ao nascer
        ('BCG', 'BCG', 0, 0, 1, 'Bacilo Calmette-Guérin', 'Formas graves de tuberculose (meningite tuberculosa e tuberculose miliar)', 0),
        ('HEP_B_1', 'Hepatite B', 0, 0, 1, 'Hepatite B - 1ª dose', 'Hepatite B e suas complicações (cirrose, câncer de fígado)', 0),
        
        # 2 meses
        ('PENTA_1', 'Pentavalente (DTP + Hib + Hepatite B)', 2, 0, 1, 'Pentavalente - 1ª dose', 'Difteria, Tétano, Coqueluche, Meningite por Hib, Hepatite B (2ª dose)', 0),
        ('VIP_1', 'VIP (Vacina Inativada Poliomielite)', 2, 0, 1, 'VIP - 1ª dose', 'Poliomielite (paralisia infantil)', 0),
        ('ROTA_1', 'Rotavírus Humano', 2, 0, 1, 'Rotavírus - 1ª dose', 'Diarreia grave causada por rotavírus', 0),
        ('PNEUMO_1', 'Pneumocócica 10-valente (Conjugada)', 2, 0, 1, 'Pneumocócica - 1ª dose', 'Meningite, pneumonia, otite média e outras infecções por pneumococos', 0),
        
        # 3 meses
        ('MENINGO_C_1', 'Meningocócica C (Conjugada)', 3, 0, 1, 'Meningocócica C - 1ª dose', 'Meningite e outras doenças graves causadas por Neisseria meningitidis sorogrupo C', 0),
        
        # 4 meses
        ('PENTA_2', 'Pentavalente (DTP + Hib + Hepatite B)', 4, 0, 2, 'Pentavalente - 2ª dose', 'Difteria, Tétano, Coqueluche, Hib, Hepatite B (3ª dose)', 0),
        ('VIP_2', 'VIP (Vacina Inativada Poliomielite)', 4, 0, 2, 'VIP - 2ª dose', 'Poliomielite', 0),
        ('ROTA_2', 'Rotavírus Humano', 4, 0, 2, 'Rotavírus - 2ª dose', 'Diarreia grave por rotavírus', 0),
        ('PNEUMO_2', 'Pneumocócica 10-valente (Conjugada)', 4, 0, 2, 'Pneumocócica - 2ª dose', 'Infecções por pneumococos', 0),
        
        # 5 meses
        ('MENINGO_C_2', 'Meningocócica C (Conjugada)', 5, 0, 2, 'Meningocócica C - 2ª dose', 'Meningite meningocócica C', 0),
        
        # 6 meses
        ('PENTA_3', 'Pentavalente (DTP + Hib + Hepatite B)', 6, 0, 3, 'Pentavalente - 3ª dose', 'Difteria, Tétano, Coqueluche, Hib, Hepatite B (3ª dose)', 0),
        ('VOP_3', 'VOP (Vacina Oral Poliomielite)', 6, 0, 3, 'VOP - 3ª dose', 'Poliomielite (última dose da série primária)', 0),
        ('INFLUENZA_1', 'Influenza (Gripe)', 6, 0, 1, 'Influenza - 1ª dose', 'Gripe e suas complicações (deve ser repetida anualmente)', 0),
        
        # 9 meses
        ('FEBRE_AMARELA', 'Febre Amarela', 9, 0, 1, 'Febre Amarela - Dose única', 'Febre amarela (reforço aos 4 anos)', 0),
        
        # 12 meses
        ('TRIPLICE_VIRAL_1', 'Tríplice Viral (SCR)', 12, 0, 1, 'Tríplice Viral - 1ª dose', 'Sarampo, Caxumba e Rubéola', 0),
        ('PNEUMO_REFORCO', 'Pneumocócica 10-valente (Conjugada)', 12, 0, 0, 'Pneumocócica - Reforço', 'Infecções por pneumococos (última dose da série primária)', 0),
        ('MENINGO_C_REFORCO', 'Meningocócica C (Conjugada)', 12, 0, 0, 'Meningocócica C - Reforço', 'Meningite meningocócica C (última dose da série primária)', 0),
    ]
    
    cursor.executemany('''
        INSERT INTO vaccine_reference 
        (vaccine_code, vaccine_name, age_months, age_days, dose_number, description, protects_against, is_optional)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', vaccines)

# Inicializa DB na startup
init_db()

# Funções auxiliares
def _normalize_email(s):
    """Única fonte de verdade: strip + lower para e-mail. Usar ao salvar e ao buscar."""
    if s is None:
        return ''
    return str(s).strip().lower()

def generate_token(length=32):
    """Gera um token seguro"""
    return secrets.token_urlsafe(length)

def _email_configured():
    """Retorna True se Resend ou SMTP (MAIL_*) estiver configurado."""
    return bool(os.environ.get("RESEND_API_KEY", "").strip()) or bool(
        app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD")
    )

def send_email(to, subject, body, sender=None):
    """Envia um email. Prioridade: Resend > Flask-Mail (Gmail/SMTP)."""
    try:
        # 1. Resend (3.000/mês grátis) - prioridade quando RESEND_API_KEY está definido
        resend_key = os.environ.get("RESEND_API_KEY", "").strip()
        if resend_key:
            try:
                import requests as _req
                from_addr = sender or os.environ.get("RESEND_FROM") or os.environ.get("MAIL_DEFAULT_SENDER") or "Sophia <onboarding@resend.dev>"
                if "@" in str(from_addr) and "<" not in str(from_addr):
                    from_addr = f"Sophia <{from_addr}>"
                payload = {
                    "from": from_addr,
                    "to": [to],
                    "subject": subject,
                    "html": body.replace("\n", "<br>") if body else subject,
                }
                r = _req.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                    json=payload,
                    timeout=15,
                )
                if 200 <= r.status_code < 300:
                    logger.info(f"[EMAIL] ✅ Enviado via Resend | Para: {to} | Assunto: {subject}")
                    print(f"[EMAIL] ✅ Enviado via Resend | Para: {to}")
                    return True
                err = r.json() if r.text else {}
                err_msg = err.get('message', err.get('name', str(err)))
                logger.warning(f"[EMAIL] Resend retornou {r.status_code}: {err}")
                print(f"[EMAIL] ⚠️ Resend retornou {r.status_code}: {err_msg}")
                if r.status_code in (403, 422, 429):
                    print(f"[EMAIL]    Dica: Com onboarding@resend.dev você só pode enviar para o email da sua conta Resend.")
                    print(f"[EMAIL]    Para enviar para qualquer email: verifique um domínio em resend.com/domains ou use MAIL_USERNAME/MAIL_PASSWORD (Gmail) no .env")
            except Exception as e:
                logger.warning(f"[EMAIL] Resend falhou, tentando SMTP: {e}")
                print(f"[EMAIL] ⚠️ Resend falhou: {e}")

        # 2. Flask-Mail (Gmail/SMTP) - fallback
        logger.info(f"[EMAIL] 🔍 Iniciando envio de email...")
        logger.info(f"[EMAIL] 🔍 MAIL_USERNAME configurado: {bool(app.config.get('MAIL_USERNAME'))}")
        logger.info(f"[EMAIL] 🔍 MAIL_PASSWORD configurado: {bool(app.config.get('MAIL_PASSWORD'))}")
        print(f"[EMAIL] 🔍 Iniciando envio de email...")
        print(f"[EMAIL] 🔍 MAIL_USERNAME configurado: {bool(app.config.get('MAIL_USERNAME'))}")
        print(f"[EMAIL] 🔍 MAIL_PASSWORD configurado: {bool(app.config.get('MAIL_PASSWORD'))}")
        
        if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
            # Para Gmail, usa o MAIL_USERNAME como sender (domínio verificado)
            # Para outros provedores, usa o sender fornecido ou o padrão
            mail_username = app.config['MAIL_USERNAME']
            if '@gmail.com' in mail_username.lower() or '@googlemail.com' in mail_username.lower():
                # Gmail: usa o próprio email como sender (mais confiável)
                from_email = sender or mail_username
            else:
                # Outros provedores: usa sender fornecido ou padrão
                from_email = sender or app.config['MAIL_DEFAULT_SENDER']
            
            logger.info(f"[EMAIL] 🔍 Usando sender: {from_email}")
            print(f"[EMAIL] 🔍 Usando sender: {from_email}")
            
            # Valida se o sender é do mesmo domínio do MAIL_USERNAME quando possível
            if '@' in mail_username and '@' in from_email:
                mail_domain = mail_username.split('@')[1]
                sender_domain = from_email.split('@')[1]
                if mail_domain != sender_domain:
                    logger.warning(f"[EMAIL] ⚠️ Sender ({from_email}) não corresponde ao domínio do MAIL_USERNAME ({mail_domain}). Pode cair no spam.")
                    print(f"[EMAIL] ⚠️ AVISO: Sender ({from_email}) diferente do domínio configurado ({mail_domain}). Use o mesmo domínio para melhor entrega.")
            
            logger.info(f"[EMAIL] 🔍 Criando mensagem... Destinatário: {to}")
            print(f"[EMAIL] 🔍 Criando mensagem... Destinatário: {to}")
            
            msg = Message(subject, recipients=[to], body=body, sender=from_email)
            
            logger.info(f"[EMAIL] 🔍 Enviando mensagem via Flask-Mail...")
            print(f"[EMAIL] 🔍 Enviando mensagem via Flask-Mail...")
            
            # Verifica se estamos em um contexto de aplicação Flask
            from flask import has_app_context
            if not has_app_context():
                logger.error(f"[EMAIL] ❌ ERRO: Não estamos em um contexto de aplicação Flask!")
                print(f"[EMAIL] ❌ ERRO: Não estamos em um contexto de aplicação Flask!")
                raise RuntimeError("Flask application context required to send email")
            
            # Tenta enviar o email
            try:
                mail.send(msg)
                logger.info(f"[EMAIL] ✅ Enviado com sucesso de: {from_email} | Para: {to} | Assunto: {subject}")
                print(f"[EMAIL] ✅ Enviado de: {from_email} | Para: {to} | Assunto: {subject}")
                return True
            except Exception as send_error:
                logger.error(f"[EMAIL] ❌ Erro ao chamar mail.send(): {send_error}", exc_info=True)
                print(f"[EMAIL] ❌ Erro ao chamar mail.send(): {send_error}")
                raise  # Re-levanta a exceção para ser capturada pelo except externo
        else:
            # Nenhum provedor configurado
            logger.warning(f"[EMAIL] EMAIL NÃO CONFIGURADO - nenhum email enviado. Para: {to}, Assunto: {subject}")
            print(f"[EMAIL] ⚠️ Nenhum email enviado.")
            print(f"[EMAIL]    Configure RESEND_API_KEY (Resend - 3.000/mês grátis) ou MAIL_USERNAME/MAIL_PASSWORD (Gmail) no .env")
            print(f"[EMAIL]    Para: {to} | Assunto: {subject}")
            return False
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[EMAIL] ❌ Erro ao enviar email: {error_msg}", exc_info=True)
        print(f"[EMAIL] ❌ Erro ao enviar email: {error_msg}")
        
        # Mensagens de erro mais específicas
        if "authentication failed" in error_msg.lower() or "535" in error_msg or "535-5.7.8" in error_msg:
            print(f"[EMAIL] ⚠️ Erro de autenticação!")
            print(f"[EMAIL]    - Verifique se o email e senha estão corretos")
            if "@gmail.com" in str(app.config.get('MAIL_USERNAME', '')).lower():
                print(f"[EMAIL]    - 🔴 IMPORTANTE PARA GMAIL: Use 'Senha de App' (não a senha normal da conta)")
                print(f"[EMAIL]      1. Ative Verificação em Duas Etapas: https://myaccount.google.com/security")
                print(f"[EMAIL]      2. Gere Senha de App: https://myaccount.google.com/apppasswords")
                print(f"[EMAIL]      3. Use essa senha no MAIL_PASSWORD do arquivo .env")
            else:
                print(f"[EMAIL]    - Verifique se a senha está correta")
            print(f"[EMAIL]    - Erro completo: {error_msg}")
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            print(f"[EMAIL] ⚠️ Erro de conexão!")
            print(f"[EMAIL]    - Verifique sua conexão com a internet")
            print(f"[EMAIL]    - Verifique se o servidor SMTP está correto: {app.config.get('MAIL_SERVER')}")
            print(f"[EMAIL]    - Verifique se a porta está correta: {app.config.get('MAIL_PORT')}")
        elif "ssl" in error_msg.lower() or "tls" in error_msg.lower():
            print(f"[EMAIL] ⚠️ Erro de SSL/TLS!")
            print(f"[EMAIL]    - Tente mudar MAIL_USE_TLS para False e usar porta 465")
        
        import traceback
        traceback.print_exc()
        # Retorna False para indicar falha
        logger.error(f"[EMAIL] ❌ send_email retornou False - email NÃO foi enviado")
        print(f"[EMAIL] ❌ send_email retornou False - email NÃO foi enviado")
        return False

def send_verification_email(email, name, token):
    """Envia email de verificação"""
    # Em produção, usar a URL real do site
    # Se BASE_URL contiver ngrok, avisa que pode cair no spam
    base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
    
    # Detecta se está usando ngrok
    if 'ngrok' in base_url.lower():
        logger.warning(f"[EMAIL] ⚠️ Usando ngrok ({base_url}). Links podem cair no spam.")
        print(f"[EMAIL] ⚠️ AVISO: Usando ngrok. E-mails podem cair no spam ou não serem entregues.")
        print(f"[EMAIL]    - Em produção, use um domínio próprio e verificado")
    
    verification_url = f"{base_url}/api/verify-email?token={token}"
    
    subject = "Ó, verificação de email da sua conta – Sophia 💕"
    body = f"""
Olá {name}! 💕

Boas-vindas à Sophia – sua companheira no puerpério! 🤱

Para ativar sua conta e começar a usar o app, é só clicar no link abaixo:

{verification_url}

Este link vale por 24 horas.

Se não foi você quem criou esta conta, pode ignorar este email.

Com carinho,
Equipe Sophia 💕
"""
    # Chama send_email e verifica se realmente foi enviado
    result = send_email(email, subject, body)
    if not result:
        # Se falhou, levanta exceção com mais detalhes
        error_detail = "Falha ao enviar email de verificação. Verifique os logs do servidor para mais detalhes."
        logger.error(f"[EMAIL] ❌ {error_detail}")
        print(f"[EMAIL] ❌ {error_detail}")
        print(f"[EMAIL] Verifique se MAIL_USERNAME e MAIL_PASSWORD estão configurados corretamente no .env")
        raise Exception(error_detail)
    return result

def send_password_reset_email(email, name, token):
    """Envia email de recuperação de senha. Retorna True se enviado, False caso contrário."""
    base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
    reset_url = f"{base_url}/reset-password?token={token}"
    
    subject = "Ó, email de recuperação de senha – Sophia 🔐"
    body = f"""
Olá {name}! 💕

Você pediu para redefinir sua senha. Clica no link abaixo para criar uma nova senha:

{reset_url}

Este link vale por 1 hora.

Se não foi você quem pediu, pode ignorar este email.

Com carinho,
Equipe Sophia 💕
"""
    return send_email(email, subject, body)

# User loader para Flask-Login (usa current_app.config para compatibilidade com blueprints)
@login_manager.user_loader
def load_user(user_id):
    db_path = current_app.config.get("DB_PATH", DB_PATH)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[4])
    return None

# Carrega os arquivos JSON
def carregar_dados():
    """
    Carrega automaticamente TODOS os arquivos JSON.
    Primeiro tenta do diretório backend (local), depois do diretório dados.
    Usa os.listdir() para identificar arquivos .json automaticamente.
    Retorna dicionários vazios se algum arquivo não for encontrado, mas registra avisos detalhados.
    """
    results = {}
    missing_files = []
    errors = []
    arquivos_carregados = 0
    total_itens = 0
    
    # Lista de diretórios para procurar (prioridade: backend local, depois dados)
    diretorios_procurar = [
        os.path.dirname(__file__),  # Diretório backend (prioridade)
        BASE_PATH  # Diretório dados (fallback)
    ]
    
    # Conjunto de arquivos já carregados (para evitar duplicatas)
    arquivos_carregados_set = set()
    
    # Procura em cada diretório
    for diretorio in diretorios_procurar:
        if not os.path.exists(diretorio):
            continue
        
        # Carrega automaticamente TODOS os arquivos .json do diretório
        try:
            arquivos_json = [f for f in os.listdir(diretorio) if f.endswith('.json')]
            logger.info(f"[OK] 🔍 Encontrados {len(arquivos_json)} arquivo(s) .json no diretório: {diretorio}")
            print(f"[OK] 🔍 Encontrados {len(arquivos_json)} arquivo(s) .json no diretório: {diretorio}")
        except Exception as e:
            logger.warning(f"[ERRO] Falha ao listar arquivos do diretório {diretorio}: {e}")
            print(f"[ERRO] Falha ao listar arquivos do diretório {diretorio}: {e}")
            continue
        
        # Carrega cada arquivo JSON encontrado (se ainda não foi carregado)
        for file_name in arquivos_json:
            # Pula se já foi carregado de outro diretório
            if file_name in arquivos_carregados_set:
                continue
            
            file_path = os.path.join(diretorio, file_name)
            try:
                if not os.path.exists(file_path):
                    continue
                
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results[file_name] = data
                    item_count = len(data) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0
                    total_itens += item_count
                    arquivos_carregados += 1
                    arquivos_carregados_set.add(file_name)
                    logger.info(f"[OK] ✅ {file_name} carregado de {diretorio} ({item_count} itens)")
                    print(f"[OK] ✅ {file_name} carregado de {diretorio} ({item_count} itens)")
            except json.JSONDecodeError as e:
                errors.append(f"{file_name}: Erro de JSON - {str(e)}")
                logger.error(f"[ERRO] ❌ Erro ao decodificar JSON em {file_name}: {e}")
                print(f"[ERRO] ❌ Falha ao ler {file_name}: {e}")
                if file_name not in results:
                    results[file_name] = {}
            except Exception as e:
                errors.append(f"{file_name}: {str(e)}")
                logger.error(f"[ERRO] ❌ Erro ao carregar {file_name}: {e}")
                print(f"[ERRO] ❌ Falha ao ler {file_name}: {e}")
                if file_name not in results:
                    results[file_name] = {}
    
    # Resumo do carregamento
    print("=" * 60)
    if arquivos_carregados > 0:
        print(f"[OK] ✅ {arquivos_carregados} arquivo(s) carregado(s) com sucesso!")
        print(f"[OK] ✅ Total de {total_itens} itens carregados da base de conhecimento")
        logger.info(f"[OK] ✅ Base de conhecimento carregada com sucesso! {arquivos_carregados} arquivos, {total_itens} itens")
    else:
        print(f"[ERRO] ⚠️ Nenhum arquivo foi carregado!")
        logger.warning("[ERRO] ⚠️ Nenhum arquivo foi carregado!")
    
    if missing_files:
        logger.warning(f"[ERRO] ⚠️ AVISO: {len(missing_files)} arquivo(s) não encontrado(s): {', '.join(missing_files)}")
        print(f"[ERRO] ⚠️ AVISO: {len(missing_files)} arquivo(s) não encontrado(s): {', '.join(missing_files)}")
    
    if errors:
        logger.error(f"[ERRO] ❌ ERRO: {len(errors)} erro(s) ao carregar arquivos:")
        print(f"[ERRO] ❌ ERRO: {len(errors)} erro(s) ao carregar arquivos:")
        for error in errors:
            logger.error(f"   - {error}")
            print(f"   - {error}")
    
    if not missing_files and not errors and arquivos_carregados > 0:
        print("[OK] ✅ Base de conhecimento carregada com sucesso!")
        logger.info("[OK] ✅ Todos os arquivos JSON foram carregados com sucesso!")
    print("=" * 60)
    
    # Retorna na ordem esperada (compatibilidade com código existente)
    return (
        results.get("base_conhecimento.json", {}),
        results.get("mensagens_apoio.json", {}),
        results.get("alertas.json", {}),
        results.get("telefones_uteis.json", {}),
        results.get("guias_praticos.json", {}),
        results.get("cuidados_gestacao.json", {}),
        results.get("cuidados_pos_parto.json", {}),
        results.get("vacinas_mae.json", {}),
        results.get("vacinas_bebe.json", {})
    )

# Validação de startup
def validate_startup():
    """Valida se todos os arquivos essenciais existem antes de iniciar a aplicação"""
    required_files = [
        "base_conhecimento.json",
        "mensagens_apoio.json",
        "alertas.json",
        "telefones_uteis.json",
        "guias_praticos.json",
        "cuidados_gestacao.json",
        "cuidados_pos_parto.json",
        "vacinas_mae.json",
        "vacinas_bebe.json"
    ]
    
    missing = []
    for file_name in required_files:
        file_path = os.path.join(BASE_PATH, file_name)
        if not os.path.exists(file_path):
            missing.append(file_name)
    
    if missing:
        logger.warning("=" * 60)
        logger.warning("⚠️  AVISO DE INICIALIZAÇÃO")
        logger.warning("=" * 60)
        logger.warning(f"⚠️  {len(missing)} arquivo(s) JSON não encontrado(s):")
        for file_name in missing:
            logger.warning(f"   - {file_name}")
        logger.warning("⚠️  O chatbot pode não funcionar corretamente!")
        logger.warning("⚠️  Verifique se os arquivos estão no diretório: " + BASE_PATH)
        logger.warning("=" * 60)
        return False
    
    logger.info("✅ Validação de startup: Todos os arquivos necessários foram encontrados")
    return True

# Valida arquivos antes de carregar
validate_startup()

# Carrega os dados
logger.info("📦 Carregando arquivos JSON...")
base_conhecimento, mensagens_apoio, alertas, telefones_uteis, guias_praticos, cuidados_gestacao, cuidados_pos_parto, vacinas_mae, vacinas_bebe = carregar_dados()

# Dicionário global BASE_CONHECIMENTO que unifica todos os dados carregados
BASE_CONHECIMENTO = {
    "base_conhecimento": base_conhecimento,
    "mensagens_apoio": mensagens_apoio,
    "alertas": alertas,
    "telefones_uteis": telefones_uteis,
    "guias_praticos": guias_praticos,
    "cuidados_gestacao": cuidados_gestacao,
    "cuidados_pos_parto": cuidados_pos_parto,
    "vacinas_mae": vacinas_mae,
    "vacinas_bebe": vacinas_bebe
}

logger.info(f"[OK] ✅ BASE_CONHECIMENTO criado com {len(BASE_CONHECIMENTO)} categorias")
print(f"[OK] ✅ BASE_CONHECIMENTO criado com {len(BASE_CONHECIMENTO)} categorias")

# Expõe dados e helpers para blueprints (health_bp: vacinas, admin, perf; auth_bp: email, tokens)
app.vacinas_mae = vacinas_mae
app.vacinas_bebe = vacinas_bebe
app._admin_allowed = _admin_allowed
app._perf_ovr_boot_ms = None
app._perf_ovr_boot_at = None
app._normalize_email = _normalize_email
app.generate_token = generate_token
app._email_configured = _email_configured
app.send_verification_email = send_verification_email
app.send_password_reset_email = send_password_reset_email
app._login_rate_limit_check = _login_rate_limit_check
app._login_rate_limit_clear = _login_rate_limit_clear
# Chat/IA: expõe para backend.blueprints.chat_routes (chat_bp)
app.base_conhecimento = base_conhecimento
app.alertas = alertas
app.telefones_uteis = telefones_uteis
app.guias_praticos = guias_praticos
app.cuidados_gestacao = cuidados_gestacao
app.cuidados_pos_parto = cuidados_pos_parto

# Histórico de conversas em memória (cache para performance)
# As conversas também são salvas no banco de dados para persistência
conversas = {}
app.conversas = conversas

# Instância global do chatbot será criada após a definição da classe ChatbotPuerperio

# Funções para persistência de conversas e informações pessoais
def salvar_conversa_db(user_id, pergunta, resposta, categoria=None, fonte=None, alertas=None):
    """Salva uma conversa no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversas (user_id, pergunta, resposta, categoria, fonte, alertas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, pergunta, resposta, categoria, fonte, json.dumps(alertas) if alertas else None))
        conn.commit()
        conn.close()
        logger.info(f"[DB] ✅ Conversa salva no banco para user_id: {user_id}")
    except Exception as e:
        logger.error(f"[DB] ❌ Erro ao salvar conversa no banco: {e}")

def carregar_historico_db(user_id, limit=50):
    """Carrega histórico de conversas do banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pergunta, resposta, categoria, fonte, alertas, timestamp
            FROM conversas
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        historico = []
        for row in reversed(rows):  # Reverte para ordem cronológica
            pergunta, resposta, categoria, fonte, alertas_str, timestamp = row
            alertas = json.loads(alertas_str) if alertas_str else None
            historico.append({
                "pergunta": pergunta,
                "resposta": resposta,
                "categoria": categoria,
                "fonte": fonte,
                "alertas": alertas,
                "timestamp": timestamp
            })
        
        logger.info(f"[DB] ✅ Histórico carregado do banco: {len(historico)} mensagens para user_id: {user_id}")
        return historico
    except Exception as e:
        logger.error(f"[DB] ❌ Erro ao carregar histórico do banco: {e}")
        return []

app.carregar_historico_db = carregar_historico_db
app.salvar_conversa_db = salvar_conversa_db

def extrair_informacoes_pessoais(pergunta, resposta, user_id, historico=None):
    """Extrai informações pessoais das conversas usando padrões melhorados"""
    try:
        # Busca informações no histórico completo também
        texto_para_analisar = pergunta
        if historico:
            # Adiciona todas as perguntas do histórico para análise
            for msg in historico:
                texto_para_analisar += " " + msg.get('pergunta', '')
        
        texto_para_analisar_lower = texto_para_analisar.lower()
        
        # Padrões melhorados para extrair nome do usuário
        nome_patterns = [
            r'(?:eu sou o|eu sou a)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s*,\s*seu|\s*,\s*sua|\s*$)',  # "Eu sou o Bruno Cartolano, seu criador"
            r'(?:me chamo|meu nome é|me chamo de)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:eu sou)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s*,\s*seu|\s*,\s*sua|\s*$)',  # "Eu sou Bruno, seu criador"
        ]
        
        # Padrões para nome do bebê
        bebe_patterns = [
            r'(?:meu bebê|meu filho|minha filha|o bebê|a bebê|o neném|a neném|meu neném|minha neném)\s+(?:se chama|chama|é|tem o nome de|chama-se)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:bebê|filho|filha|neném)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        # Padrões para informações sobre o projeto/motivo
        projeto_patterns = [
            r'(?:estou|estou criando|estou desenvolvendo|estou fazendo|estou trabalhando|trabalho|trabalho em|desenvolvo|desenvolvi|fiz|fiz um|fiz uma|criei|criei um|criei uma|estou criando um|estou criando uma)\s+(?:site|aplicativo|app|projeto|sistema|ferramenta|plataforma|chatbot|bot|assistente)',
            r'(?:criar|desenvolver|fazer|trabalhar|trabalhando)\s+(?:um|uma|o|a)\s+(?:site|aplicativo|app|projeto|sistema|ferramenta|plataforma|chatbot|bot|assistente)',
            r'(?:para|com o objetivo de|com a finalidade de|para ajudar|para auxiliar)\s+(?:mães|mamães|gestantes|mulheres|pessoas)',
        ]
        
        # Busca nome do usuário - padrões melhorados
        nome_usuario = None
        for pattern in nome_patterns:
            matches = re.finditer(pattern, texto_para_analisar, re.IGNORECASE)
            for match in matches:
                nome_candidato = match.group(1).strip()
                # Remove vírgulas e palavras que não são parte do nome
                nome_candidato = re.sub(r',.*$', '', nome_candidato).strip()
                # Filtra nomes muito curtos ou que são palavras comuns
                palavras_comuns = ['sophia', 'oi', 'olá', 'ola', 'hey', 'aqui', 'estou', 'sou', 'é', 'criador', 'desenvolvedor', 'programador', 'seu', 'sua']
                if len(nome_candidato) >= 2 and nome_candidato.lower() not in palavras_comuns and not any(pal in nome_candidato.lower() for pal in palavras_comuns):
                    nome_usuario = nome_candidato
                    break
            if nome_usuario:
                break
        
        # Busca nome do bebê
        nome_bebe = None
        for pattern in bebe_patterns:
            match = re.search(pattern, texto_para_analisar, re.IGNORECASE)
            if match:
                nome_bebe = match.group(1).strip()
                break
        
        # Busca informações sobre projeto/motivo
        tem_projeto = False
        for pattern in projeto_patterns:
            if re.search(pattern, texto_para_analisar_lower, re.IGNORECASE):
                tem_projeto = True
                break
        
        # Extrai informações adicionais do texto
        informacoes_adicionais = []
        if tem_projeto:
            informacoes_adicionais.append("A usuária está criando/desenvolvendo um site/projeto relacionado a puerpério/gestação")
        
        # Se encontrou informações, salva no banco
        if nome_usuario or nome_bebe or informacoes_adicionais:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Verifica se já existe registro
            cursor.execute('SELECT nome_usuario, nome_bebe, informacoes_pessoais FROM user_info WHERE user_id = ?', (user_id,))
            existing = cursor.fetchone()
            
            # Prepara informações pessoais em JSON
            info_pessoais_dict = {}
            if informacoes_adicionais:
                info_pessoais_dict['projeto'] = informacoes_adicionais[0]
            
            info_pessoais_json = json.dumps(info_pessoais_dict) if info_pessoais_dict else None
            
            if existing:
                # Atualiza informações existentes
                nome_atual, bebe_atual, info_atual_str = existing
                nome_final = nome_usuario or nome_atual
                bebe_final = nome_bebe or bebe_atual
                
                # Mescla informações adicionais
                if info_atual_str:
                    try:
                        info_atual_dict = json.loads(info_atual_str)
                        info_atual_dict.update(info_pessoais_dict)
                        info_pessoais_json = json.dumps(info_atual_dict)
                    except:
                        info_pessoais_json = json.dumps(info_pessoais_dict) if info_pessoais_dict else info_atual_str
                
                cursor.execute('''
                    UPDATE user_info 
                    SET nome_usuario = ?, nome_bebe = ?, informacoes_pessoais = ?, ultima_atualizacao = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (nome_final, bebe_final, info_pessoais_json, user_id))
            else:
                # Cria novo registro
                cursor.execute('''
                    INSERT INTO user_info (user_id, nome_usuario, nome_bebe, informacoes_pessoais)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, nome_usuario, nome_bebe, info_pessoais_json))
            
            conn.commit()
            conn.close()
            logger.info(f"[DB] ✅ Informações pessoais atualizadas: nome={nome_usuario}, bebê={nome_bebe}, projeto={tem_projeto}")
            
    except Exception as e:
        logger.error(f"[DB] ❌ Erro ao extrair informações pessoais: {e}", exc_info=True)

def obter_informacoes_pessoais(user_id):
    """Obtém informações pessoais do usuário do banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT nome_usuario, nome_bebe, informacoes_pessoais, preferencias FROM user_info WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            nome_usuario, nome_bebe, info_pessoais, preferencias = row
            return {
                "nome_usuario": nome_usuario,
                "nome_bebe": nome_bebe,
                "informacoes_pessoais": json.loads(info_pessoais) if info_pessoais else None,
                "preferencias": json.loads(preferencias) if preferencias else None
            }
        return None
    except Exception as e:
        logger.error(f"[DB] ❌ Erro ao obter informações pessoais: {e}")
        return None

def filtrar_recomendacoes_medicas(resposta):
    """
    Filtra e bloqueia recomendações médicas perigosas nas respostas.
    Detecta padrões de recomendações de medicamentos, posologia, tratamentos ou diagnósticos.
    Retorna a resposta filtrada com avisos de segurança se necessário.
    """
    if not resposta:
        return resposta
    
    resposta_lower = resposta.lower()
    
    # Padrões perigosos que indicam recomendações médicas
    padroes_perigosos = [
        # Recomendações de medicamentos
        r'tome\s+(?:o|a|os|as)?\s*(?:medicamento|remédio|fármaco|comprimido|pílula|pomada|gotas|injeção)',
        r'use\s+(?:o|a|os|as)?\s*(?:medicamento|remédio|fármaco|comprimido|pílula|pomada|gotas|injeção)',
        r'recomendo\s+(?:o|a|os|as)?\s*(?:medicamento|remédio|fármaco)',
        r'sugiro\s+(?:o|a|os|as)?\s*(?:medicamento|remédio|fármaco)',
        r'indico\s+(?:o|a|os|as)?\s*(?:medicamento|remédio|fármaco)',
        r'pode\s+tomar\s+(?:o|a|os|as)?\s*(?:medicamento|remédio|fármaco)',
        r'deve\s+tomar\s+(?:o|a|os|as)?\s*(?:medicamento|remédio|fármaco)',
        
        # Posologia e doses
        r'\d+\s*(?:mg|ml|g|comprimidos?|pílulas?|gotas?)\s+(?:por|ao|de)\s+(?:dia|semana|mês)',
        r'tome\s+\d+',
        r'use\s+\d+',
        r'dose\s+de\s+\d+',
        r'\d+\s+vezes\s+ao\s+dia',
        r'\d+\s+vezes\s+por\s+dia',
        r'a\s+cada\s+\d+\s+horas?',
        
        # Tratamentos específicos
        r'tratamento\s+com\s+(?:medicamento|remédio|fármaco)',
        r'fazer\s+tratamento\s+com',
        r'iniciar\s+tratamento',
        
        # Diagnósticos
        r'você\s+tem\s+\w+',
        r'você\s+está\s+com\s+\w+',
        r'isso\s+é\s+(?:um|uma)\s+\w+',
        r'parece\s+ser\s+\w+',
        r'provavelmente\s+é\s+\w+',
        
        # Suplementos e vitaminas
        r'tome\s+(?:suplemento|vitamina|ferro|cálcio|vitamina\s+d)',
        r'use\s+(?:suplemento|vitamina|ferro|cálcio|vitamina\s+d)',
        r'recomendo\s+(?:suplemento|vitamina)',
    ]
    
    # Verifica se há padrões perigosos
    for padrao in padroes_perigosos:
        if re.search(padrao, resposta_lower):
            logger.warning(f"[FILTRO] ⚠️⚠️⚠️ RECOMENDAÇÃO MÉDICA DETECTADA E BLOQUEADA: {padrao}")
            logger.warning(f"[FILTRO] Resposta original: {resposta[:200]}...")
            
            # Remove a recomendação perigosa e adiciona aviso de segurança
            resposta_filtrada = re.sub(padrao, '', resposta, flags=re.IGNORECASE)
            resposta_filtrada = re.sub(r'\s+', ' ', resposta_filtrada).strip()
            
            # Adiciona aviso obrigatório
            aviso_seguranca = "\n\n⚠️ IMPORTANTE: Este conteúdo é apenas informativo e não substitui uma consulta médica profissional. NUNCA tome medicamentos, suplementos ou faça tratamentos sem orientação médica. Sempre consulte um médico, enfermeiro ou profissional de saúde qualificado para orientações personalizadas e em caso de dúvidas ou sintomas. Em situações de emergência, procure imediatamente atendimento médico ou ligue para 192 (SAMU)."
            
            if aviso_seguranca not in resposta_filtrada:
                resposta_filtrada += aviso_seguranca
            
            return resposta_filtrada
    
    return resposta

# Palavras-chave para alertas médicos
palavras_alerta = ["sangramento", "febre", "dor", "inchaço", "tristeza", "depressão", "emergência"]
# Palavras/frases que devem ser ignoradas nos alertas (falsos positivos)
palavras_ignorar_alertas = ["criador", "desenvolvedor", "developer", "programador", "criei", "criou", "fiz", "feito", "sou seu", "sou o"]

# Termos de risco emocional/suicídio - RISCO ALTO (desejo explícito de morte)
# ⚠️⚠️⚠️ LISTA FORTALECIDA - Mais variações e termos comuns ⚠️⚠️⚠️
TERMOS_RISCO_ALTO = [
    # Desejo explícito de morte
    "quero morrer", "quer morrer", "queria morrer", "quero me matar", "quer me matar", "queria me matar",
    "me matar", "me mataria", "vou me matar", "vou morrer", "vou acabar com tudo",
    "acabar com tudo", "acabar com a vida", "acabar com minha vida", "acabar com tudo isso",
    "tirar a própria vida", "tirar minha vida", "tirar a vida", "tirar minha própria vida",
    "sumir do mundo", "desaparecer do mundo", "sumir para sempre", "desaparecer para sempre",
    "prefiro morrer", "morrer seria melhor", "seria melhor morrer", "seria melhor se eu morresse",
    "não quero mais viver", "nao quero mais viver", "não quero viver", "nao quero viver",
    "cansada de viver", "cansado de viver", "cansada da vida", "cansado da vida",
    "quero desaparecer para sempre", "quer desaparecer para sempre",
    "não vejo saída", "nao vejo saida", "sem saída", "sem saida", "não há saída", "nao ha saida",
    "chega pra mim", "chega para mim", "chega de tudo", "chega de viver",
    "não aguento mais viver", "nao aguento mais viver", "não aguento viver", "nao aguento viver",
    "vou me suicidar", "vou suicidar", "pensar em suicídio", "pensar em suicidio", "pensando em suicídio",
    "planejando me matar", "planejo me matar", "planejo me suicidar",
    # Variações adicionais
    "quero acabar com tudo", "quer acabar com tudo", "vou acabar comigo", "acabar comigo",
    "não quero existir", "nao quero existir", "quero parar de existir", "quer parar de existir",
    "melhor estar morta", "melhor estar morto", "preferia estar morta", "preferia estar morto",
    "quero que tudo acabe", "quer que tudo acabe", "quero que acabe tudo",
    "não vale mais a pena viver", "nao vale mais a pena viver", "não vale a pena viver",
    "não tem mais razão para viver", "nao tem mais razao para viver", "sem razão para viver",
    "quero pular da ponte", "quer pular da ponte", "vou pular da ponte",
    "quero me jogar", "quer se jogar", "vou me jogar", "vou me jogar da ponte",
    "quero tomar remédio demais", "quer tomar remédio demais", "vou tomar remédio demais",
    "quero me enforcar", "quer se enforcar", "vou me enforcar",
    "quero cortar os pulsos", "quer cortar os pulsos", "vou cortar os pulsos"
]

# Termos de risco emocional - RISCO LEVE (tristeza, desesperança, mas sem desejo explícito de morte)
# ⚠️⚠️⚠️ LISTA FORTALECIDA - Mais variações e termos comuns ⚠️⚠️⚠️
TERMOS_RISCO_LEVE = [
    # Desesperança e cansaço
    "não aguento mais", "nao aguento mais", "não aguento", "nao aguento",
    "não vale mais a pena", "nao vale mais a pena", "não vale a pena", "nao vale a pena",
    "não tem mais sentido", "nao tem mais sentido", "sem sentido", "não faz sentido",
    "melhor se eu não existisse", "seria melhor se eu não existisse", "seria melhor não existir",
    "ninguém sentiria minha falta", "ninguem sentiria minha falta", "ninguém sentiria falta",
    "todo mundo seria mais feliz", "todos seriam mais feliz", "todos seriam mais felizes sem mim",
    "quero desaparecer", "quer desaparecer", "queria desaparecer", "quero sumir",
    "sumir", "desaparecer", "sumir daqui", "desaparecer daqui",
    "estou perdendo a esperança", "perdendo a esperança", "sem esperança", "sem esperanças",
    "não consigo mais", "nao consigo mais", "não consigo", "nao consigo",
    "tô mal", "to mal", "estou mal", "estou muito mal", "estou péssima", "estou péssimo",
    "não aguento mais isso", "nao aguento mais isso", "não aguento mais nada",
    # Variações adicionais
    "não tenho mais forças", "nao tenho mais forcas", "sem forças", "sem forcas",
    "estou esgotada", "estou esgotado", "esgotada", "esgotado",
    "não vejo futuro", "nao vejo futuro", "sem futuro", "não há futuro",
    "estou sozinha", "estou sozinho", "me sinto sozinha", "me sinto sozinho",
    "ninguém me entende", "ninguem me entende", "ninguém entende", "ninguem entende",
    "não tenho ninguém", "nao tenho ninguem", "sem ninguém", "sem ninguem",
    "estou desesperada", "estou desesperado", "desesperada", "desesperado",
    "não sei mais o que fazer", "nao sei mais o que fazer", "não sei o que fazer",
    "estou perdida", "estou perdido", "perdida", "perdido",
    "não consigo mais lidar", "nao consigo mais lidar", "não consigo lidar",
    "estou no limite", "no limite", "chegando no limite",
    "não aguento mais essa vida", "nao aguento mais essa vida", "não aguento essa vida",
    "estou pensando em desistir", "pensando em desistir", "quero desistir", "quer desistir"
]

# Expressões que EXCLUEM alerta (falsos positivos - análise de contexto)
EXPRESOES_EXCLUSAO = [
    "quase morri de rir", "quase morri de tanto rir", "morri de rir", "morrendo de rir",
    "quase morri", "quase morreu", "quase matei", "quase matou",
    "quero matar você", "quer matar", "vou matar você", "vou te matar",
    "quero que você morra", "quer que eu morra",
    "não quero que você morra", "não quero que morra",
    "filme sobre", "livro sobre", "história sobre", "notícia sobre",
    "personagem que", "personagem morreu", "personagem se matou",
    "ele morreu", "ela morreu", "eles morreram", "morreu no", "morreu em",
    "criador", "desenvolvedor", "programador", "fiz", "criei", "desenvolvi",
    "de rir", "de tanto rir", "de rir muito"
]

# ============================================================================
# BUFFER DE CONVERSA EMOCIONAL - MEMÓRIA TEMPORÁRIA
# ============================================================================

# Histórico emocional: armazena últimas 5 mensagens por usuário
HISTORICO_EMOCIONAL = {}  # {user_id: [mensagem1, mensagem2, ...]}

# Contador de alertas: quantas vezes o usuário gerou alerta
CONTADOR_ALERTA = {}  # {user_id: contador}

# Flag de sessão em alerta: mantém estado ativo/inativo
SESSION_ALERT = {}  # {user_id: {"ativo": True/False, "nivel": "alto"/"leve", "timestamp": ...}}
CONTEXT_TAG_HISTORY = {}  # {user_id: [tag1, tag2, ...]} - Histórico de tags de contexto

# Respostas progressivas conforme repetição de risco
RESPOSTAS_RISCO = {
    "alto": [
        # ⚠️⚠️⚠️ RESPOSTAS DIRETAS E CONTUNDENTES - CVV (188) SEMPRE PRESENTE ⚠️⚠️⚠️
        "Sinto muito que você esteja passando por um momento tão difícil. 💛\n\n**Você não está sozinho(a).**\n\n**Por favor, ligue AGORA para o CVV – 188** (gratuito, sigiloso e disponível 24 horas).\n\nOu acesse: **https://cvv.org.br/chat/**\n\nEles podem te ouvir com cuidado neste momento. 💛\n\nSe quiser, posso ficar aqui com você enquanto você busca apoio, tudo bem?",
        "Eu me preocupo muito com você. **Sua vida importa e tem valor.** 💛\n\n**Por favor, ligue AGORA para o CVV – 188** ou acesse **https://cvv.org.br/chat/**\n\nEles estão disponíveis 24 horas para te ouvir com cuidado e sem julgamento.\n\nVocê não precisa enfrentar isso sozinho(a).",
        "Percebo que você está em sofrimento profundo. 💛\n\n**Você merece cuidado e ajuda profissional IMEDIATA.**\n\n**Ligue AGORA para o CVV – 188** (gratuito e sigiloso) ou acesse **https://cvv.org.br/chat/**\n\nEles podem te ouvir neste momento. Estou aqui também se quiser conversar enquanto busca apoio.",
        "Vejo que você está passando por um momento muito difícil. 💛\n\n**Por favor, entre em contato IMEDIATAMENTE com o CVV – 188** (gratuito e sigiloso) ou acesse **https://cvv.org.br/chat/**\n\nEles estão disponíveis 24 horas e podem te ouvir AGORA.\n\n**Por favor, não desista. Há pessoas que se importam com você e querem te ajudar.**",
        "Sua vida tem valor imenso. 💛\n\n**Você não está sozinho(a).**\n\n**Ligue AGORA para o CVV – 188** ou acesse **https://cvv.org.br/chat/**\n\nEles podem te ouvir com cuidado neste momento, sem julgamento.\n\n**Por favor, não desista. Há ajuda disponível.**"
    ],
    "leve": [
        # ⚠️⚠️⚠️ RESPOSTAS EMPÁTICAS MAS DIRETAS - CVV (188) SEMPRE PRESENTE ⚠️⚠️⚠️
        "Parece que as coisas estão difíceis para você. 💛\n\n**Você não precisa enfrentar isso sozinho(a).**\n\n**O CVV (188) pode te ouvir AGORA** – é gratuito, sigiloso e disponível 24 horas.\n\nOu acesse: **https://cvv.org.br/chat/**\n\nEstou aqui também se quiser conversar mais sobre como você está se sentindo.",
        "Sei que é um momento delicado. 💛\n\n**O CVV (188) pode oferecer uma escuta segura e anônima** sempre que você precisar.\n\nLigue **188** ou acesse **https://cvv.org.br/chat/**\n\nEles estão disponíveis 24 horas para te ouvir.\n\nEstou aqui também se quiser conversar.",
        "Você não precisa enfrentar isso sozinho(a). 💛\n\n**O CVV pode te ouvir a qualquer hora:** ligue **188** (gratuito e sigiloso) ou acesse **https://cvv.org.br/chat/**\n\nEles estão disponíveis 24 horas.\n\nSe quiser, também posso continuar conversando com você aqui.",
        "Entendo que você esteja se sentindo assim. 💛\n\n**Se quiser conversar com alguém especializado, pode ligar para o CVV – 188** (gratuito e sigiloso) ou acessar **https://cvv.org.br/chat/**\n\nEles estão disponíveis 24 horas para te ouvir.\n\nEstou aqui também se quiser conversar mais sobre como você está se sentindo.",
        "Você não está sozinho(a). 💛\n\nSei que pode ser muito difícil, mas **há pessoas que podem te ajudar.**\n\n**O CVV (188) está disponível 24 horas** para te ouvir – ligue **188** ou acesse **https://cvv.org.br/chat/**\n\nEstou aqui também se quiser conversar."
    ]
}

# Frases que indicam melhora (desativam alerta)
FRASES_MELHORA = [
    "já estou bem", "ja estou bem", "estou bem agora", "estou melhor",
    "já melhorei", "ja melhorei", "melhorei", "estou ok", "estou ok agora",
    "já passou", "ja passou", "passou", "tudo bem agora", "tudo ok",
    "não precisa se preocupar", "nao precisa se preocupar", "não se preocupe",
    "estava brincando", "era brincadeira", "só estava testando",
    "era só teste", "era teste", "testando", "não é sério", "nao é serio",
    "estou bem", "tudo bem", "tudo certo", "tudo tranquilo"
]

def adicionar_ao_historico_emocional(user_id, mensagem):
    """
    Adiciona mensagem ao histórico emocional do usuário (máximo 5 itens).
    """
    if user_id not in HISTORICO_EMOCIONAL:
        HISTORICO_EMOCIONAL[user_id] = []
    
    HISTORICO_EMOCIONAL[user_id].append(mensagem)
    
    # Mantém apenas as últimas 5 mensagens
    if len(HISTORICO_EMOCIONAL[user_id]) > 5:
        HISTORICO_EMOCIONAL[user_id] = HISTORICO_EMOCIONAL[user_id][-5:]
    
    logger.info(f"[HISTORICO_EMOCIONAL] ✅ Mensagem adicionada ao histórico (user_id: {user_id}, total: {len(HISTORICO_EMOCIONAL[user_id])})")

def analisar_tendencia_emocional(user_id):
    """
    Analisa o padrão de sentimentos no histórico emocional.
    Retorna: {"tendencia": "alto"/"leve"/"melhora"/"normal", "risco_detectado": True/False}
    """
    if user_id not in HISTORICO_EMOCIONAL or len(HISTORICO_EMOCIONAL[user_id]) < 1:
        return {"tendencia": "normal", "risco_detectado": False}
    
    historico = HISTORICO_EMOCIONAL[user_id]
    mensagens_recentes = historico[-3:] if len(historico) >= 3 else historico
    
    # Verifica se há frases de melhora nas mensagens recentes
    mensagens_lower = [msg.lower() for msg in mensagens_recentes]
    tem_melhora = any(any(frase in msg for frase in FRASES_MELHORA) for msg in mensagens_lower)
    
    if tem_melhora:
        logger.info(f"[TENDENCIA] ✅ Tendência de melhora detectada no histórico")
        return {"tendencia": "melhora", "risco_detectado": False}
    
    # Analisa cada mensagem recente para risco
    contador_risco_alto = 0
    contador_risco_leve = 0
    
    for mensagem in mensagens_recentes:
        # Chama sem user_id para evitar recursão infinita
        resultado = detectar_alerta_risco_suicidio(mensagem, user_id=None, usar_tendencia=False)
        if resultado.get("alerta"):
            if resultado.get("nivel") == "alto":
                contador_risco_alto += 1
            elif resultado.get("nivel") == "leve":
                contador_risco_leve += 1
    
    # Se 3 mensagens seguidas têm risco alto, tendência é alta
    if contador_risco_alto >= 3:
        logger.warning(f"[TENDENCIA] ⚠️⚠️⚠️ Tendência de RISCO ALTO detectada (3+ mensagens com risco alto)")
        return {"tendencia": "alto", "risco_detectado": True}
    elif contador_risco_alto >= 2:
        logger.warning(f"[TENDENCIA] ⚠️ Tendência de RISCO ALTO detectada (2 mensagens com risco alto)")
        return {"tendencia": "alto", "risco_detectado": True}
    elif contador_risco_leve >= 3:
        logger.warning(f"[TENDENCIA] ⚠️ Tendência de RISCO LEVE detectada (3+ mensagens com risco leve)")
        return {"tendencia": "leve", "risco_detectado": True}
    elif contador_risco_leve >= 2:
        logger.info(f"[TENDENCIA] ⚠️ Tendência de RISCO LEVE detectada (2 mensagens com risco leve)")
        return {"tendencia": "leve", "risco_detectado": True}
    
    return {"tendencia": "normal", "risco_detectado": False}

def gerar_resposta_progressiva(user_id, nivel):
    """
    Gera resposta progressiva conforme o número de vezes que o usuário está em estado de alerta.
    """
    # Inicializa contador se não existir
    if user_id not in CONTADOR_ALERTA:
        CONTADOR_ALERTA[user_id] = 0
    
    # Incrementa contador
    CONTADOR_ALERTA[user_id] += 1
    contador = CONTADOR_ALERTA[user_id]
    
    # Seleciona resposta baseada no nível e contador
    respostas_disponiveis = RESPOSTAS_RISCO.get(nivel, RESPOSTAS_RISCO["leve"])
    
    # Usa o contador para escolher uma resposta (cicla entre as respostas)
    indice_resposta = (contador - 1) % len(respostas_disponiveis)
    resposta_base = respostas_disponiveis[indice_resposta]
    
    # ⚠️⚠️⚠️ GARANTE QUE CVV (188) ESTÁ SEMPRE PRESENTE ⚠️⚠️⚠️
    # Verifica se a resposta base já contém CVV/188
    tem_cvv = "188" in resposta_base or "cvv" in resposta_base.lower()
    
    # Adiciona informações adicionais se for o primeiro alerta ou múltiplos
    if contador == 1:
        if nivel == "alto":
            if not tem_cvv:
                resposta_final = (
                    f"{resposta_base}\n\n"
                    "**Por favor, ligue AGORA para o CVV – 188** (gratuito e sigiloso) ou acesse **https://cvv.org.br/chat/**\n\n"
                    "Eles estão disponíveis 24 horas e podem te ouvir AGORA. 💛\n\n"
                    "Se quiser, posso ficar com você por aqui enquanto você busca apoio, tudo bem?"
                )
            else:
                resposta_final = (
                    f"{resposta_base}\n\n"
                    "Se quiser, posso ficar com você por aqui enquanto você busca apoio, tudo bem?"
                )
        else:
            if not tem_cvv:
                resposta_final = (
                    f"{resposta_base}\n\n"
                    "**O CVV (188) está disponível 24 horas** para te ouvir – ligue **188** ou acesse **https://cvv.org.br/chat/**\n\n"
                    "Estou aqui também se quiser conversar mais sobre como você está se sentindo."
                )
            else:
                resposta_final = (
                    f"{resposta_base}\n\n"
                    "Estou aqui também se quiser conversar mais sobre como você está se sentindo."
                )
    elif contador >= 3:
        # Se já houve 3+ alertas, reforça a importância de buscar ajuda
        if not tem_cvv:
            resposta_final = (
                f"{resposta_base}\n\n"
                "**Percebo que você continua em sofrimento. Por favor, considere buscar ajuda profissional.**\n\n"
                "**O CVV (188) está disponível 24 horas** para te ouvir com cuidado e sem julgamento.\n\n"
                "Ligue **188** ou acesse **https://cvv.org.br/chat/**"
            )
        else:
            resposta_final = (
                f"{resposta_base}\n\n"
                "**Percebo que você continua em sofrimento. Por favor, considere buscar ajuda profissional.**\n\n"
                "**O CVV (188) está disponível 24 horas** para te ouvir com cuidado e sem julgamento."
            )
    else:
        # Se não tem CVV na resposta base, adiciona
        if not tem_cvv:
            resposta_final = (
                f"{resposta_base}\n\n"
                "**O CVV (188) está disponível 24 horas** para te ouvir – ligue **188** ou acesse **https://cvv.org.br/chat/**"
            )
        else:
            resposta_final = resposta_base
    
    logger.info(f"[RESPOSTA_PROGRESSIVA] ✅ Resposta gerada (nível: {nivel}, contador: {contador})")
    return resposta_final

def atualizar_session_alert(user_id, ativo, nivel=None):
    """
    Atualiza o estado de alerta da sessão do usuário.
    """
    if user_id not in SESSION_ALERT:
        SESSION_ALERT[user_id] = {"ativo": False, "nivel": None, "timestamp": None}
    
    SESSION_ALERT[user_id]["ativo"] = ativo
    if nivel:
        SESSION_ALERT[user_id]["nivel"] = nivel
    SESSION_ALERT[user_id]["timestamp"] = datetime.now().isoformat()
    
    logger.info(f"[SESSION_ALERT] ✅ Estado atualizado (user_id: {user_id}, ativo: {ativo}, nivel: {nivel})")

def verificar_melhora_usuario(mensagem):
    """
    Verifica se a mensagem indica que o usuário está melhor.
    """
    mensagem_lower = mensagem.lower()
    return any(frase in mensagem_lower for frase in FRASES_MELHORA)

def detectar_alerta_risco_suicidio(mensagem, user_id=None, usar_tendencia=True):
    """
    Detecta mensagens de risco emocional/suicídio com análise de contexto inteligente.
    Classifica o risco como LEVE ou ALTO e retorna resposta apropriada.
    Implementa análise de contexto para evitar falsos positivos.
    Se user_id for fornecido, usa histórico emocional para análise de tendência.
    """
    # ⚠️⚠️⚠️ LOG DE DEBUG PARA VALIDAÇÃO ⚠️⚠️⚠️
    logger.critical(f"[DETECÇÃO_RISCO] 🔍 INICIANDO DETECÇÃO - Mensagem: '{mensagem[:100]}', user_id: {user_id}")
    print(f"[DETECÇÃO_RISCO] 🔍 INICIANDO DETECÇÃO - Mensagem: '{mensagem[:100]}', user_id: {user_id}")
    
    mensagem_lower = mensagem.lower().strip()
    
    # Verifica se há indicação de melhora (prioritário)
    if user_id and verificar_melhora_usuario(mensagem):
        logger.info(f"[ALERTA] ✅ Usuário indicou melhora - desativando alerta")
        if user_id in SESSION_ALERT:
            atualizar_session_alert(user_id, False, None)
            # Reseta contador se usuário melhorou
            if user_id in CONTADOR_ALERTA:
                CONTADOR_ALERTA[user_id] = 0
        return {"alerta": False, "tipo": None, "nivel": None, "melhora": True}
    
    # Remove acentos para detecção mais robusta
    mensagem_normalizada = ''.join(
        char for char in unicodedata.normalize('NFD', mensagem_lower)
        if unicodedata.category(char) != 'Mn'
    )
    
    # PRIMEIRO: Verifica se há expressões que EXCLUEM o alerta (falsos positivos)
    for exclusao in EXPRESOES_EXCLUSAO:
        exclusao_normalizada = ''.join(
            char for char in unicodedata.normalize('NFD', exclusao.lower())
            if unicodedata.category(char) != 'Mn'
        )
        # Se encontrar expressão de exclusão, NÃO aciona alerta
        if exclusao_normalizada in mensagem_normalizada or exclusao in mensagem_lower:
            # Log reduzido para performance
            logger.info(f"[ALERTA] Excluído por contexto: '{exclusao}'")
            return {"alerta": False, "tipo": None, "nivel": None}
    
    # SEGUNDO: Verifica termos de RISCO ALTO (desejo explícito de morte)
    risco_alto_detectado = False
    termo_alto_encontrado = None
    # ⚠️⚠️⚠️ OTIMIZAÇÃO: Loop otimizado - sem logs dentro do loop para performance ⚠️⚠️⚠️
    for termo in TERMOS_RISCO_ALTO:
        termo_normalizado = ''.join(
            char for char in unicodedata.normalize('NFD', termo.lower())
            if unicodedata.category(char) != 'Mn'
        )
        # Verifica se o termo está na mensagem normalizada OU na mensagem original (lowercase)
        if termo_normalizado in mensagem_normalizada or termo in mensagem_lower:
            risco_alto_detectado = True
            termo_alto_encontrado = termo
            # Log apenas após detectar (fora do loop para não afetar performance)
            logger.critical(f"[ALERTA] ⚠️⚠️⚠️ RISCO ALTO detectado! Termo: '{termo}'")
            break
    
    # TERCEIRO: Se não encontrou risco alto, verifica RISCO LEVE
    risco_leve_detectado = False
    termo_leve_encontrado = None
    if not risco_alto_detectado:
        for termo in TERMOS_RISCO_LEVE:
            termo_normalizado = ''.join(
                char for char in unicodedata.normalize('NFD', termo.lower())
                if unicodedata.category(char) != 'Mn'
            )
            if termo_normalizado in mensagem_normalizada or termo in mensagem_lower:
                risco_leve_detectado = True
                termo_leve_encontrado = termo
                logger.warning(f"[ALERTA] ⚠️ RISCO LEVE detectado! Termo: '{termo}'")
                print(f"[ALERTA] ⚠️ RISCO LEVE detectado!")
                print(f"[ALERTA] Termo: '{termo}'")
                break
    
    # QUARTO: Se user_id fornecido e usar_tendencia=True, analisa tendência emocional
    nivel_final = None
    if user_id and usar_tendencia and (risco_alto_detectado or risco_leve_detectado):
        tendencia = analisar_tendencia_emocional(user_id)
        if tendencia["tendencia"] == "alto":
            nivel_final = "alto"
            logger.warning(f"[ALERTA] 📊 Tendência emocional indica RISCO ALTO")
        elif tendencia["tendencia"] == "leve" and not risco_alto_detectado:
            nivel_final = "leve"
        elif risco_alto_detectado:
            nivel_final = "alto"
        elif risco_leve_detectado:
            nivel_final = "leve"
    else:
        if risco_alto_detectado:
            nivel_final = "alto"
        elif risco_leve_detectado:
            nivel_final = "leve"
    
    # ⚠️⚠️⚠️ RESPOSTA BASEADA NO NÍVEL DE RISCO - DIRETA E CONTUNDENTE ⚠️⚠️⚠️
    # CVV (188) SEMPRE presente e destacado
    # ⚠️⚠️⚠️ OTIMIZAÇÃO: Logs reduzidos para performance - apenas críticos ⚠️⚠️⚠️
    if nivel_final == "alto":
        # Gera resposta progressiva se user_id fornecido
        if user_id:
            resposta_seguranca = gerar_resposta_progressiva(user_id, "alto")
        else:
            # Resposta padrão para risco ALTO - DIRETA e CONTUNDENTE
            resposta_seguranca = (
                "Sinto muito por você estar passando por um momento tão difícil. 💛\n\n"
                "**Você não está sozinho(a).** Eu me importo com você e quero te ajudar a buscar apoio.\n\n"
                "**Por favor, ligue AGORA para o CVV – 188** (gratuito e sigiloso) ou acesse **https://cvv.org.br/chat/**\n\n"
                "Eles estão disponíveis 24 horas e podem te ouvir com cuidado **AGORA MESMO**. 💛\n\n"
                "Se quiser, posso ficar com você por aqui enquanto você busca apoio, tudo bem?\n\n"
                "**Por favor, não desista. Há pessoas que se importam com você e querem te ajudar.**"
            )
        # Log crítico apenas (não bloqueia)
        logger.critical(f"[ALERTA] RISCO ALTO - Resposta gerada")
        return {
            "resposta": resposta_seguranca,
            "alerta": True,
            "tipo": "risco_suicidio",
            "nivel": "alto",
            "termo_detectado": termo_alto_encontrado
        }
    elif nivel_final == "leve":
        # Gera resposta progressiva se user_id fornecido
        if user_id:
            resposta_seguranca = gerar_resposta_progressiva(user_id, "leve")
        else:
            # Resposta padrão para risco LEVE - EMPÁTICA mas DIRETA
            resposta_seguranca = (
                "Sinto muito que você esteja se sentindo assim. 💛\n\n"
                "**Você não está sozinho(a).** Sei que pode ser muito difícil, mas há pessoas que podem te ajudar.\n\n"
                "**Se você quiser conversar com alguém especializado, pode ligar para o CVV – 188** (gratuito e sigiloso) "
                "ou acessar **https://cvv.org.br/chat/**\n\n"
                "Eles estão disponíveis 24 horas para te ouvir. 💛\n\n"
                "Estou aqui também se quiser conversar mais sobre como você está se sentindo."
            )
        return {
            "resposta": resposta_seguranca,
            "alerta": True,
            "tipo": "risco_emocional",
            "nivel": "leve",
            "termo_detectado": termo_leve_encontrado
        }
    
    return {"alerta": False, "tipo": None, "nivel": None}

# ============================================================================
# RF.EMO.009 - TRIAGEM EMOCIONAL: MÃE ANSIOSA
# Integração com BMad Core para detecção e apoio a mães ansiosas
# ============================================================================

# Carrega dados de triagem emocional
TRIAGEM_EMOCIONAL = {}
try:
    triagem_path = os.path.join(BASE_PATH, "triagem_emocional.json")
    if os.path.exists(triagem_path):
        with open(triagem_path, "r", encoding="utf-8") as f:
            TRIAGEM_EMOCIONAL = json.load(f)
            logger.info("[TRIAGEM] ✅ Dados de triagem emocional carregados")
    else:
        # Tenta no diretório backend
        triagem_path_backend = os.path.join(os.path.dirname(__file__), "triagem_emocional.json")
        if os.path.exists(triagem_path_backend):
            with open(triagem_path_backend, "r", encoding="utf-8") as f:
                TRIAGEM_EMOCIONAL = json.load(f)
                logger.info("[TRIAGEM] ✅ Dados de triagem emocional carregados do backend")
except Exception as e:
    logger.warning(f"[TRIAGEM] ⚠️ Erro ao carregar triagem emocional: {e}")
    TRIAGEM_EMOCIONAL = {}

def detectar_triagem_ansiedade(mensagem, user_id=None):
    """
    RF.EMO.009 - Detecta sinais de ansiedade em mães gestantes ou no puerpério.
    Integrado com BMad Core para triagem emocional.
    
    Retorna:
    {
        "detectado": True/False,
        "nivel": "leve"/"moderada"/"alta"/None,
        "perfil": "mae_ansiosa"/None,
        "resposta": "resposta personalizada",
        "recursos": [lista de recursos de apoio]
    }
    """
    if not TRIAGEM_EMOCIONAL or "perfis_emocionais" not in TRIAGEM_EMOCIONAL:
        return {"detectado": False}
    
    perfil_ansiosa = TRIAGEM_EMOCIONAL.get("perfis_emocionais", {}).get("mae_ansiosa", {})
    if not perfil_ansiosa:
        return {"detectado": False}
    
    padroes = perfil_ansiosa.get("padroes_deteccao", {})
    mensagem_lower = mensagem.lower()
    
    # Remove acentos para detecção mais robusta
    mensagem_normalizada = ''.join(
        char for char in unicodedata.normalize('NFD', mensagem_lower)
        if unicodedata.category(char) != 'Mn'
    )
    
    # Verifica palavras-chave
    palavras_chave = padroes.get("palavras_chave", [])
    frases_completas = padroes.get("frases_completas", [])
    contextos = padroes.get("contextos", [])
    
    # Contador de indicadores encontrados
    indicadores_encontrados = 0
    palavras_encontradas = []
    
    # Verifica palavras-chave
    for palavra in palavras_chave:
        palavra_normalizada = ''.join(
            char for char in unicodedata.normalize('NFD', palavra.lower())
            if unicodedata.category(char) != 'Mn'
        )
        if palavra_normalizada in mensagem_normalizada or palavra in mensagem_lower:
            indicadores_encontrados += 1
            palavras_encontradas.append(palavra)
    
    # Verifica frases completas (mais específicas, peso maior)
    frases_encontradas = []
    for frase in frases_completas:
        frase_normalizada = ''.join(
            char for char in unicodedata.normalize('NFD', frase.lower())
            if unicodedata.category(char) != 'Mn'
        )
        if frase_normalizada in mensagem_normalizada or frase in mensagem_lower:
            indicadores_encontrados += 2  # Frases completas têm peso maior
            frases_encontradas.append(frase)
    
    # Verifica contexto (gestação, parto, bebê, etc.)
    tem_contexto = False
    for contexto in contextos:
        contexto_normalizado = ''.join(
            char for char in unicodedata.normalize('NFD', contexto.lower())
            if unicodedata.category(char) != 'Mn'
        )
        if contexto_normalizado in mensagem_normalizada or contexto in mensagem_lower:
            tem_contexto = True
            break
    
    # Se não tem contexto relevante, pode ser ansiedade não relacionada à maternidade
    # Mas ainda assim detectamos se houver muitos indicadores
    if not tem_contexto and indicadores_encontrados < 3:
        return {"detectado": False}
    
    # Se não encontrou indicadores suficientes
    if indicadores_encontrados == 0:
        return {"detectado": False}
    
    # Determina nível de ansiedade baseado nos indicadores
    nivel = None
    if indicadores_encontrados >= 5 or len(frases_encontradas) >= 2:
        nivel = "alta"
    elif indicadores_encontrados >= 3 or len(frases_encontradas) >= 1:
        nivel = "moderada"
    elif indicadores_encontrados >= 1:
        nivel = "leve"
    
    # Busca resposta apropriada
    niveis_ansiedade = perfil_ansiosa.get("niveis_ansiedade", {})
    resposta_data = niveis_ansiedade.get(nivel, {})
    respostas_disponiveis = resposta_data.get("respostas", [])
    
    # Seleciona resposta (usa contador se user_id fornecido)
    resposta = ""
    if respostas_disponiveis:
        if user_id:
            # Usa contador para variar respostas
            contador_ansiedade = CONTADOR_ALERTA.get(user_id, 0)
            indice = contador_ansiedade % len(respostas_disponiveis)
            resposta = respostas_disponiveis[indice]
        else:
            resposta = respostas_disponiveis[0]
    else:
        # Resposta padrão se não houver específica
        resposta = (
            f"Entendo que você esteja se sentindo ansiosa. 💛\n\n"
            f"É normal ter preocupações durante a gestação e nos primeiros meses com o bebê.\n\n"
            f"**Se a ansiedade estiver te incomodando muito, considere:**\n"
            f"- Conversar com seu médico ou enfermeiro\n"
            f"- Buscar apoio de um profissional de saúde mental\n"
            f"- Praticar técnicas de respiração e relaxamento\n\n"
            f"**Para apoio emocional imediato:**\n"
            f"- **CVV (188)** - disponível 24 horas, gratuito e sigiloso\n"
            f"- **Disque Saúde (136)** - orientação em saúde"
        )
    
    # Busca recursos de apoio
    recursos_apoio = perfil_ansiosa.get("recursos_apoio", {})
    telefones = recursos_apoio.get("telefones", [])
    orientacoes = recursos_apoio.get("orientacoes", [])
    
    logger.info(f"[TRIAGEM] ✅ Ansiedade detectada - Nível: {nivel}, Indicadores: {indicadores_encontrados}")
    
    return {
        "detectado": True,
        "nivel": nivel,
        "perfil": "mae_ansiosa",
        "resposta": resposta,
        "recursos": {
            "telefones": telefones,
            "orientacoes": orientacoes
        },
        "indicadores_encontrados": indicadores_encontrados,
        "palavras_encontradas": palavras_encontradas[:5],  # Limita a 5 para não sobrecarregar
        "frases_encontradas": frases_encontradas
    }

app.detectar_triagem_ansiedade = detectar_triagem_ansiedade

# ============================================================================
# CLASSE: StemmerPortugues - Normalização de palavras em português
# ============================================================================
class StemmerPortugues:
    """
    Stemmer para português brasileiro.
    Usa NLTK RSLPStemmer se disponível, caso contrário usa regras básicas.
    """
    def __init__(self):
        self.stemmer = None
        self.use_nltk = False
        
        if NLTK_AVAILABLE:
            try:
                self.stemmer = RSLPStemmer()
                self.use_nltk = True
                logger.info("[STEMmer] ✅ NLTK RSLPStemmer inicializado com sucesso")
            except Exception as e:
                logger.warning(f"[STEMmer] ⚠️ Falha ao inicializar NLTK: {e}")
                self.use_nltk = False
        
        # Regras básicas de stemming para português (fallback)
        self.regras_sufixos = [
            ('ações', 'ação'), ('ões', 'ão'), ('ões', 'ao'),
            ('amentos', 'amento'), ('imentos', 'imento'),
            ('adas', 'ada'), ('idas', 'ida'), ('adas', 'ar'), ('idas', 'ir'),
            ('ados', 'ado'), ('idos', 'ido'), ('ados', 'ar'), ('idos', 'ir'),
            ('ando', 'ar'), ('indo', 'ir'), ('endo', 'er'),
            ('aria', 'ar'), ('eria', 'er'), ('iria', 'ir'),
            ('ava', 'ar'), ('eva', 'er'), ('iva', 'ir'),
            ('ei', 'ar'), ('ou', 'ar'),
            ('am', 'ar'), ('em', 'er'), ('im', 'ir'),
            ('ar', ''), ('er', ''), ('ir', ''),
            ('s', ''),  # Remove plural
        ]
    
    def stem(self, palavra):
        """
        Retorna o radical (stem) de uma palavra.
        """
        if not palavra or len(palavra) < 3:
            return palavra.lower()
        
        palavra_lower = palavra.lower()
        
        # Se NLTK disponível, usa RSLPStemmer
        if self.use_nltk and self.stemmer:
            try:
                return self.stemmer.stem(palavra_lower)
            except:
                pass
        
        # Fallback: regras básicas
        for sufixo, substituicao in self.regras_sufixos:
            if palavra_lower.endswith(sufixo):
                return palavra_lower[:-len(sufixo)] + substituicao
        
        return palavra_lower
    
    def stem_texto(self, texto):
        """
        Retorna lista de stems de um texto.
        """
        # Remove acentos e normaliza
        texto_normalizado = ''.join(
            char for char in unicodedata.normalize('NFD', texto.lower())
            if unicodedata.category(char) != 'Mn'
        )
        
        # Extrai palavras (apenas letras, mínimo 3 caracteres)
        palavras = re.findall(r'\b[a-záàâãéêíóôõúç]{3,}\b', texto_normalizado)
        
        # Aplica stemming
        stems = [self.stem(palavra) for palavra in palavras]
        
        return stems

# ============================================================================
# CLASSE: IndiceInvertido - Índice invertido para busca rápida
# ============================================================================
class IndiceInvertido:
    """
    Índice invertido para busca eficiente na base de conhecimento.
    Estrutura: palavra_stem -> [(categoria, peso), ...]
    """
    def __init__(self, base_conhecimento, stemmer):
        self.base = base_conhecimento
        self.stemmer = stemmer
        self.indice = defaultdict(list)  # palavra_stem -> [(categoria, peso), ...]
        self.categorias_info = {}  # categoria -> {pergunta, resposta, texto_completo}
        self.construir_indice()
    
    def construir_indice(self):
        """
        Constrói o índice invertido a partir da base de conhecimento.
        """
        logger.info("[INDICE] 🔨 Construindo índice invertido...")
        total_palavras = 0
        
        for categoria, conteudo in self.base.items():
            pergunta = conteudo.get("pergunta", "")
            resposta = conteudo.get("resposta", "")
            texto_completo = f"{pergunta} {resposta}".lower()
            
            # Armazena informações da categoria
            self.categorias_info[categoria] = {
                "pergunta": pergunta,
                "resposta": resposta,
                "texto_completo": texto_completo
            }
            
            # Extrai stems do texto completo
            stems = self.stemmer.stem_texto(texto_completo)
            
            # Extrai stems da pergunta (peso maior)
            stems_pergunta = self.stemmer.stem_texto(pergunta)
            
            # Conta frequência de palavras
            contador_stems = Counter(stems)
            contador_pergunta = Counter(stems_pergunta)
            
            # Adiciona ao índice com pesos
            # ⚠️⚠️⚠️ AJUSTE: Palavras na pergunta têm peso 3.0, na resposta peso 1.0 (aumentado de 2.0 para 3.0)
            # Isso força o item cuja pergunta original é mais próxima do input do usuário a ter pontuação maior
            stems_processados = set()
            for stem in stems:
                if stem in stems_processados:
                    continue
                stems_processados.add(stem)
                
                # Calcula peso: palavra na pergunta = 3.0, na resposta = 1.0
                peso = 1.0
                if stem in contador_pergunta:
                    peso = 3.0 + (contador_pergunta[stem] * 0.15)  # Bonus por frequência na pergunta (aumentado)
                else:
                    peso = 1.0 + (contador_stems[stem] * 0.05)  # Bonus por frequência na resposta
                
                self.indice[stem].append((categoria, peso))
                total_palavras += 1
        
        logger.info(f"[INDICE] ✅ Índice construído: {len(self.indice)} palavras únicas, {total_palavras} entradas totais")
        logger.info(f"[INDICE] ✅ {len(self.categorias_info)} categorias indexadas")
    
    def buscar(self, query, threshold=0.35, top_k=3):
        """
        Busca na base usando o índice invertido.
        Retorna: (resposta, categoria, similaridade) ou (None, None, 0)
        
        Args:
            query: Pergunta do usuário
            threshold: Score mínimo para retornar resultado
            top_k: Número de melhores resultados para considerar (reranking)
        """
        # Extrai stems da query
        stems_query = self.stemmer.stem_texto(query)
        
        if not stems_query:
            return None, None, 0
        
        # Conta quantas vezes cada categoria aparece (score)
        scores_categorias = defaultdict(float)
        stems_encontrados = defaultdict(set)  # categoria -> {stems encontrados}
        
        # Para cada stem da query, busca no índice
        for stem in stems_query:
            if stem in self.indice:
                # Para cada categoria que contém essa palavra
                for categoria, peso in self.indice[stem]:
                    scores_categorias[categoria] += peso
                    stems_encontrados[categoria].add(stem)
        
        if not scores_categorias:
            return None, None, 0
        
        # Normaliza scores (divide pelo número de stems na query)
        num_stems_query = len(stems_query)
        scores_normalizados = {}
        for categoria in scores_categorias:
            # Score = (soma de pesos) / (número de stems na query)
            # + bonus por porcentagem de stems encontrados
            porcentagem_match = len(stems_encontrados[categoria]) / num_stems_query
            score_normalizado = (scores_categorias[categoria] / num_stems_query) * (1 + porcentagem_match)
            scores_normalizados[categoria] = score_normalizado
        
        # ⚠️⚠️⚠️ RERANKING: Ordena por score e pega os Top K
        # Isso permite escolher o melhor resultado entre os mais bem pontuados
        categorias_ordenadas = sorted(scores_normalizados.items(), key=lambda x: x[1], reverse=True)
        top_categorias = categorias_ordenadas[:top_k]
        
        if not top_categorias:
            return None, None, 0
        
        # ⚠️⚠️⚠️ RERANKING FINAL: Refina os Top K usando similaridade de strings na pergunta
        # Isso garante que o item cuja pergunta é mais próxima do input do usuário seja escolhido
        pergunta_lower = query.lower()
        melhor_score_reranking = 0
        melhor_categoria_reranking = None
        resultados_reranking = []
        
        for categoria, score_indice in top_categorias:
            if categoria in self.categorias_info:
                pergunta_base = self.categorias_info[categoria]["pergunta"].lower()
                # Calcula similaridade de strings entre pergunta do usuário e pergunta da base
                similaridade_pergunta = difflib.SequenceMatcher(None, pergunta_lower, pergunta_base).ratio()
                
                # ⚠️⚠️⚠️ AJUSTE: Prioriza MUITO MAIS a similaridade da pergunta (50%) vs score do índice (50%)
                # Isso força o sistema a escolher itens cuja pergunta é mais próxima do input do usuário
                # Se similaridade da pergunta for alta (>0.6), aumenta ainda mais o peso
                if similaridade_pergunta > 0.6:
                    # Se similaridade alta, prioriza MUITO a similaridade (70% similaridade, 30% índice)
                    score_reranking = (score_indice * 0.3) + (similaridade_pergunta * 0.7 * 10)  # Multiplica por 10 para escala similar
                else:
                    # Caso contrário, balanceia: 50% índice, 50% similaridade
                    score_reranking = (score_indice * 0.5) + (similaridade_pergunta * 0.5 * 10)  # Multiplica por 10 para escala similar
                
                resultados_reranking.append((categoria, score_reranking, similaridade_pergunta, score_indice))
                
                if score_reranking > melhor_score_reranking:
                    melhor_score_reranking = score_reranking
                    melhor_categoria_reranking = categoria
        
        # Se encontrou resultado no reranking, retorna
        if melhor_categoria_reranking and melhor_score_reranking >= threshold:
            info = self.categorias_info[melhor_categoria_reranking]
            # Log dos Top K para debug
            if len(top_categorias) > 1:
                logger.info(f"[BUSCA] Top {top_k} categorias (antes do reranking): {[(cat, f'{sco:.2f}') for cat, sco in top_categorias[:3]]}")
                # Ordena resultados do reranking por score
                resultados_ordenados = sorted(resultados_reranking, key=lambda x: x[1], reverse=True)
                logger.info(f"[BUSCA] Top {min(3, len(resultados_ordenados))} após reranking: {[(cat, f'score:{sco:.2f}, sim:{sim:.2f}, idx:{idx:.2f}') for cat, sco, sim, idx in resultados_ordenados[:3]]}")
                logger.info(f"[BUSCA] ✅ Melhor categoria após reranking: {melhor_categoria_reranking} (score: {melhor_score_reranking:.2f})")
            return info["resposta"], melhor_categoria_reranking, melhor_score_reranking
        
        # Fallback: retorna o melhor resultado do índice (sem reranking)
        melhor_categoria, score = top_categorias[0]
        if score >= threshold:
            info = self.categorias_info[melhor_categoria]
            return info["resposta"], melhor_categoria, score
        
        return None, None, 0

class ChatbotPuerperio:
    def __init__(self):
        self.base = base_conhecimento
        self.apoio = mensagens_apoio
        self.alertas = alertas
        self.telefones = telefones_uteis
        self.guias = guias_praticos
        
        # Inicializa stemmer e índice invertido
        self.stemmer = StemmerPortugues()
        self.indice_invertido = IndiceInvertido(self.base, self.stemmer)
        logger.info("[ChatbotPuerperio] Stemmer e indice invertido inicializados")
        
        # Controle de repetição de mensagens (por user_id)
        self.ultimas_respostas = {}  # {user_id: [lista das últimas 3 respostas]}
        # Controle de saudação (1 vez por conversa; não repetir acolhimento)
        self.user_greeted = {}  # {user_id: True} após primeira resposta
        
        # Armazena clientes OpenAI e threads por usuário
        self.openai_client = openai_client
        self.assistant_id = OPENAI_ASSISTANT_ID
        self.user_threads = {}  # {user_id: thread_id}
        
        # Armazena cliente Gemini e histórico de conversas por usuário
        self.gemini_model = gemini_model
        self.user_historico_gemini = {}  # {user_id: [lista de mensagens]}
        
        # Armazena cliente Groq
        self.groq_client = groq_client
        self.groq_system_instruction = None
        
        # Carrega system prompt para Groq (se estiver usando Groq)
        if AI_PROVIDER == "groq" and self.groq_client:
            try:
                self.groq_system_instruction = self._carregar_system_prompt()
                if self.groq_system_instruction:
                    logger.info("[GROQ] ✅ System prompt carregado com sucesso para Groq")
                    print("[GROQ] ✅ System prompt carregado com sucesso para Groq")
                else:
                    logger.warning("[GROQ] ⚠️ System prompt vazio para Groq")
                    print("[GROQ] ⚠️ System prompt vazio para Groq")
            except Exception as e:
                logger.error(f"[GROQ] Erro ao carregar system prompt: {e}")
                print(f"[GROQ] Erro ao carregar system prompt: {e}")
        
        # Carrega system prompt para Gemini
        self.gemini_system_instruction = None
        if AI_PROVIDER == "gemini" and self.gemini_model is None and GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                # Carrega system prompt do loader.py
                self.gemini_system_instruction = self._carregar_system_prompt()
                if self.gemini_system_instruction:
                    # Inicializa modelo Gemini com system instruction
                    import google.generativeai as genai
                    genai.configure(api_key=GEMINI_API_KEY)
                    self.gemini_model = genai.GenerativeModel(
                        'gemini-pro',
                        system_instruction=self.gemini_system_instruction
                    )
                    logger.info("[GEMINI] Modelo Gemini inicializado com system prompt")
                    print("[GEMINI] Modelo Gemini inicializado com system prompt")
            except Exception as e:
                logger.error(f"[GEMINI] Erro ao inicializar Gemini no __init__: {e}")
                print(f"[GEMINI] Erro ao inicializar Gemini no __init__: {e}")
                self.gemini_model = None
        elif AI_PROVIDER == "gemini" and self.gemini_model:
            # Se já foi inicializado globalmente, carrega system prompt também
            self.gemini_system_instruction = self._carregar_system_prompt()
            if self.gemini_system_instruction:
                # Reinicializa com system instruction
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=GEMINI_API_KEY)
                    self.gemini_model = genai.GenerativeModel(
                        'gemini-pro',
                        system_instruction=self.gemini_system_instruction
                    )
                    logger.info("[GEMINI] Modelo Gemini reconfigurado com system prompt")
                except Exception as e:
                    logger.warning(f"[GEMINI] Erro ao reconfigurar Gemini: {e}")
        
        # Cria assistente Sophia se não existir (apenas para OpenAI)
        if AI_PROVIDER == "openai" and self.openai_client and not self.assistant_id:
            logger.info(f"[ChatbotPuerperio] Criando assistente Sophia...")
            print(f"[ChatbotPuerperio] Criando assistente Sophia...")
            self.assistant_id = self._criar_assistente_sophia()
            if self.assistant_id:
                logger.info(f"[ChatbotPuerperio] ✅ Assistente criado: {self.assistant_id}")
                print(f"[ChatbotPuerperio] ✅ Assistente criado: {self.assistant_id}")
            else:
                logger.error(f"[ChatbotPuerperio] ❌ Falha ao criar assistente na inicialização")
                print(f"[ChatbotPuerperio] ❌ Falha ao criar assistente na inicialização")
        
        logger.info(f"[ChatbotPuerperio] Inicializado. Provider: {AI_PROVIDER}, OpenAI: {self.openai_client is not None}, Gemini: {self.gemini_model is not None}, Groq: {self.groq_client is not None}")
        print(f"[ChatbotPuerperio] Inicializado. Provider: {AI_PROVIDER}, OpenAI: {self.openai_client is not None}, Gemini: {self.gemini_model is not None}, Groq: {self.groq_client is not None}")
    
    def _carregar_system_prompt(self):
        """Carrega o system prompt do loader.py para uso com Gemini e Groq"""
        try:
            import os
            loader_path = os.path.join(os.path.dirname(__file__), 'loader.py')
            if os.path.exists(loader_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("loader", loader_path)
                loader_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(loader_module)
                load_all = loader_module.load_all
                
                logger.info("[GEMINI] Carregando System Prompt do loader.py...")
                loaded_data = load_all()
                system_prompt = loaded_data.get("system_prompt", "")
                if system_prompt:
                    logger.info("[GEMINI] ✅ System prompt carregado com sucesso")
                    return system_prompt
                else:
                    logger.warning("[GEMINI] ⚠️ System prompt vazio do loader")
            else:
                logger.warning(f"[GEMINI] ⚠️ Loader não encontrado em {loader_path}")
        except Exception as e:
            logger.warning(f"[GEMINI] ⚠️ Erro ao carregar system prompt: {e}. Usando fallback.")
        
        # Fallback: system prompt básico
        return """Você é a Sophia, uma Inteligência Artificial EMPÁTICA, ACOLHEDORA e ESPECIALIZADA EXCLUSIVAMENTE em gestação, parto, pós-parto, vacinação e cuidados maternos. Sempre seja empática, acolhedora e oriente consultar profissionais de saúde quando necessário."""
    
    def _criar_assistente_sophia(self):
        """Cria o assistente Sophia personalizado na OpenAI usando nova arquitetura (loader.py)"""
        if not self.openai_client:
            return None
        
        try:
            # Usa o novo loader.py para carregar Base de Dados + Persona + System Prompt
            instructions = None
            try:
                # Importa o loader (pode estar na mesma pasta ou uma pasta acima)
                import sys
                import os
                loader_path = os.path.join(os.path.dirname(__file__), 'loader.py')
                if os.path.exists(loader_path):
                    # Importa o módulo diretamente
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("loader", loader_path)
                    loader_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(loader_module)
                    load_all = loader_module.load_all
                    
                    logger.info("[SOPHIA] Carregando Base de Dados, Persona e System Prompt (nova arquitetura)...")
                    loaded_data = load_all()
                    
                    # Obtém o system prompt completo já construído pelo loader
                    instructions = loaded_data.get("system_prompt", "")
                    if instructions:
                        logger.info("[SOPHIA] ✅ System prompt carregado com sucesso (nova arquitetura)")
                    else:
                        raise ValueError("System prompt vazio do loader")
                else:
                    raise FileNotFoundError(f"Loader não encontrado em {loader_path}")
            except Exception as loader_error:
                # Fallback: se o loader falhar, usa instruções básicas
                logger.warning(f"[SOPHIA] ⚠️ Erro ao carregar nova arquitetura: {loader_error}. Usando fallback.")
                instructions = None
            
            if not instructions:
                logger.warning("[SOPHIA] ⚠️ System prompt vazio, usando fallback")
                instructions = """Você é a Sophia, uma Inteligência Artificial EMPÁTICA, ACOLHEDORA e ESPECIALIZADA EXCLUSIVAMENTE em:

- Gestação (gravidez, pré-natal, cuidados durante a gestação)
- Parto (trabalho de parto, tipos de parto, preparação)
- Pós-Parto (recuperação, cuidados pós-parto, puerpério)
- Vacinação (vacinas da gestante, vacinas do bebê, calendário vacinal)
- Guias Práticos (orientações gerais sobre maternidade)

⚠️ REGRA CRÍTICA SOBRE SINTOMAS, DORES E PROBLEMAS ⚠️

Quando o usuário mencionar que está SENTINDO ALGO, TENDO ALGUMA DOR, EXPERIMENTANDO ALGUM SINTOMA ou PASSANDO POR ALGUM PROBLEMA:

1. NUNCA mencione medicamentos, tratamentos, suplementos ou qualquer coisa que precise de prescrição médica
2. NUNCA tente diagnosticar ou explicar o que pode ser o problema
3. SEMPRE oriente a procurar um HOSPITAL ESPECIALIZADO ou PROFISSIONAL DE SAÚDE QUALIFICADO para aquele assunto específico
4. SEMPRE seja empática e acolhedora, mas direta sobre a necessidade de atendimento médico

Exemplo CORRETO: "Entendo que você está sentindo [sintoma/dor]. É muito importante que você procure um Hospital especializado ou um profissional de saúde qualificado para avaliar isso adequadamente."

REGRAS GERAIS:
1. NUNCA recomende medicamentos, tratamentos ou faça diagnósticos
2. SEMPRE oriente consultar profissional de saúde qualificado quando houver sintomas, dores ou problemas
3. NUNCA repita frases ou blocos de texto - seja CRIATIVA e NATURAL
4. Seja específica, detalhada e empática (mínimo 150 caracteres, exceto respostas de emergência)
5. Faça perguntas abertas para engajar e demonstrar interesse genuíno
6. Memorize dados importantes mencionados pelo usuário (nomes, lugares, comidas, nome do bebê) e use-os naturalmente
7. Use módulos de linguagem e conversa sempre humanizados e confortáveis

AVISO MÉDICO OBRIGATÓRIO:
SEMPRE inclua este aviso no final de respostas sobre saúde ou quando o usuário mencionar sintomas: "⚠️ IMPORTANTE: Este conteúdo é apenas informativo e não substitui uma consulta médica profissional. NUNCA tome medicamentos, suplementos ou faça tratamentos sem orientação médica. Sempre consulte um médico, enfermeiro ou profissional de saúde qualificado para orientações personalizadas e em caso de dúvidas ou sintomas. Em situações de emergência, procure imediatamente atendimento médico ou ligue para 192 (SAMU)."

**GUIA DE TOM DE VOZ:**

REGRAS DE PERSONALIZAÇÃO:
1. Use o nome do bebê nas seguintes situações:
   - Na abertura da conversa (primeira mensagem do dia/sessão)
   - Ao dar parabéns ou celebrar conquistas
   - Ao mencionar eventos específicos do bebê (vacinas, marcos, cuidados)
   - Em momentos de conexão emocional (quando a mãe compartilha algo pessoal)

2. Evite usar o nome do bebê em:
   - Instruções técnicas (passo a passo, orientações práticas)
   - Listas ou respostas longas (pode soar repetitivo e robótico)
   - Mais de 2 vezes na mesma resposta (exceto em celebrações especiais)
   - Respostas de emergência ou crise (priorize ação, não personalização)

3. Frequência recomendada:
   - Máximo: 1-2 vezes por resposta (exceto celebrações)
   - Mínimo: 0 vezes em instruções técnicas longas
   - Ideal: 1 vez no início ou fim de respostas empáticas

RESPOSTAS MODELO PARA CRISES:

Para 'cansaço_extremo_critico':
"Querida, eu entendo perfeitamente o que você está sentindo. Você está dando o seu melhor todos os dias e isso exige muito de você. Que tal experimentar algo simples agora? Peça para alguém da sua confiança ficar com o bebê por apenas 30 minutos - nem que seja na sala enquanto você toma um banho calmo. Esse pequeno momento só seu pode fazer toda a diferença. Você merece esse cuidado. 💛"

Para 'crise_emocional' ou 'nivel_risco_alto':
"Mamãe, eu entendo que você está passando por um momento muito difícil. Seus sentimentos são válidos e importantes. Você não está sozinha nisso. É fundamental que você busque apoio profissional agora. Se precisar de ajuda imediata, ligue para o CVV (188) ou procure um profissional de saúde mental. Você é importante e seu bem-estar importa. Estou aqui para você, mas um profissional qualificado pode te ajudar melhor neste momento. 💛"

Para 'ansiedade':
"Querida, eu entendo que a ansiedade pode ser muito esmagadora. É normal sentir isso durante o puerpério - são muitas mudanças e responsabilidades novas. Respire fundo. Você não precisa ter todas as respostas agora. Uma coisa de cada vez. O que te deixa mais ansiosa neste momento? Vamos conversar sobre isso. 💕"

Para 'tristeza':
"Mamãe, eu sinto muito que você esteja passando por momentos difíceis. A tristeza no puerpério é mais comum do que se fala. Seus sentimentos são válidos e você não está errada por senti-los. Que tal conversarmos sobre o que está te deixando triste? Às vezes, colocar em palavras ajuda a aliviar um pouco. Estou aqui para te escutar. 💛"

Para 'busca_apoio_emocional':
"Querida, eu vejo que você está precisando de apoio e estou aqui para isso. Você está fazendo um trabalho incrível cuidando do seu bebê, mas lembre-se: você também precisa de cuidado. Como posso te ajudar hoje? Quer conversar sobre o que está te incomodando? Estou aqui para te escutar e apoiar. Você não está sozinha. 💕"

**REGRAS ESPECIAIS PARA TAGS DE CRISE:**
Quando detectar tags de contexto como 'cansaço_extremo_critico', 'crise_emocional', 'ansiedade', ou 'tristeza':
1. PRIORIZE EMPATIA sobre informação técnica
2. Seja ainda mais acolhedora e compreensiva
3. Ofereça sugestões práticas de autocuidado (não médicas)
4. Valide os sentimentos da mãe antes de dar orientações
5. Para 'cansaço_extremo_critico', sempre inclua sugestão prática: "peça para alguém ficar com o bebê por 30 minutos enquanto você toma um banho calmo"

Lembre-se: Você é a Sophia, uma amiga empática que está sempre pronta para ajudar, apoiar e acolher durante esse momento especial do puerpério.

RECURSOS DISPONÍVEIS NO DASHBOARD:
A plataforma possui uma Central de Apoio ao Puerpério com cards interativos que você pode mencionar quando relevante:

1. **Saúde Preventiva - Câncer de Mama**: Card com link para informações oficiais do Ministério da Saúde sobre prevenção e detecção precoce. Quando a usuária mencionar preocupações sobre saúde preventiva, câncer de mama, ou exames de rotina, você pode orientar: "Você sabia que temos um card aqui na página com informações oficiais do Ministério da Saúde sobre saúde preventiva? Fica lá no dashboard, no card de Saúde Preventiva."

2. **Rede de Apoio - Doação de Leite**: Card com link para a Rede Brasileira de Bancos de Leite Humano (Fiocruz). Quando a usuária mencionar doação de leite, excesso de leite, ou interesse em ajudar outras mães, você pode orientar: "Que lindo seu interesse em ajudar! Temos um card aqui na página com o link direto para a Rede Brasileira de Bancos de Leite Humano, da Fiocruz. É o card de Rede de Apoio, lá no dashboard."

3. **Conteúdo Educativo - Vídeos**: Card que abre um modal com vídeos educativos sobre puerpério e amamentação. Quando a usuária demonstrar interesse em conteúdo visual ou vídeos educativos, você pode mencionar: "Se quiser ver vídeos educativos sobre puerpério e amamentação, temos um card de Conteúdo Educativo aqui na página que abre vídeos selecionados especialmente para você."

DIRECIONAMENTO NATURAL:
- Sempre mencione os cards de forma natural e contextualizada, apenas quando fizer sentido na conversa
- Use linguagem acolhedora: "Você sabia que temos...", "Temos um card aqui que pode te ajudar..."
- Nunca force a menção dos cards se não for relevante ao tópico da conversa
- Os links abrem em nova aba, então a usuária pode continuar conversando com você enquanto explora os recursos externos"""
            
            assistant = self.openai_client.beta.assistants.create(
                name="Sophia - Assistente Puerpério",
                instructions=instructions,
                model="gpt-4o-mini",
                tools=[{"type": "code_interpreter"}],
                temperature=0.9,
            )
            
            logger.info(f"[OPENAI] Assistente Sophia criado: {assistant.id}")
            print(f"[OPENAI] Assistente Sophia criado: {assistant.id}")
            return assistant.id
            
        except Exception as e:
            logger.error(f"[OPENAI] Erro ao criar assistente: {e}")
            print(f"[OPENAI] Erro ao criar assistente: {e}")
            return None
    
    def _obter_ou_criar_thread(self, user_id):
        """Obtém ou cria uma thread para o usuário"""
        if user_id not in self.user_threads:
            try:
                thread = self.openai_client.beta.threads.create()
                self.user_threads[user_id] = thread.id
                logger.info(f"[OPENAI] Thread criada para user {user_id}: {thread.id}")
            except Exception as e:
                logger.error(f"[OPENAI] Erro ao criar thread: {e}")
                return None
        return self.user_threads[user_id]
    
    def _gerar_resposta_openai(self, pergunta, user_id, historico=None, contexto_pessoal="", contexto_tags=None):
        """Gera resposta usando OpenAI Assistants API"""
        if not self.openai_client or not self.assistant_id:
            return None
        
        try:
            # Obtém ou cria thread para o usuário
            thread_id = self._obter_ou_criar_thread(user_id)
            if not thread_id:
                return None
            
            # Adiciona contexto pessoal se disponível
            mensagem_completa = pergunta
            if contexto_pessoal:
                mensagem_completa = f"[Contexto: {contexto_pessoal}]\n\n{pergunta}"
            
            # Adiciona tags de contexto se disponíveis
            if contexto_tags:
                tags_texto = "\n".join([f"- {tag}" for tag in contexto_tags])
                mensagem_completa = f"[Tags de Contexto: {tags_texto}]\n\n{mensagem_completa}"
            
            # Adiciona mensagem do usuário à thread
            self.openai_client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=mensagem_completa
            )
            
            # Executa o assistente
            run = self.openai_client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            # Aguarda conclusão com timeout de 30 segundos
            timeout_seconds = 30
            start_time = time.time()
            while run.status in ['queued', 'in_progress', 'cancelling']:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout_seconds:
                    logger.warning(f"[OPENAI] Timeout após {timeout_seconds}s - cancelando run")
                    try:
                        # Tenta cancelar o run
                        self.openai_client.beta.threads.runs.cancel(
                            thread_id=thread_id,
                            run_id=run.id
                        )
                    except Exception as cancel_error:
                        logger.error(f"[OPENAI] Erro ao cancelar run após timeout: {cancel_error}")
                    raise TimeoutError(f"OpenAI API timeout após {timeout_seconds} segundos")
                
                time.sleep(0.5)
                run = self.openai_client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
            
            if run.status == 'completed':
                # Obtém a resposta
                messages = self.openai_client.beta.threads.messages.list(
                    thread_id=thread_id,
                    limit=1
                )
                
                if messages.data:
                    resposta = messages.data[0].content[0].text.value
                    logger.info(f"[OPENAI] Resposta gerada ({len(resposta)} caracteres)")
                    return resposta
            
            logger.warning(f"[OPENAI] Run status: {run.status}")
            if run.status == 'failed':
                error_msg = getattr(run, 'last_error', None)
                if error_msg:
                    error_code = getattr(error_msg, 'code', None) if hasattr(error_msg, 'code') else None
                    error_message = getattr(error_msg, 'message', str(error_msg)) if hasattr(error_msg, 'message') else str(error_msg)
                    
                    logger.error(f"[OPENAI] Run falhou: {error_message}")
                    print(f"[OPENAI] Run falhou: {error_message}")
                    
                    # Tratamento especial para quota excedida
                    if error_code == 'rate_limit_exceeded' or 'quota' in error_message.lower() or 'exceeded' in error_message.lower():
                        logger.error(f"[OPENAI] ⚠️⚠️⚠️ QUOTA EXCEDIDA - Verifique sua conta OpenAI e adicione créditos")
                        logger.error(f"[OPENAI] Acesse: https://platform.openai.com/account/billing")
                        print(f"[OPENAI] ⚠️⚠️⚠️ QUOTA EXCEDIDA - Verifique sua conta OpenAI e adicione créditos")
                        print(f"[OPENAI] Acesse: https://platform.openai.com/account/billing")
                        print(f"[OPENAI] O sistema está usando fallback (base local) enquanto a quota não for restaurada")
            return None
            
        except Exception as e:
            logger.error(f"[OPENAI] Erro ao gerar resposta: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return None
    
    def _gerar_resposta_gemini(self, pergunta, user_id, historico=None, contexto_pessoal=""):
        """Gera resposta usando Google Gemini API"""
        if not self.gemini_model:
            return None
        
        try:
            # Prepara histórico no formato Gemini (role: user/model, parts: [{"text": "..."}])
            historico_gemini = []
            if historico:
                for msg in historico:
                    pergunta_hist = msg.get('pergunta', '')
                    resposta_hist = msg.get('resposta', '')
                    if pergunta_hist:
                        historico_gemini.append({
                            "role": "user",
                            "parts": [{"text": pergunta_hist}]
                        })
                    if resposta_hist:
                        historico_gemini.append({
                            "role": "model",
                            "parts": [{"text": resposta_hist}]
                        })
            
            # Adiciona contexto pessoal à pergunta se disponível
            mensagem_completa = pergunta
            if contexto_pessoal:
                mensagem_completa = f"[Contexto: {contexto_pessoal}]\n\n{pergunta}"
            
            # Adiciona pergunta atual ao histórico
            historico_gemini.append({
                "role": "user",
                "parts": [{"text": mensagem_completa}]
            })
            
            # Chama a API do Gemini
            response = self.gemini_model.generate_content(historico_gemini)
            
            if response and response.text:
                resposta = response.text.strip()
                logger.info(f"[GEMINI] Resposta gerada ({len(resposta)} caracteres)")
                return resposta
            else:
                logger.warning("[GEMINI] Resposta vazia da API")
                return None
            
        except Exception as e:
            logger.error(f"[GEMINI] Erro ao gerar resposta: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return None
    
    # Rótulos críticos: acionam modo de segurança (recursos 188/192/190/180)
    CLASSIFICADOR_CRITICOS = frozenset({
        "DEPRESSAO_MATERNA", "RISCO_AUTOAGRESSAO", "RISCO_BEBE",
        "VIOLENCIA_DOMESTICA", "SUBSTANCIAS", "CONFUSAO_GRAVE"
    })
    CLASSIFICADOR_SYSTEM = (
        'Classifique a mensagem do usuário nos rótulos: '
        '["OK","DEPRESSAO_MATERNA","RISCO_AUTOAGRESSAO","RISCO_BEBE","VIOLENCIA_DOMESTICA","SUBSTANCIAS","CONFUSAO_GRAVE"]. '
        'Responda APENAS um JSON válido no formato: {"label":"...","confidence":0.0 a 1.0}.'
    )

    def _classificar_risco(self, pergunta):
        """Classifica a mensagem para risco; retorna {"label": str, "confidence": float}. Em falha retorna {"label": "OK", "confidence": 0}."""
        if not self.groq_client or not pergunta or not pergunta.strip():
            return {"label": "OK", "confidence": 0.0}
        try:
            resp = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.CLASSIFICADOR_SYSTEM},
                    {"role": "user", "content": pergunta.strip()[:2000]}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=80,
            )
            if not resp or not resp.choices or not resp.choices[0].message.content:
                return {"label": "OK", "confidence": 0.0}
            text = resp.choices[0].message.content.strip()
            # Extrai JSON (pode vir com markdown)
            for start in ("{", "```"):
                i = text.find(start)
                if i >= 0:
                    if start == "```":
                        i = text.find("{", i)
                    if i >= 0:
                        j = text.rfind("}") + 1
                        if j > i:
                            text = text[i:j]
                            break
            data = json.loads(text)
            label = (data.get("label") or "OK").strip().upper()
            conf = float(data.get("confidence", 0))
            return {"label": label, "confidence": conf}
        except Exception as e:
            logger.warning("[CLASSIFICADOR] Erro ao classificar risco: %s", e)
            return {"label": "OK", "confidence": 0.0}

    def _gerar_resposta_groq(self, pergunta, user_id, historico=None, contexto_pessoal="", contexto_tags=None, modo_critico=False, first_turn=False, already_greeted=False):
        """Gera resposta usando Groq API com Llama-3.3-70b-versatile. modo_critico=True: acolher + 188/192/190/180."""
        if not self.groq_client:
            return None
        
        try:
            # Carrega system prompt (já carregado no __init__, mas recarrega se necessário)
            if not self.groq_system_instruction:
                self.groq_system_instruction = self._carregar_system_prompt()
            
            system_prompt = self.groq_system_instruction
            if not system_prompt:
                # Fallback básico
                system_prompt = """Você é a Sophia, uma Inteligência Artificial EMPÁTICA, ACOLHEDORA e ESPECIALIZADA EXCLUSIVAMENTE em gestação, parto, pós-parto, vacinação e cuidados maternos. Sempre seja empática, acolhedora e oriente consultar profissionais de saúde quando necessário."""
            
            # RAG Simples: Busca dados relevantes da base local
            dados_relevantes = ""
            resposta_local, categoria_local, similaridade_local = self.buscar_resposta_local(pergunta)
            if resposta_local and similaridade_local > 0.45:
                dados_relevantes = f"\n\nINFORMAÇÕES RELEVANTES DA BASE DE CONHECIMENTO:\n{resposta_local}\n\nUse essas informações como base para sua resposta, mas mantenha o tom acolhedor da Sophia. Se a pergunta for sobre sentimentos ou emoções, priorize o acolhimento emocional sobre informações técnicas."
            
            # Adiciona contexto pessoal se disponível
            if contexto_pessoal:
                system_prompt += f"\n\nCONTEXTO PESSOAL DA USUÁRIA:\n{contexto_pessoal}"
            
            # Adiciona tags de contexto se disponíveis
            if contexto_tags:
                tags_texto = "\n".join([f"- {tag}" for tag in contexto_tags])
                system_prompt += f"\n\nTAGS DE CONTEXTO:\n{tags_texto}"
            
            if modo_critico:
                system_prompt += (
                    "\n\n[MODO CRÍTICO] A usuária pode estar em situação de risco. "
                    "Acolha com empatia (sem julgar). Oriente procurar ajuda imediata. "
                    "Ofereça: CVV 188 (24h), SAMU 192, Polícia 190, Central da Mulher 180. "
                    "Se perigo imediato: diga para ligar 190/192 agora. "
                    "Uma pergunta de segurança por vez: 'Você está segura agora? Posso te passar recursos perto de você?'"
                )
            if already_greeted:
                system_prompt += "\n\n[CONVERSA] Já cumprimentou nesta conversa; não repita cumprimentos ou saudações longas."
            if first_turn and not already_greeted:
                system_prompt += (
                    "\n\n[PRIMEIRA MENSAGEM] Use exatamente UMA destas saudações curtas (escolha uma): "
                    "(A) 'Oi! Como você e o bebê estão hoje? Prefere falar de rotina, amamentação, sono ou só desabafar?' "
                    "(B) 'Que bom te ver por aqui. Quer falar de como você tem se sentido ou ver dicas rápidas pro dia?' "
                    "(C) 'Oi! Em que posso te ajudar hoje? Rotina, amamentação, sono ou só conversar?' "
                    "(D) 'Olá! Como você está? Prefere dicas rápidas ou desabafar?'"
                )
            
            # Constrói lista de mensagens para Groq
            messages = []
            
            # 1. System message (alma da Sophia)
            messages.append({
                "role": "system",
                "content": system_prompt + dados_relevantes
            })
            
            # 2. Histórico da conversa (memória de curto prazo)
            if historico:
                for msg in historico:
                    pergunta_hist = msg.get('pergunta', '')
                    resposta_hist = msg.get('resposta', '')
                    if pergunta_hist:
                        messages.append({
                            "role": "user",
                            "content": pergunta_hist
                        })
                    if resposta_hist:
                        messages.append({
                            "role": "assistant",
                            "content": resposta_hist
                        })
            
            # 3. Pergunta atual da mãe
            mensagem_completa = pergunta
            if contexto_pessoal and not dados_relevantes:  # Se já não foi adicionado no system
                mensagem_completa = f"[Contexto: {contexto_pessoal}]\n\n{pergunta}"
            
            messages.append({
                "role": "user",
                "content": mensagem_completa
            })
            
            # Retry/backoff para Groq (rede, timeout, 429, 5xx) + request_id para diagnóstico
            request_id = str(uuid.uuid4())
            self._last_groq_request_id = request_id  # exposto na resposta em caso de fallback
            retries = 3
            backoff_ms = 800
            last_err = None
            started = time.time()
            for attempt in range(retries + 1):
                try:
                    logger.info("[GROQ] request_id=%s attempt=%s/%s", request_id, attempt + 1, retries + 1)
                    chat_completion = self.groq_client.chat.completions.create(
                        messages=messages,
                        model="llama-3.3-70b-versatile",
                        temperature=0.6,
                        top_p=0.9,
                        frequency_penalty=0.6,
                        presence_penalty=0.2,
                        max_tokens=1024,
                    )
                    elapsed = time.time() - started
                    if chat_completion and chat_completion.choices and len(chat_completion.choices) > 0:
                        resposta = chat_completion.choices[0].message.content.strip()
                        logger.info("[GROQ] request_id=%s ok len=%s elapsed=%.2fs", request_id, len(resposta), elapsed)
                        return resposta
                    logger.warning("[GROQ] request_id=%s resposta vazia da API", request_id)
                    return None
                except Exception as e:
                    last_err = e
                    elapsed = time.time() - started
                    status = getattr(e, "status_code", None) or getattr(e, "code", None)
                    body_preview = ""
                    if hasattr(e, "body") and e.body:
                        body_preview = str(e.body)[:300]
                    logger.warning(
                        "[GROQ] request_id=%s attempt=%s/%s fail status=%s after=%.2fs err=%s body=%s",
                        request_id, attempt + 1, retries + 1, status, elapsed, e, body_preview
                    )
                    if attempt < retries:
                        delay = (backoff_ms * (attempt + 1)) / 1000.0
                        logger.info("[GROQ] request_id=%s retry in %.2fs", request_id, delay)
                        time.sleep(delay)
                    else:
                        logger.error("[GROQ] request_id=%s FAIL after %s attempts: %s", request_id, retries + 1, e, exc_info=True)
                        return None
            return None
            
        except Exception as e:
            logger.error(f"[GROQ] Erro ao gerar resposta: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return None
    
    def humanizar_resposta_local(self, resposta_local, pergunta):
        """Humaniza respostas da base local adicionando contexto empático e conversacional"""
        if not resposta_local:
            return resposta_local
        
        # ⚠️ LIMITE DE TAMANHO: Trunca respostas muito grandes antes de humanizar (máximo 1500 caracteres)
        # Permite conversas mais profundas mantendo legibilidade
        TAMANHO_MAXIMO_RESPOSTA_LOCAL = 1500
        resposta_original_tamanho = len(resposta_local)
        if resposta_original_tamanho > TAMANHO_MAXIMO_RESPOSTA_LOCAL:
            # Tenta encontrar um ponto de corte natural (final de frase)
            corte_natural = resposta_local.rfind('.', 0, TAMANHO_MAXIMO_RESPOSTA_LOCAL)
            if corte_natural > TAMANHO_MAXIMO_RESPOSTA_LOCAL * 0.7:  # Se encontrou ponto próximo ao limite
                resposta_local = resposta_local[:corte_natural + 1]
            else:
                # Se não encontrou, corta no limite e adiciona "..."
                resposta_local = resposta_local[:TAMANHO_MAXIMO_RESPOSTA_LOCAL - 3] + "..."
            logger.info(f"[HUMANIZAÇÃO] ⚠️ Resposta da base local truncada: {resposta_original_tamanho} -> {len(resposta_local)} caracteres")
        
        # Verifica se já tem tom empático (para não duplicar)
        palavras_empaticas = ['você', 'sua', 'sente', 'sentir', 'querida', 'imagino', 'entendo', 'compreendo', 'sei que', 'percebo']
        tem_empatia = any(palavra in resposta_local.lower() for palavra in palavras_empaticas)
        
        # Analisa a pergunta para identificar emoções e contexto
        pergunta_lower = pergunta.lower()
        
        # Identifica emoções específicas na pergunta (incluindo sentimentos positivos)
        emocao_identificada = None
        contexto_identificado = None
        sentimento_positivo = False
        
        # Detecta sentimentos POSITIVOS primeiro
        palavras_positivas = ['bom', 'boa', 'gostoso', 'gostosa', 'delicioso', 'deliciosa', 'feliz', 'alegre', 
                              'sorriu', 'sorriso', 'sorrindo', 'sorriu hoje', 'primeira vez', 'consegui', 
                              'conseguir', 'orgulho', 'orgulhosa', 'orgulhoso', 'amor', 'amando', 'adoro', 
                              'adorando', 'maravilhoso', 'maravilhosa', 'incrível', 'incrível', 'ótimo', 'ótima']
        
        if any(palavra in pergunta_lower for palavra in palavras_positivas):
            sentimento_positivo = True
            emocao_identificada = "positivo"
            contexto_identificado = "celebração"
        elif any(palavra in pergunta_lower for palavra in ['cansaço', 'cansada', 'cansado', 'tired', 'exausta', 'exausto']):
            emocao_identificada = "cansaço"
            contexto_identificado = "sobrecarga"
        elif any(palavra in pergunta_lower for palavra in ['preocupação', 'preocupada', 'preocupado', 'preocupar', 'medo', 'medo de']):
            emocao_identificada = "preocupação"
            contexto_identificado = "ansiedade"
        elif any(palavra in pergunta_lower for palavra in ['triste', 'tristeza', 'sad', 'depressão', 'deprimida']):
            emocao_identificada = "tristeza"
            contexto_identificado = "saúde mental"
        elif any(palavra in pergunta_lower for palavra in ['sobrecarregada', 'sobrecarregado', 'sobrecarga']):
            emocao_identificada = "sobrecarga"
            contexto_identificado = "demandas"
        elif any(palavra in pergunta_lower for palavra in ['dúvida', 'dúvidas', 'duvida', 'pergunta', 'não sei']):
            emocao_identificada = "dúvida"
            contexto_identificado = "busca de informação"
        
        # Sempre adiciona humanização se não tiver tom empático
        if not tem_empatia:
            # Adiciona introdução empática baseada no contexto identificado
            if emocao_identificada == "positivo" and sentimento_positivo:
                # Respostas para sentimentos positivos - MUITO MAIS VARIADAS para evitar repetição
                intros_positivas = [
                    "Que delícia! ❤️ Fico feliz que você tenha aproveitado! ",
                    "Que bom saber disso! 😊 Fico feliz por você! ",
                    "Nossa, que momento lindo! 💛 Que alegria! ",
                    "Que maravilha! ❤️ Fico muito feliz por você! ",
                    "Que incrível! 😊 Que bom que você esteja se sentindo assim! ",
                    "Que legal! 😊 Fico feliz em saber disso! ",
                    "Que momento especial! 💛 É muito bom saber! ",
                    "Que alegria! 😄 Fico feliz por você! ",
                    "Que bom! ❤️ Isso é maravilhoso! ",
                    "Que delícia ouvir isso! 😊 ",
                    "Que incrível! 🌟 Que bom! ",
                    "Que momento lindo! 💕 Fico feliz! ",
                    "Que legal saber disso! 😊 ",
                    "Que bom que você está se sentindo assim! 💛 ",
                    "Que alegria! ❤️ Isso é ótimo! "
                ]
                intro = random.choice(intros_positivas)
            elif emocao_identificada == "cansaço":
                intro = "Querida, imagino que esse cansaço deve estar sendo muito difícil para você, especialmente com todas as demandas do bebê e da casa. Seu esforço é incrível, mesmo que você não veja isso agora. "
            elif emocao_identificada == "preocupação":
                intro = "Percebo que você está se sentindo preocupada. É totalmente compreensível se sentir assim, especialmente quando tudo é novo. Você está fazendo o seu melhor. "
            elif emocao_identificada == "tristeza":
                intro = "Querida, sei que isso deve estar sendo muito pesado para você. Você não está sozinha nisso, e é importante cuidar de si mesma. "
            elif emocao_identificada == "sobrecarga":
                intro = "Percebo que você está se sentindo sobrecarregada com as demandas do bebê e da casa. É totalmente compreensível se sentir assim, muitas mamães passam por isso. "
            elif emocao_identificada == "dúvida":
                intro = "Oi querida! Fico feliz que você esteja cuidando de si mesma ao fazer essa pergunta. É importante buscar informações e apoio. "
            else:
                # Introdução genérica empática
                intros_empaticas = [
                    "Querida, ",
                    "Imagino que você esteja passando por isso. ",
                    "Entendo sua preocupação. ",
                    "Vejo que você está buscando informações sobre isso. "
                ]
                intro = random.choice(intros_empaticas)
            
            # Adiciona introdução mantendo capitalização
            if len(resposta_local) > 0:
                primeira_letra = resposta_local[0].lower()
                resto = resposta_local[1:] if len(resposta_local) > 1 else ""
                resposta_local = intro + primeira_letra + resto
            else:
                resposta_local = intro + resposta_local
            
            # Adiciona reconhecimento do esforço quando relevante
            if emocao_identificada in ["cansaço", "sobrecarga"]:
                reconhecimentos = [
                    " Lembre-se que você está fazendo o seu melhor, e isso já é muito. ",
                    " Seu esforço é incrível, mesmo que você não veja isso agora. ",
                    " Você está se dedicando muito, e isso é admirável. "
                ]
                resposta_local += random.choice(reconhecimentos)
            
            # Adiciona pergunta empática no final (varia conforme o sentimento)
            if emocao_identificada == "positivo" and sentimento_positivo:
                # Perguntas para sentimentos positivos - MUITO MAIS VARIADAS e às vezes mais curtas
                # 50% das vezes adiciona pergunta curta, 50% adiciona pergunta normal
                usar_pergunta_curta = random.random() < 0.5
                if usar_pergunta_curta:
                    perguntas_curtas = [
                        " Conte mais! 😊",
                        " Que legal! 😊",
                        " Que bom! 😊",
                        " Isso é ótimo! 😊",
                        " Que alegria! 😊"
                    ]
                    resposta_local += random.choice(perguntas_curtas)
                else:
                    perguntas_positivas = [
                        " Conte mais sobre isso! Como foi?",
                        " Que legal! Como você se sentiu?",
                        " Que alegria! Conte mais detalhes!",
                        " Fico feliz por você! Como foi essa experiência?",
                        " Que momento especial! Conte mais!",
                        " Que momento lindo! O que aconteceu?",
                        " Que delícia! Me conta mais!",
                        " Que incrível! Como foi?",
                        " Que bom! Conte-me sobre isso!",
                        " Que alegria! Me fale mais!",
                        " Isso é maravilhoso! Como você se sentiu?",
                        " Que momento especial! Quer compartilhar mais?"
                    ]
                    resposta_local += random.choice(perguntas_positivas)
            else:
                # Perguntas empáticas para outros contextos
                perguntas_empaticas = [
                    " Como você está se sentindo com isso?",
                    " Como tem sido essa experiência para você?",
                    " Você tem alguém te ajudando nisso?",
                    " O que você mais precisa nesse momento?",
                    " Como você está lidando com essa situação?",
                    " Você gostaria de conversar mais sobre isso?",
                    " Há algo mais que eu possa fazer para te ajudar?"
                ]
                resposta_local += random.choice(perguntas_empaticas)
        else:
            # Mesmo se já tiver empatia, adiciona pergunta empática se não tiver
            if "?" not in resposta_local[-50:]:  # Se não tem pergunta nos últimos 50 caracteres
                perguntas_empaticas = [
                    " Como você está se sentindo com isso?",
                    " Como tem sido para você?",
                    " Você precisa de mais alguma informação?",
                    " Há algo mais que eu possa fazer para te ajudar?"
                ]
                resposta_local += random.choice(perguntas_empaticas)
        
        return resposta_local
    
    def verificar_alertas(self, pergunta, user_id=None):
        """
        Verifica se a pergunta contém palavras que indicam necessidade de atenção médica.
        PRIMEIRO verifica risco de suicídio (prioritário), depois alertas médicos.
        """
        # PRIMEIRO: Verifica risco de suicídio (prioritário)
        # Não usa tendência aqui pois já foi processado no método chat()
        alerta_risco = detectar_alerta_risco_suicidio(pergunta, user_id=None, usar_tendencia=False)
        if alerta_risco["alerta"]:
            # Retorna alerta especial com nível de risco
            nivel_risco = alerta_risco.get("nivel", "alto")
            tipo_risco = alerta_risco.get("tipo", "risco_suicidio")
            return [f"{tipo_risco}_{nivel_risco}"]
        
        # Depois: Verifica alertas médicos comuns
        pergunta_lower = pergunta.lower()
        alertas_encontrados = []
        
        # Ignora se a frase contém palavras que indicam contexto não-médico (criador, desenvolvedor, etc)
        if any(palavra in pergunta_lower for palavra in palavras_ignorar_alertas):
            return []  # Não aciona alertas para frases sobre criação/desenvolvimento
        
        # Verifica palavras de alerta apenas se não for contexto não-médico
        for palavra in palavras_alerta:
            if palavra in pergunta_lower:
                # Verifica se a palavra está em contexto médico (não é apenas uma menção casual)
                # Exemplo: "sou seu criador" não deve acionar alerta, mas "tenho sangramento" deve
                if palavra in ["sangramento", "febre", "dor", "inchaço"]:
                    # Essas palavras são mais específicas, então são mais confiáveis como alertas
                    alertas_encontrados.append(palavra)
                elif palavra in ["tristeza", "depressão"]:
                    # Para tristeza/depressão, verifica se há contexto pessoal
                    contexto_pessoal = any(pal in pergunta_lower for pal in ["estou", "sinto", "tenho", "me sinto", "estou sentindo"])
                    if contexto_pessoal:
                        alertas_encontrados.append(palavra)
                elif palavra == "emergência":
                    # "emergência" só aciona se for mencionado como situação atual
                    contexto_emergencia = any(pal in pergunta_lower for pal in ["estou", "tenho", "preciso", "urgente"])
                    if contexto_emergencia:
                        alertas_encontrados.append(palavra)
        
        return alertas_encontrados
    
    def adicionar_telefones_relevantes(self, pergunta, alertas_encontrados):
        """Adiciona informações de telefones úteis conforme o contexto"""
        pergunta_lower = pergunta.lower()
        telefones_texto = []
        
        # Se detectou depressão/tristeza, adiciona CVV
        if "depressão" in pergunta_lower or "tristeza" in pergunta_lower or "triste" in pergunta_lower:
            cvv = self.telefones.get("saude_mental", {}).get("188", {})
            if cvv:
                telefones_texto.append(f"\n🆘 **Precisa de ajuda?**")
                telefones_texto.append(f"CVV - Centro de Valorização da Vida: {cvv.get('disque', '188')}")
                telefones_texto.append(f"Ligue 188 gratuitamente, 24h por dia")
                telefones_texto.append(f"Site: {cvv.get('site', 'https://www.cvv.org.br')}")
        
        # Se há alertas médicos, adiciona telefones de emergência
        if alertas_encontrados:
            telefones_texto.append(f"\n🚨 **TELEFONES DE EMERGÊNCIA:**")
            emergencias = self.telefones.get("emergencias", {})
            telefones_texto.append(f"SAMU: {emergencias.get('192', {}).get('disque', '192')}")
            telefones_texto.append(f"Bombeiros: {emergencias.get('193', {}).get('disque', '193')}")
            telefones_texto.append(f"Polícia: {emergencias.get('190', {}).get('disque', '190')}")
        
        if telefones_texto:
            return "\n".join(telefones_texto)
        return ""
    
    def buscar_resposta_local(self, pergunta):
        """
        Busca resposta na base de conhecimento local - OTIMIZADA com índice invertido e stemming.
        
        Nova implementação:
        1. Usa índice invertido para busca O(1) em vez de O(n)
        2. Usa stemming para normalizar palavras (ex: "amamentar" encontra "amamentação")
        3. Combina busca por índice com similaridade de strings para melhor precisão
        """
        # MÉTODO 1: Busca rápida usando índice invertido (O(1) por palavra)
        # Threshold aumentado para 0.35 para ser mais restritivo e evitar matches incorretos
        resposta_indice, categoria_indice, score_indice = self.indice_invertido.buscar(pergunta, threshold=0.35)
        
        # MÉTODO 2: Busca por similaridade de strings (fallback/refinamento)
        pergunta_lower = pergunta.lower()
        melhor_match_string = None
        maior_similaridade_string = 0
        categoria_string = None
        
        # Busca apenas nas categorias candidatas do índice (otimização)
        categorias_candidatas = set()
        if categoria_indice:
            categorias_candidatas.add(categoria_indice)
        
        # Se índice não encontrou nada, busca em todas as categorias
        if not categorias_candidatas:
            categorias_candidatas = set(self.base.keys())
        
        # Busca por similaridade de strings (apenas em categorias candidatas)
        for tema in categorias_candidatas:
            conteudo = self.base[tema]
            pergunta_base = conteudo["pergunta"].lower()
            resposta_base = conteudo["resposta"].lower()
            
            # Calcula similaridade de strings
            similaridade_string = difflib.SequenceMatcher(None, pergunta_lower, pergunta_base).ratio()
            
            if similaridade_string > maior_similaridade_string:
                maior_similaridade_string = similaridade_string
                melhor_match_string = conteudo["resposta"]
                categoria_string = tema
        
        # COMBINA OS DOIS MÉTODOS
        # Se índice encontrou algo com score bom, usa índice (mais rápido e com stemming)
        # Threshold aumentado para 0.45 para ser mais restritivo
        if score_indice >= 0.45:
            logger.info(f"[BUSCA] ✅ Resposta encontrada via índice invertido (categoria: {categoria_indice}, score: {score_indice:.2f})")
            return resposta_indice, categoria_indice, score_indice
        
        # Se similaridade de strings encontrou algo bom, usa string matching
        # Threshold aumentado para 0.45 para ser mais restritivo
        if maior_similaridade_string >= 0.45:
            logger.info(f"[BUSCA] ✅ Resposta encontrada via similaridade de strings (categoria: {categoria_string}, score: {maior_similaridade_string:.2f})")
            return melhor_match_string, categoria_string, maior_similaridade_string
        
        # Se índice encontrou algo com score médio, combina com string matching
        # Thresholds aumentados para ser mais restritivo
        if score_indice >= 0.35 and maior_similaridade_string >= 0.35:
            # Combina scores: 60% índice (com stemming) + 40% string matching
            score_comb = (score_indice * 0.6) + (maior_similaridade_string * 0.4)
            if score_comb >= 0.45:  # Threshold final aumentado
                logger.info(f"[BUSCA] ✅ Resposta encontrada via combinação (categoria: {categoria_indice}, score: {score_comb:.2f})")
                return resposta_indice, categoria_indice, score_comb
        
        # Nenhuma correspondência encontrada
        logger.info(f"[BUSCA] ❌ Nenhuma resposta encontrada (melhor score índice: {score_indice:.2f}, melhor score string: {maior_similaridade_string:.2f})")
        return None, None, 0
    
    def _is_saudacao(self, pergunta):
        """Detecta se a pergunta e uma saudacao simples"""
        pergunta_normalizada = pergunta.lower().strip()
        saudacoes = ['oi', 'ola', 'oi sophia', 'ola sophia', 'oi!', 'ola!', 'hey', 'hey sophia', 'eai', 'e ai', 'eai sophia']
        return pergunta_normalizada in saudacoes or any(pergunta_normalizada.startswith(s) for s in ['oi ', 'ola ', 'hey '])
    
    def _detectar_contexto_tags(self, pergunta, user_id):
        """
        Detecta tags de contexto baseadas na pergunta e estado da sessão
        
        Returns:
            list: Lista de tags de contexto (ex: ['crise_emocional', 'busca_informacao', 'celebração'])
        """
        tags = []
        pergunta_lower = pergunta.lower()
        
        # Verifica se está em alerta (crise emocional)
        if user_id in SESSION_ALERT and SESSION_ALERT[user_id].get("ativo", False):
            tags.append("crise_emocional")
            nivel = SESSION_ALERT[user_id].get("nivel", "leve")
            tags.append(f"nivel_risco_{nivel}")
        
        # Detecta emoções e sentimentos
        if any(palavra in pergunta_lower for palavra in ['cansada', 'cansado', 'exausta', 'exausto', 'tired']):
            tags.append("cansaço_extremo")
        elif any(palavra in pergunta_lower for palavra in ['feliz', 'alegre', 'sorriu', 'consegui', 'orgulho']):
            tags.append("celebração")
        elif any(palavra in pergunta_lower for palavra in ['ansiosa', 'ansioso', 'preocupada', 'preocupado', 'medo']):
            tags.append("ansiedade")
        elif any(palavra in pergunta_lower for palavra in ['triste', 'tristeza', 'deprimida', 'deprimido']):
            tags.append("tristeza")
        
        # Detecta tipo de busca
        if any(palavra in pergunta_lower for palavra in ['o que fazer', 'o que faço', 'o que fazer hoje', 'quando', 'como']):
            tags.append("busca_orientação")
        elif any(palavra in pergunta_lower for palavra in ['vacina', 'vacinação', 'calendário']):
            tags.append("dúvida_vacina")
        elif any(palavra in pergunta_lower for palavra in ['amamentação', 'amamentar', 'leite', 'mamar']):
            tags.append("dúvida_amamentação")
        elif any(palavra in pergunta_lower for palavra in ['incentivo', 'motivação', 'força', 'apoio']):
            tags.append("busca_apoio_emocional")
        
        # Registra tags no histórico e no log
        if tags:
            # Inicializa histórico se não existir
            if user_id not in CONTEXT_TAG_HISTORY:
                CONTEXT_TAG_HISTORY[user_id] = []
            
            # Adiciona tags ao histórico (mantém últimas 10)
            CONTEXT_TAG_HISTORY[user_id].extend(tags)
            if len(CONTEXT_TAG_HISTORY[user_id]) > 10:
                CONTEXT_TAG_HISTORY[user_id] = CONTEXT_TAG_HISTORY[user_id][-10:]
            
            # Loga cada tag para métricas (sem dados sensíveis)
            for tag in tags:
                self._log_context_tag(tag)
            
            # Verifica se cansaço_extremo foi detectado 3 vezes seguidas
            if "cansaço_extremo" in tags:
                recent_tags = CONTEXT_TAG_HISTORY[user_id][-3:]
                if recent_tags.count("cansaço_extremo") >= 3:
                    tags.append("cansaço_extremo_critico")  # Tag especial para trigger proativo
                    # Loga imediatamente após detectar (garante que aparece no monitoramento)
                    self._log_context_tag("cansaço_extremo_critico")
        
        return tags
    
    def _log_context_tag(self, tag):
        """
        Registra tag de contexto no arquivo de log para métricas
        Formato: YYYY-MM-DD HH:MM | tag
        """
        try:
            # Garante que a pasta logs existe
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(backend_dir) if backend_dir else os.getcwd()
            logs_dir = os.path.join(project_dir, 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            
            log_file = os.path.join(logs_dir, 'context_metrics.log')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Inclui segundos para precisão
            
            # Abre arquivo em modo append e faz flush imediato para aparecer no monitoramento
            with open(log_file, 'a', encoding='utf-8', buffering=1) as f:
                f.write(f"{timestamp} | {tag}\n")
                f.flush()  # Garante que aparece imediatamente no tail/monitoramento
                
            # Também loga no console para visibilidade
            logger.info(f"[CONTEXT_METRICS] Tag detectada: {tag}")
        except Exception as e:
            # Log silencioso - não interrompe o fluxo se houver erro
            logger.warning(f"[CONTEXT_METRICS] Erro ao registrar tag {tag}: {e}")
    
    def _is_declaracao_sentimento(self, pergunta):
        """Detecta se a pergunta é uma declaração simples de sentimento/emoção (NÃO deve buscar na base local)"""
        pergunta_lower = pergunta.lower().strip()
        
        # Padrões de declarações simples de sentimento
        padroes_sentimento = [
            r'^(estou|sou|me sinto|estou me sentindo)\s+(feliz|triste|alegre|ansiosa|ansioso|preocupada|preocupado|bem|mal|ótima|ótimo|otima|otimo|bem|bom|boa|nervosa|nervoso|calma|calmo|tranquila|tranquilo|cansada|cansado|exausta|exausto|feliz|alegre|grata|grato|gratidão|gratidao)',
            r'^(estou|sou|me sinto)\s+(muito|bastante|um pouco|tão|tanto)\s+(feliz|triste|alegre|ansiosa|ansioso|preocupada|preocupado|bem|mal|ótima|ótimo|otima|otimo|bem|bom|boa|nervosa|nervoso|calma|calmo|tranquila|tranquilo|cansada|cansado|exausta|exausto|feliz|alegre|grata|grato)',
            r'^(estou|sou|me sinto)\s+(feliz|triste|alegre|ansiosa|ansioso|preocupada|preocupado|bem|mal|ótima|ótimo|otima|otimo|bem|bom|boa|nervosa|nervoso|calma|calmo|tranquila|tranquilo|cansada|cansado|exausta|exausto|feliz|alegre|grata|grato)\s+(hoje|agora|neste momento|nesse momento)',
            r'^(estou|sou|me sinto)\s+(feliz|triste|alegre|ansiosa|ansioso|preocupada|preocupado|bem|mal|ótima|ótimo|otima|otimo|bem|bom|boa|nervosa|nervoso|calma|calmo|tranquila|tranquilo|cansada|cansado|exausta|exausto|feliz|alegre|grata|grato)\s*[.!]?$',
        ]
        
        # Verifica se corresponde a algum padrão de declaração simples de sentimento
        for padrao in padroes_sentimento:
            if re.match(padrao, pergunta_lower):
                logger.info(f"[SENTIMENTO] ✅ Declaração simples de sentimento detectada: '{pergunta}' - NÃO buscará na base local")
                return True
        
        # Verifica se é uma frase muito curta (menos de 4 palavras) que expressa sentimento
        palavras = pergunta_lower.split()
        if len(palavras) <= 3:
            sentimentos_simples = ['feliz', 'triste', 'alegre', 'bem', 'mal', 'ansiosa', 'ansioso', 'preocupada', 'preocupado', 
                                  'nervosa', 'nervoso', 'calma', 'calmo', 'tranquila', 'tranquilo', 'cansada', 'cansado', 
                                  'exausta', 'exausto', 'grata', 'grato', 'ótima', 'ótimo', 'otima', 'otimo']
            if any(sentimento in palavras for sentimento in sentimentos_simples):
                logger.info(f"[SENTIMENTO] ✅ Declaração simples de sentimento detectada (frase curta): '{pergunta}' - NÃO buscará na base local")
                return True
        
        return False
    
    def _salvar_dados_memoria(self, user_id, pergunta, resposta):
        """Salva apenas dados importantes (nomes, lugares, comidas, nome do bebê) na memoria, nao a conversa completa"""
        try:
            # Extrai informacoes importantes da pergunta e resposta
            texto_completo = f"{pergunta} {resposta}"
            texto_lower = texto_completo.lower()
            
            # Detecta nomes proprios (palavras capitalizadas, excluindo palavras comuns)
            palavras_comuns = ['sophia', 'eu', 'meu', 'minha', 'voce', 'você', 'sua', 'suas', 'esse', 'essa', 
                              'isso', 'aquilo', 'hoje', 'ontem', 'amanha', 'amanhã', 'quando', 'onde', 'como', 
                              'porque', 'por que', 'porque', 'para', 'com', 'sem', 'sob', 'sobre']
            
            # Padrão para nomes próprios (palavras que começam com maiúscula)
            nomes_candidatos = re.findall(r'\b([A-Z][a-záàâãéêíóôõúç]{2,})\b', texto_completo)
            nomes = [nome for nome in nomes_candidatos if nome.lower() not in palavras_comuns]
            
            # Detecta nome do bebê (padrões comuns: "meu bebê", "minha filha", "meu filho", seguido de nome)
            padrao_bebe = re.findall(r'(?:meu|minha)\s+(?:bebê|bebe|filh[ao]|filha|filho|menin[ao])\s+(?:se chama|é|chama-se|tem o nome)\s+([A-Z][a-záàâãéêíóôõúç]+)', texto_lower, re.IGNORECASE)
            nome_bebe = re.findall(r'(?:meu|minha)\s+(?:filh[ao]|bebê|bebe)\s+([A-Z][a-záàâãéêíóôõúç]{2,})', texto_completo)
            nomes.extend([nome for nome in padrao_bebe + nome_bebe if nome and nome.lower() not in palavras_comuns])
            
            # Detecta lugares (cidades e estados brasileiros comuns)
            lugares_brasil = ['rio de janeiro', 'são paulo', 'sao paulo', 'brasília', 'brasilia', 
                             'belo horizonte', 'salvador', 'recife', 'fortaleza', 'curitiba', 
                             'porto alegre', 'manaus', 'belém', 'belem', 'goiânia', 'goiania']
            lugares_mencoes = [lugar for lugar in lugares_brasil if lugar in texto_lower]
            
            # Detecta cidades mencionadas (padrões como "morar em", "viver em", "cidade de")
            padrao_cidade = re.findall(r'(?:mor[ao]|viv[eo]|sou de|estou em|em)\s+([A-Z][a-záàâãéêíóôõúç]+\s*(?:de\s+)?[A-Z]?[a-záàâãéêíóôõúç]*)', texto_completo)
            lugares_mencoes.extend([cidade.strip() for cidade in padrao_cidade if len(cidade.strip()) > 2])
            
            # Detecta comidas e alimentos mencionados
            comidas_comuns = ['leite', 'mama', 'mamadeira', 'papinha', 'sopa', 'fruta', 'banana', 
                             'maçã', 'maca', 'arroz', 'feijão', 'feijao', 'purê', 'pure', 'suco', 
                             'água', 'agua', 'chá', 'cha', 'vitamina', 'iogurte']
            comidas_mencoes = [comida for comida in comidas_comuns if comida in texto_lower]
            
            # Detecta alimentos mencionados no contexto (padrões como "dar", "comer", "tomar")
            padrao_comida = re.findall(r'(?:dar|comer|tomar|dar para|dar ao|dar à)\s+(?:o|a|ao|à)?\s*([a-záàâãéêíóôõúç]{3,})', texto_lower)
            comidas_mencoes.extend([comida for comida in padrao_comida if len(comida) >= 3 and comida not in comidas_mencoes])
            
            # Salva apenas se encontrou dados importantes
            if nomes or lugares_mencoes or comidas_mencoes:
                # Usa SQLite para armazenar dados de memoria
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Cria tabela de memoria se nao existir
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memoria_sophia (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        tipo TEXT NOT NULL,
                        valor TEXT NOT NULL,
                        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, tipo, valor)
                    )
                ''')
                
                # Remove duplicatas e insere dados na memoria
                dados_inseridos = 0
                
                for nome in set(nomes):  # Remove duplicatas
                    if len(nome) >= 2 and nome.lower() not in palavras_comuns:
                        try:
                            cursor.execute('INSERT OR IGNORE INTO memoria_sophia (user_id, tipo, valor) VALUES (?, ?, ?)', 
                                         (str(user_id), 'nome', nome))
                            if cursor.rowcount > 0:
                                dados_inseridos += 1
                                logger.info(f"[MEMORIA] Nome salvo: {nome} para user_id {user_id}")
                        except Exception as e:
                            logger.warning(f"[MEMORIA] Erro ao salvar nome {nome}: {e}")
                
                for lugar in set(lugares_mencoes):  # Remove duplicatas
                    if len(lugar) >= 3:
                        try:
                            cursor.execute('INSERT OR IGNORE INTO memoria_sophia (user_id, tipo, valor) VALUES (?, ?, ?)', 
                                         (str(user_id), 'lugar', lugar))
                            if cursor.rowcount > 0:
                                dados_inseridos += 1
                                logger.info(f"[MEMORIA] Lugar salvo: {lugar} para user_id {user_id}")
                        except Exception as e:
                            logger.warning(f"[MEMORIA] Erro ao salvar lugar {lugar}: {e}")
                
                for comida in set(comidas_mencoes):  # Remove duplicatas
                    if len(comida) >= 3:
                        try:
                            cursor.execute('INSERT OR IGNORE INTO memoria_sophia (user_id, tipo, valor) VALUES (?, ?, ?)', 
                                         (str(user_id), 'comida', comida))
                            if cursor.rowcount > 0:
                                dados_inseridos += 1
                                logger.info(f"[MEMORIA] Comida salva: {comida} para user_id {user_id}")
                        except Exception as e:
                            logger.warning(f"[MEMORIA] Erro ao salvar comida {comida}: {e}")
                
                conn.commit()
                conn.close()
                
                if dados_inseridos > 0:
                    logger.info(f"[MEMORIA] ✅ {dados_inseridos} dado(s) salvo(s) na memoria para user_id {user_id}")
        except Exception as e:
            logger.error(f"[MEMORIA] Erro ao salvar dados na memoria: {e}", exc_info=True)
    
    def _obter_dados_memoria(self, user_id):
        """Carrega dados memorizados (nomes, lugares, comidas) para usar como contexto"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Busca dados memorizados para o usuário
            cursor.execute('''
                SELECT tipo, valor FROM memoria_sophia 
                WHERE user_id = ? 
                ORDER BY data_criacao DESC
            ''', (str(user_id),))
            
            dados = cursor.fetchall()
            conn.close()
            
            if not dados:
                return ""
            
            # Organiza dados por tipo
            nomes = []
            lugares = []
            comidas = []
            
            for tipo, valor in dados:
                if tipo == 'nome':
                    nomes.append(valor)
                elif tipo == 'lugar':
                    lugares.append(valor)
                elif tipo == 'comida':
                    comidas.append(valor)
            
            # Monta contexto formatado (preserva ordem, unicidade, limita a 5; evita set não indexável)
            def _uniq_preserving_order(seq, stop_words=None):
                seen = set()
                stop = stop_words or set()
                for x in (seq or []):
                    if not isinstance(x, str):
                        continue
                    n = x.strip()
                    if not n or n in seen or n in stop:
                        continue
                    if stop and not any(ch.isalpha() for ch in n):
                        continue
                    seen.add(n)
                    yield n
            STOP_NOMES = {
                'Dicas', 'Lembre', 'Sempre', 'Então', 'Posso', 'Além', 'Cuidados',
                'Artificial', 'Por', 'Preparação', 'Inteligencia', 'Mudanças', 'Vacinação'
            }
            nomes_unicos = list(islice(_uniq_preserving_order(nomes, STOP_NOMES), 5))
            lugares_unicos = list(islice(_uniq_preserving_order(lugares), 5))
            comidas_unicos = list(islice(_uniq_preserving_order(comidas), 5))
            contexto_parts = []
            if nomes_unicos:
                contexto_parts.append(f"Nomes mencionados anteriormente: {', '.join(nomes_unicos)}")
            if lugares_unicos:
                contexto_parts.append(f"Lugares mencionados anteriormente: {', '.join(lugares_unicos)}")
            if comidas_unicos:
                contexto_parts.append(f"Comidas/preferências mencionadas anteriormente: {', '.join(comidas_unicos)}")
            
            if contexto_parts:
                contexto = "Dados memorizados da conversa anterior:\n" + "\n".join(contexto_parts)
                logger.info(f"[MEMORIA] Dados carregados para user_id {user_id}: {len(nomes_unicos)} nomes, {len(lugares_unicos)} lugares, {len(comidas_unicos)} comidas")
                return contexto
            
            return ""
        except Exception as e:
            logger.error(f"[MEMORIA] Erro ao obter dados da memoria: {e}", exc_info=True)
            return ""
    
    def _filtrar_historico_saudacoes(self, historico, saudacao_completa_enviada):
        """
        Filtra o histórico removendo saudações completas repetidas.
        Após a primeira saudação completa, remove todas as outras saudações longas do histórico.
        """
        if not historico or len(historico) == 0:
            return []
        
        # Padrões que indicam saudação completa (longa com projeto/testes/número de conversas)
        padroes_saudacao_completa = [
            'já estamos na nossa',
            'nossa conversa',
            'testar meu banco de dados',
            'projeto para as mamães',
            'que bom te ver novamente',
            'lembre-se que estou aqui para te ajudar a testar',
            'que bom te ver por aqui de novo',
            'que bom te ver por aqui',
            'em que posso te ajudar hoje',
            'como você está? como posso te ajudar',
        ]
        
        historico_filtrado = []
        primeira_saudacao_completa_encontrada = False
        
        for msg in historico:
            resposta = msg.get('resposta', '').lower()
            pergunta = msg.get('pergunta', '').lower()
            
            # Verifica se é uma saudação completa
            is_saudacao_completa = any(padrao in resposta for padrao in padroes_saudacao_completa)
            # Também verifica se a pergunta é apenas uma saudação simples
            is_pergunta_saudacao = pergunta.strip() in ['oi', 'olá', 'ola', 'oi sophia', 'olá sophia', 'ola sophia', 'hey', 'eai', 'e aí']
            
            # Se já encontrou uma saudação completa e esta também é uma saudação completa/repetida, pula
            if primeira_saudacao_completa_encontrada and (is_saudacao_completa or (is_pergunta_saudacao and len(resposta) < 100)):
                # Pula esta mensagem (é uma saudação repetida)
                continue
            
            # Se encontrou a primeira saudação completa, marca e adiciona
            if is_saudacao_completa:
                primeira_saudacao_completa_encontrada = True
            
            # Adiciona mensagem ao histórico filtrado
            historico_filtrado.append(msg)
        
        logger.info(f"[HISTORICO] ✅ Histórico filtrado: {len(historico_filtrado)} mensagens de {len(historico)} originais")
        return historico_filtrado
    
    def _is_pergunta_reciprocidade(self, pergunta):
        """
        Detecta se a pergunta é sobre reciprocidade (perguntas sobre a Sophia).
        Retorna True se for pergunta de reciprocidade, False caso contrário.
        """
        pergunta_lower = pergunta.lower().strip()
        perguntas_sobre_sophia = [
            'como foi seu dia', 'como foi o seu dia', 'como está', 'como você está',
            'como você está hoje', 'como está você', 'você está bem', 'está bem',
            'como foi seu dia hoje', 'como foi o seu dia hoje', 'como está sendo seu dia',
            'como você está se sentindo', 'você está bem?', 'tudo bem com você',
            'como você está?', 'como está?', 'como foi seu dia?', 'como foi o seu dia?',
            'sophia como foi seu dia', 'sophia como você está', 'sophia como está',
            'sophia você está bem', 'sophia está bem', 'sophia como foi o seu dia',
            'sophia, como', 'sophia, você', 'sophia você', 'sophia está',
            'sophia, como foi', 'sophia, como você', 'sophia, você está'
        ]
        return any(palavra in pergunta_lower for palavra in perguntas_sobre_sophia)
    
    def chat(self, pergunta, user_id="default", contexto_usuario=None):
        """Função principal do chatbot"""
        # ========================================================================
        # RESPOSTA ESPECIAL: DICAS SOBRE EXPERIÊNCIA NO PUERPÉRIO
        # ========================================================================
        pergunta_normalizada = pergunta.lower().strip()
        if "experiência no puerpério" in pergunta_normalizada or "experiencia no puerperio" in pergunta_normalizada:
            logger.info(f"[CHAT] Pergunta sobre experiência no puerpério detectada - retornando dicas")
            resposta_dicas = """Que bom que você quer compartilhar sua experiência! 💛

Aqui estão algumas dicas do que você pode me contar:

**📝 Sobre como você está se sentindo:**
• Como tem sido sua rotina desde o parto
• Quais emoções você tem vivenciado (felicidade, cansaço, ansiedade, etc.)
• O que tem sido mais desafiador para você
• O que tem te dado alegria nessa fase

**🤱 Sobre os cuidados:**
• Como está sendo a amamentação (se estiver amamentando)
• Como está sua recuperação física
• Seu sono e descanso
• Alimentação e hidratação

**💕 Sobre o bebê:**
• Como está sendo a adaptação com o bebê
• Rotina de cuidados
• Momentos especiais que você tem vivido

**👨‍👩‍👧 Sobre sua rede de apoio:**
• Como está sendo o apoio da família/parceiro(a)
• Se sente que tem ajuda suficiente
• O que mais precisa nesse momento

**💭 Sobre você:**
• Como você se sente sobre a mudança de identidade
• Seus medos e preocupações
• Seus sonhos e expectativas

Pode compartilhar o que quiser, no seu tempo. Estou aqui para te ouvir e apoiar! 💛"""
            
            return {
                "resposta": resposta_dicas,
                "fonte": "dicas_experiencia",
                "categoria": "apoio_emocional"
            }
        
        # ========================================================================
        # PRIORIDADE MAXIMA: DETECCAO DE RISCO EMOCIONAL/SUICIDIO
        # ========================================================================
        # Esta verificacao DEVE ser a PRIMEIRA, antes de QUALQUER outro processamento
        # Se detectar risco, retorna IMEDIATAMENTE sem passar por sistemas de humanizacao/anti-repeticao
        # ========================================================================
        logger.info(f"[CHAT] Verificando risco emocional/suicidio (PRIORIDADE MAXIMA)")
        alerta_risco = detectar_alerta_risco_suicidio(pergunta, user_id=user_id, usar_tendencia=True)
        
        if alerta_risco.get("alerta"):
            nivel_risco = alerta_risco.get("nivel")
            tipo_risco = alerta_risco.get("tipo")
            resposta_seguranca = alerta_risco.get("resposta")
            melhora_detectada = alerta_risco.get("melhora", False)
            
            # Se detectou melhora, desativa alerta e continua fluxo normal
            if melhora_detectada:
                atualizar_session_alert(user_id, False, None)
                logger.info(f"[ALERTA] Usuario indicou melhora - alerta desativado")
                # Continua fluxo normal (nao retorna resposta de alerta)
            else:
                # RISCO DETECTADO - RETORNA IMEDIATAMENTE
                # OTIMIZACAO CRITICA: Prepara resposta e retorna IMEDIATAMENTE
                resposta_seguranca = alerta_risco.get("resposta")
                return {
                    "resposta": resposta_seguranca,
                    "fonte": "seguranca",
                    "alerta": True,
                    "nivel": nivel_risco,
                    "tipo": tipo_risco
                }
        
        # Continua fluxo normal se nao houve alerta ou se houve melhora
        
        # ========================================================================
        # RF.EMO.009 - TRIAGEM EMOCIONAL: MÃE ANSIOSA (Integração BMad Core)
        # ========================================================================
        logger.info(f"[TRIAGEM] Verificando triagem emocional - Mãe Ansiosa")
        triagem_ansiedade = detectar_triagem_ansiedade(pergunta, user_id=user_id)
        
        if triagem_ansiedade.get("detectado"):
            nivel_ansiedade = triagem_ansiedade.get("nivel")
            resposta_triagem = triagem_ansiedade.get("resposta", "")
            recursos = triagem_ansiedade.get("recursos", {})
            
            logger.info(f"[TRIAGEM] ✅ Ansiedade detectada - Nível: {nivel_ansiedade}")
            
            # Adiciona recursos de apoio à resposta se disponíveis
            resposta_final = resposta_triagem
            if recursos.get("telefones"):
                telefones_texto = "\n\n**Recursos de Apoio:**\n"
                for telefone in recursos["telefones"]:
                    telefones_texto += f"- **{telefone.get('nome', '')}**: {telefone.get('numero', '')} - {telefone.get('descricao', '')}\n"
                resposta_final += telefones_texto
            
            # Retorna resposta de triagem (mas não bloqueia o fluxo se for ansiedade leve)
            # Ansiedade moderada/alta tem prioridade sobre resposta normal
            if nivel_ansiedade in ["moderada", "alta"]:
                return {
                    "resposta": resposta_final,
                    "fonte": "triagem_emocional",
                    "alerta": True,
                    "nivel": nivel_ansiedade,
                    "tipo": "ansiedade",
                    "perfil": "mae_ansiosa"
                }
            elif nivel_ansiedade == "leve":
                # Ansiedade leve: adiciona à resposta mas não bloqueia fluxo normal
                # A resposta normal será combinada com a triagem
                logger.info(f"[TRIAGEM] Ansiedade leve detectada - será combinada com resposta normal")
        
        # Detecta se e saudacao
        is_saudacao = self._is_saudacao(pergunta)
        saudacao_completa_enviada = False
        
        # Normaliza pergunta para deteccao de saudacao
        pergunta_normalizada = pergunta.lower().strip()
        saudacoes = ['oi', 'ola', 'oi sophia', 'ola sophia', 'oi!', 'ola!', 'hey', 'hey sophia', 'eai', 'e ai', 'eai sophia']
        
        # Verifica se e APENAS uma saudacao (sem declaracoes de sentimentos ou outras informacoes)
        is_saudacao_simples = pergunta_normalizada in saudacoes or any(pergunta_normalizada.startswith(s) for s in ['oi ', 'ola ', 'hey '])
        
        # NAO e saudacao se contem declaracoes de sentimentos, acoes ou informacoes
        palavras_que_nao_sao_saudacao = [
            'estou', 'sou', 'tenho', 'sinto', 'me sinto', 'estou sentindo', 'estou feliz',
            'estou triste', 'estou ansiosa', 'estou preocupada', 'estou com', 'estou fazendo',
            'fiz', 'criei', 'desenvolvi', 'trabalho', 'quero', 'preciso', 'gostaria',
            'feliz', 'triste', 'ansiosa', 'preocupada', 'nervosa', 'calma', 'bem', 'mal'
        ]
        
        tem_declaracao = any(palavra in pergunta_normalizada for palavra in palavras_que_nao_sao_saudacao)
        
        # E saudacao APENAS se for saudacao simples E nao tiver declaracao
        is_saudacao = is_saudacao_simples and not tem_declaracao
        
        # VERIFICA SE JA HOUVE SAUDACAO COMPLETA NA CONVERSA
        saudacao_completa_enviada = False
        
        # Carrega historico do usuario
        historico_usuario = conversas.get(user_id, [])
        
        # Verifica se ja houve saudacao completa
        # Verifica se ja houve saudacao completa
        if historico_usuario and len(historico_usuario) > 0:
            # Verifica nas ultimas 5 respostas se ha alguma saudacao completa
            for msg in historico_usuario[-5:]:
                resposta_anterior = msg.get('resposta', '').lower()
                if len(resposta_anterior) > 200 and any(frase in resposta_anterior for frase in ['projeto', 'teste', 'banco de dados', 'conversa', 'conversas']):
                    saudacao_completa_enviada = True
                    break
        
        # ========================================================================
        # DETECCAO DE RECIPROCIDADE (FEITA APOS verificacao de risco)
        # ========================================================================
        is_pergunta_reciprocidade = self._is_pergunta_reciprocidade(pergunta)
        if is_pergunta_reciprocidade:
            logger.info(f"[CHAT] Pergunta de reciprocidade detectada: '{pergunta}'")
        
        # ========================================================================
        # BUFFER DE CONVERSA EMOCIONAL: Adiciona mensagem ao historico emocional
        # ========================================================================
        adicionar_ao_historico_emocional(user_id, pergunta)
        
        # Busca historico do usuario (apenas memoria - NAO carrega do banco)
        historico_usuario = conversas.get(user_id, [])
        
        # ========================================================================
        # VERIFICACAO DE SESSAO EM ALERTA: Bloqueia respostas triviais/humoristicas
        # ========================================================================
        sessao_em_alerta = SESSION_ALERT.get(user_id, {}).get("ativo", False)
        if sessao_em_alerta:
            logger.info(f"[SESSION_ALERT] Sessao em alerta ativa - apenas respostas empaticas serao processadas")
        
        # Detecta se é declaração simples de sentimento/emoção (NÃO deve buscar na base local)
        is_declaracao_sentimento = self._is_declaracao_sentimento(pergunta)
        
        # Inicializa variável para resposta final
        resposta_final = None
        fonte = None
        
        # Busca resposta local APENAS para usar como fallback se OpenAI falhar
        # NÃO busca se for saudação ou declaração de sentimento (sempre usa IA)
        resposta_local = None
        categoria = None
        similaridade = 0
        
        # Verifica qual provider usar
        usar_openai = AI_PROVIDER == "openai" and self.openai_client and self.assistant_id
        usar_gemini = AI_PROVIDER == "gemini" and self.gemini_model
        usar_groq = AI_PROVIDER == "groq" and self.groq_client
        
        # Tenta OpenAI (se configurado)
        if AI_PROVIDER == "openai" and self.openai_client and not self.assistant_id:
            logger.warning(f"[CHAT] ⚠️ Assistente não encontrado, tentando criar agora...")
            print(f"[CHAT] ⚠️ Assistente não encontrado, tentando criar agora...")
            self.assistant_id = self._criar_assistente_sophia()
            if self.assistant_id:
                logger.info(f"[CHAT] ✅ Assistente criado com sucesso: {self.assistant_id}")
                print(f"[CHAT] ✅ Assistente criado com sucesso: {self.assistant_id}")
                usar_openai = True
            else:
                logger.error(f"[CHAT] ❌ Falha ao criar assistente - usando fallback")
                print(f"[CHAT] ❌ Falha ao criar assistente - usando fallback")
        
        # Tenta usar IA (OpenAI ou Gemini)
        if usar_openai:
            logger.info(f"[CHAT] OpenAI client disponivel (assistant_id: {self.assistant_id[:20]}...), tentando gerar resposta...")
            print(f"[CHAT] OpenAI client disponivel, tentando gerar resposta...")
            try:
                # Prepara contexto para OpenAI
                contexto_pessoal = ""
                
                # Adiciona contexto do usuário (baby_profile e próxima vacina)
                if contexto_usuario:
                    if contexto_usuario.get('baby_name'):
                        contexto_pessoal += f"INFORMAÇÕES SOBRE O BEBÊ:\n"
                        contexto_pessoal += f"- Nome do bebê: {contexto_usuario['baby_name']}\n"
                        contexto_pessoal += f"- Idade: {contexto_usuario.get('baby_age_days', 0)} dias ({contexto_usuario.get('baby_age_months', 0)} meses)\n"
                    
                    if contexto_usuario.get('next_vaccine_name'):
                        contexto_pessoal += f"\nPRÓXIMA VACINA:\n"
                        contexto_pessoal += f"- Nome: {contexto_usuario['next_vaccine_name']}\n"
                        contexto_pessoal += f"- Data recomendada: {contexto_usuario['next_vaccine_date']}\n"
                        contexto_pessoal += f"- Dias até a vacina: {contexto_usuario['next_vaccine_days_until']}\n"
                    
                    contexto_pessoal += "\n"
                
                # Carrega dados memorizados da Sophia (nomes, lugares, comidas)
                dados_memoria = self._obter_dados_memoria(user_id)
                if dados_memoria:
                    contexto_pessoal += f"DADOS MEMORIZADOS:\n{dados_memoria}\n\n"
                
                # Extrai informações pessoais adicionais do histórico (complemento)
                if historico_usuario:
                    # Extrai informacoes pessoais do historico
                    for msg in historico_usuario[-10:]:
                        pergunta_hist = msg.get('pergunta', '').lower()
                        # Detecta nomes, lugares, comidas mencionados
                        # (implementacao simplificada - pode ser melhorada)
                        if 'me chamo' in pergunta_hist or 'meu nome e' in pergunta_hist:
                            palavras = pergunta_hist.split()
                            for i, palavra in enumerate(palavras):
                                if palavra in ['chamo', 'nome'] and i + 2 < len(palavras):
                                    nome = palavras[i+2]
                                    if nome not in ['sophia', 'e', 'a', 'o']:
                                        # Só adiciona se ainda não estiver nos dados memorizados
                                        if not dados_memoria or nome.lower() not in dados_memoria.lower():
                                            contexto_pessoal += f"Nome mencionado: {nome}. "
                                        break
                
                # Prepara historico para OpenAI (ultimas 5 mensagens)
                historico_para_openai = []
                if historico_usuario:
                    historico_para_openai = historico_usuario[-5:]
                
                # Detecta tags de contexto (momento emocional da usuária)
                contexto_tags = self._detectar_contexto_tags(pergunta, user_id)
                
                # Se cansaço_extremo foi detectado 3 vezes seguidas, adiciona sugestão proativa
                if "cansaço_extremo_critico" in contexto_tags:
                    # Sugestão proativa revisada por Mary - tom amoroso, não como ordem
                    # Ver docs/VALIDACAO_TOM_DE_VOZ_MARY.md
                    sugestao_proativa = "\n\n[SUGESTÃO PROATIVA IMPORTANTE]: A mãe parece muito exausta (cansaço detectado 3 vezes seguidas). A resposta da Sophia DEVE incluir naturalmente a sugestão: 'Que tal experimentar algo simples agora? Peça para alguém da sua confiança ficar com o bebê por apenas 30 minutos - nem que seja na sala enquanto você toma um banho calmo ou simplesmente fecha os olhos. Esse pequeno momento só seu pode fazer toda a diferença. Você merece esse cuidado. 💛' Integre essa sugestão de forma empática e fluida na resposta, como uma interrupção amorosa, não como uma ordem ou parágrafo separado."
                    contexto_pessoal += sugestao_proativa
                
                # Gera resposta usando OpenAI
                resposta_openai = self._gerar_resposta_openai(
                    pergunta,
                    user_id,
                    historico=historico_para_openai,
                    contexto_pessoal=contexto_pessoal or "",
                    contexto_tags=contexto_tags
                )
                
                if resposta_openai and resposta_openai.strip():
                    # SEMPRE usa a resposta da IA (OpenAI)
                    # A base local é APENAS para fallback se a IA falhar completamente
                    resposta_final = resposta_openai.strip()
                    fonte = "openai"
                    
                    logger.info(f"[CHAT] ✅ Resposta gerada pela IA (OpenAI) - {len(resposta_final)} caracteres")
                    
                    # Armazena resposta nas ultimas respostas para deteccao de repeticao
                    if user_id not in self.ultimas_respostas:
                        self.ultimas_respostas[user_id] = []
                    self.ultimas_respostas[user_id].append(resposta_final)
                    if len(self.ultimas_respostas[user_id]) > 3:
                        self.ultimas_respostas[user_id].pop(0)
                    
                    # Verifica repeticao
                    resposta_repetida = None
                    if len(self.ultimas_respostas[user_id]) >= 2:
                        for resposta_anterior in self.ultimas_respostas[user_id][:-1]:
                            similaridade_seq = difflib.SequenceMatcher(None, resposta_final.lower(), resposta_anterior.lower()).ratio()
                            palavras_final = set(resposta_final.lower().split())
                            palavras_anterior = set(resposta_anterior.lower().split())
                            if palavras_final and palavras_anterior:
                                similaridade_palavras = len(palavras_final.intersection(palavras_anterior)) / len(palavras_final.union(palavras_anterior))
                                similaridade_total = (similaridade_seq + similaridade_palavras) / 2
                                if similaridade_total > 0.80:
                                    resposta_repetida = resposta_anterior
                                    break
                    
                    # Se detectou repeticao, regenera resposta
                    if resposta_repetida:
                        logger.warning(f"[CHAT] Repeticao detectada - regenerando resposta")
                        resposta_regenerada = self._gerar_resposta_openai(
                            pergunta,
                            user_id,
                            historico=historico_para_openai,
                            contexto_pessoal=f"EVITE REPETIR: {resposta_repetida[:200]}"
                        )
                        if resposta_regenerada and len(resposta_regenerada.strip()) >= 150:
                            resposta_final = resposta_regenerada.strip()
                            fonte = "openai_regenerada"
                    
                    # Salva dados na memoria (apenas dados, nao conversas)
                    self._salvar_dados_memoria(user_id, pergunta, resposta_final)
                    
                    return {
                        "resposta": resposta_final,
                        "fonte": fonte,
                        "categoria": categoria,
                        "contexto_tags": contexto_tags if contexto_tags else []  # Inclui tags de contexto
                    }
                else:
                    # Resposta OpenAI vazia ou None
                    logger.warning(f"[CHAT] ⚠️ OpenAI retornou resposta vazia - usando fallback")
                    print(f"[CHAT] ⚠️ OpenAI retornou resposta vazia - usando fallback")
            except Exception as e:
                logger.error(f"[CHAT] ❌ Erro ao gerar resposta OpenAI: {e}", exc_info=True)
                import traceback
                traceback.print_exc()
                # Continua para fallback
        
        # Tenta usar Gemini (se configurado)
        elif usar_gemini:
            logger.info(f"[CHAT] Gemini disponível, tentando gerar resposta...")
            print(f"[CHAT] Gemini disponível, tentando gerar resposta...")
            try:
                # Prepara contexto para Gemini
                contexto_pessoal = ""
                
                # Carrega dados memorizados da Sophia (nomes, lugares, comidas)
                dados_memoria = self._obter_dados_memoria(user_id)
                if dados_memoria:
                    contexto_pessoal += dados_memoria + "\n\n"
                
                # Extrai informações pessoais adicionais do histórico (complemento)
                if historico_usuario:
                    for msg in historico_usuario[-10:]:
                        pergunta_hist = msg.get('pergunta', '').lower()
                        if 'me chamo' in pergunta_hist or 'meu nome e' in pergunta_hist:
                            palavras = pergunta_hist.split()
                            for i, palavra in enumerate(palavras):
                                if palavra in ['chamo', 'nome'] and i + 2 < len(palavras):
                                    nome = palavras[i+2]
                                    if nome not in ['sophia', 'e', 'a', 'o']:
                                        if not dados_memoria or nome.lower() not in dados_memoria.lower():
                                            contexto_pessoal += f"Nome mencionado: {nome}. "
                                        break
                
                # Prepara historico para Gemini (ultimas 5 mensagens)
                historico_para_gemini = []
                if historico_usuario:
                    historico_para_gemini = historico_usuario[-5:]
                
                # Gera resposta usando Gemini
                resposta_ia = self._gerar_resposta_gemini(
                    pergunta,
                    user_id,
                    historico=historico_para_gemini,
                    contexto_pessoal=contexto_pessoal or ""
                )
                
                if resposta_ia and resposta_ia.strip():
                    # SEMPRE usa a resposta da IA (Gemini)
                    resposta_final = resposta_ia.strip()
                    fonte = "gemini"
                    
                    logger.info(f"[CHAT] ✅ Resposta gerada pela IA (Gemini) - {len(resposta_final)} caracteres")
                    
                    # Armazena resposta nas ultimas respostas para deteccao de repeticao
                    if user_id not in self.ultimas_respostas:
                        self.ultimas_respostas[user_id] = []
                    self.ultimas_respostas[user_id].append(resposta_final)
                    if len(self.ultimas_respostas[user_id]) > 3:
                        self.ultimas_respostas[user_id].pop(0)
                    
                    # Verifica repeticao
                    resposta_repetida = None
                    if len(self.ultimas_respostas[user_id]) >= 2:
                        for resposta_anterior in self.ultimas_respostas[user_id][:-1]:
                            similaridade_seq = difflib.SequenceMatcher(None, resposta_final.lower(), resposta_anterior.lower()).ratio()
                            palavras_final = set(resposta_final.lower().split())
                            palavras_anterior = set(resposta_anterior.lower().split())
                            if palavras_final and palavras_anterior:
                                similaridade_palavras = len(palavras_final.intersection(palavras_anterior)) / len(palavras_final.union(palavras_anterior))
                                similaridade_total = (similaridade_seq + similaridade_palavras) / 2
                                if similaridade_total > 0.80:
                                    resposta_repetida = resposta_anterior
                                    break
                    
                    # Se detectou repeticao, regenera resposta
                    if resposta_repetida:
                        logger.warning(f"[CHAT] Repeticao detectada - regenerando resposta")
                        resposta_regenerada = self._gerar_resposta_gemini(
                            pergunta,
                            user_id,
                            historico=historico_para_gemini,
                            contexto_pessoal=f"EVITE REPETIR: {resposta_repetida[:200]}"
                        )
                        if resposta_regenerada and len(resposta_regenerada.strip()) >= 150:
                            resposta_final = resposta_regenerada.strip()
                            fonte = "gemini_regenerada"
                    
                    # Salva dados na memoria
                    self._salvar_dados_memoria(user_id, pergunta, resposta_final)
                    
                    return {
                        "resposta": resposta_final,
                        "fonte": fonte,
                        "categoria": categoria
                    }
                else:
                    # Resposta Gemini vazia ou None
                    logger.warning(f"[CHAT] ⚠️ Gemini retornou resposta vazia - usando fallback")
                    print(f"[CHAT] ⚠️ Gemini retornou resposta vazia - usando fallback")
            except Exception as e:
                logger.error(f"[CHAT] ❌ Erro ao gerar resposta Gemini: {e}", exc_info=True)
                import traceback
                traceback.print_exc()
                # Continua para fallback
        
        # Tenta usar Groq (se configurado)
        elif usar_groq:
            logger.info(f"[CHAT] Groq disponível, tentando gerar resposta...")
            print(f"[CHAT] Groq disponível, tentando gerar resposta...")
            try:
                # Prepara contexto para Groq
                contexto_pessoal = ""
                
                # Adiciona contexto do usuário (baby_profile e próxima vacina)
                if contexto_usuario:
                    if contexto_usuario.get('baby_name'):
                        contexto_pessoal += f"INFORMAÇÕES SOBRE O BEBÊ:\n"
                        contexto_pessoal += f"- Nome do bebê: {contexto_usuario['baby_name']}\n"
                        contexto_pessoal += f"- Idade: {contexto_usuario.get('baby_age_days', 0)} dias ({contexto_usuario.get('baby_age_months', 0)} meses)\n"
                    
                    if contexto_usuario.get('next_vaccine_name'):
                        contexto_pessoal += f"\nPRÓXIMA VACINA:\n"
                        contexto_pessoal += f"- Nome: {contexto_usuario['next_vaccine_name']}\n"
                        contexto_pessoal += f"- Data recomendada: {contexto_usuario['next_vaccine_date']}\n"
                        contexto_pessoal += f"- Dias até a vacina: {contexto_usuario['next_vaccine_days_until']}\n"
                    
                    contexto_pessoal += "\n"
                
                # Carrega dados memorizados da Sophia (nomes, lugares, comidas)
                dados_memoria = self._obter_dados_memoria(user_id)
                if dados_memoria:
                    contexto_pessoal += f"DADOS MEMORIZADOS:\n{dados_memoria}\n\n"
                
                # Extrai informações pessoais adicionais do histórico (complemento)
                if historico_usuario:
                    for msg in historico_usuario[-10:]:
                        pergunta_hist = msg.get('pergunta', '').lower()
                        if 'me chamo' in pergunta_hist or 'meu nome e' in pergunta_hist:
                            palavras = pergunta_hist.split()
                            for i, palavra in enumerate(palavras):
                                if palavra in ['chamo', 'nome'] and i + 2 < len(palavras):
                                    nome = palavras[i+2]
                                    if nome not in ['sophia', 'e', 'a', 'o']:
                                        if not dados_memoria or nome.lower() not in dados_memoria.lower():
                                            contexto_pessoal += f"Nome mencionado: {nome}. "
                                        break
                
                # Prepara historico para Groq (ultimas 5 mensagens)
                historico_para_groq = []
                if historico_usuario:
                    historico_para_groq = historico_usuario[-5:]
                
                # Detecta tags de contexto (momento emocional da usuária)
                contexto_tags = self._detectar_contexto_tags(pergunta, user_id)
                
                # Se cansaço_extremo foi detectado 3 vezes seguidas, adiciona sugestão proativa
                if "cansaço_extremo_critico" in contexto_tags:
                    sugestao_proativa = "\n\n[SUGESTÃO PROATIVA IMPORTANTE]: A mãe parece muito exausta (cansaço detectado 3 vezes seguidas). A resposta da Sophia DEVE incluir naturalmente a sugestão: 'Que tal experimentar algo simples agora? Peça para alguém da sua confiança ficar com o bebê por apenas 30 minutos - nem que seja na sala enquanto você toma um banho calmo ou simplesmente fecha os olhos. Esse pequeno momento só seu pode fazer toda a diferença. Você merece esse cuidado. 💛' Integre essa sugestão de forma empática e fluida na resposta, como uma interrupção amorosa, não como uma ordem ou parágrafo separado."
                    contexto_pessoal += sugestao_proativa
                
                # Classificador de risco: se crítico, ativa modo segurança (188/192/190/180)
                classificacao = self._classificar_risco(pergunta)
                modo_critico = (
                    classificacao["label"] in self.CLASSIFICADOR_CRITICOS
                    and classificacao["confidence"] >= 0.5
                )
                if modo_critico:
                    logger.info("[CHAT] Modo crítico ativado label=%s conf=%.2f", classificacao["label"], classificacao["confidence"])
                first_turn = not historico_para_groq
                already_greeted = self.user_greeted.get(user_id, False)
                
                # Gera resposta usando Groq
                resposta_groq = self._gerar_resposta_groq(
                    pergunta,
                    user_id,
                    historico=historico_para_groq,
                    contexto_pessoal=contexto_pessoal or "",
                    contexto_tags=contexto_tags,
                    modo_critico=modo_critico,
                    first_turn=first_turn,
                    already_greeted=already_greeted,
                )
                
                if resposta_groq and resposta_groq.strip():
                    # Marca que já cumprimentou nesta sessão (não repetir acolhimento)
                    self.user_greeted[user_id] = True
                    # SEMPRE usa a resposta da IA (Groq)
                    resposta_final = resposta_groq.strip()
                    fonte = "groq"
                    
                    logger.info(f"[CHAT] ✅ Resposta gerada pela IA (Groq) - {len(resposta_final)} caracteres")
                    
                    # Armazena resposta nas ultimas respostas para deteccao de repeticao (guardRepetition)
                    if user_id not in self.ultimas_respostas:
                        self.ultimas_respostas[user_id] = []
                    self.ultimas_respostas[user_id].append(resposta_final)
                    if len(self.ultimas_respostas[user_id]) > 3:
                        self.ultimas_respostas[user_id].pop(0)
                    
                    # guardRepetition: similaridade > 0.92 => pede variação breve
                    resposta_repetida = None
                    if len(self.ultimas_respostas[user_id]) >= 2:
                        for resposta_anterior in self.ultimas_respostas[user_id][:-1]:
                            similaridade_seq = difflib.SequenceMatcher(None, resposta_final.lower(), resposta_anterior.lower()).ratio()
                            palavras_final = set(resposta_final.lower().split())
                            palavras_anterior = set(resposta_anterior.lower().split())
                            if palavras_final and palavras_anterior:
                                similaridade_palavras = len(palavras_final.intersection(palavras_anterior)) / len(palavras_final.union(palavras_anterior))
                                similaridade_total = (similaridade_seq + similaridade_palavras) / 2
                                if similaridade_total > 0.92:
                                    resposta_repetida = resposta_anterior
                                    break
                    
                    if resposta_repetida:
                        logger.warning("[CHAT] guardRepetition: similaridade > 0.92 - regenerando com variação breve")
                        resposta_regenerada = self._gerar_resposta_groq(
                            pergunta,
                            user_id,
                            historico=historico_para_groq,
                            contexto_pessoal="Faça uma variação mais breve e sem repetir acolhimentos. Foque no próximo passo prático.",
                            contexto_tags=contexto_tags,
                            modo_critico=modo_critico,
                            first_turn=False,
                            already_greeted=True,
                        )
                        if resposta_regenerada and len(resposta_regenerada.strip()) >= 150:
                            resposta_final = resposta_regenerada.strip()
                            fonte = "groq_regenerada"
                    
                    # Salva dados na memoria
                    self._salvar_dados_memoria(user_id, pergunta, resposta_final)
                    
                    return {
                        "resposta": resposta_final,
                        "fonte": fonte,
                        "categoria": categoria,
                        "contexto_tags": contexto_tags if contexto_tags else []
                    }
                else:
                    # Resposta Groq vazia ou None
                    logger.warning(f"[CHAT] ⚠️ Groq retornou resposta vazia - usando fallback")
                    print(f"[CHAT] ⚠️ Groq retornou resposta vazia - usando fallback")
            except Exception as e:
                logger.error(f"[CHAT] ❌ Erro ao gerar resposta Groq: {e}", exc_info=True)
                import traceback
                traceback.print_exc()
                # Continua para fallback
        else:
            # Log detalhado do por que não está usando IA
            if AI_PROVIDER == "openai":
                if not self.openai_client:
                    logger.warning(f"[CHAT] ⚠️ OpenAI client não disponível - usando fallback")
                    print(f"[CHAT] ⚠️ OpenAI client não disponível - usando fallback")
                elif not self.assistant_id:
                    logger.warning(f"[CHAT] ⚠️ Assistant ID não disponível - usando fallback")
                    print(f"[CHAT] ⚠️ Assistant ID não disponível - usando fallback")
            elif AI_PROVIDER == "gemini":
                if not self.gemini_model:
                    logger.warning(f"[CHAT] ⚠️ Gemini model não disponível - usando fallback")
                    print(f"[CHAT] ⚠️ Gemini model não disponível - usando fallback")
            elif AI_PROVIDER == "groq":
                if not self.groq_client:
                    logger.warning(f"[CHAT] ⚠️ Groq client não disponível - usando fallback")
                    print(f"[CHAT] ⚠️ Groq client não disponível - usando fallback")
        
        # FALLBACK: Se OpenAI nao funcionou, busca resposta local como ultimo recurso
        if not resposta_final:
            logger.warning(f"[CHAT] ⚠️ OpenAI falhou ou retornou vazio - tentando fallback...")
            
            # Busca resposta local APENAS agora (fallback)
            if not is_saudacao and not is_declaracao_sentimento:
                resposta_local, categoria, similaridade = self.buscar_resposta_local(pergunta)
                # VALIDACAO ADICIONAL: Se encontrou resposta local, verifica se realmente corresponde a pergunta
                if resposta_local and similaridade > 0.45:
                    # Compara palavras-chave importantes da pergunta com a resposta
                    palavras_chave_pergunta = set(re.findall(r'\b\w{4,}\b', pergunta.lower()))
                    palavras_chave_resposta = set(re.findall(r'\b\w{4,}\b', resposta_local.lower()[:200]))
                    palavras_comuns = palavras_chave_pergunta.intersection(palavras_chave_resposta)
                    relevancia = len(palavras_comuns) / len(palavras_chave_pergunta) if len(palavras_chave_pergunta) > 0 else 0
                    
                    # Se relevancia for baixa, descarta resposta local
                    if relevancia < 0.4:
                        resposta_local = None
                        similaridade = 0
                        logger.info(f"[BUSCA] ⚠️ Resposta local descartada por baixa relevância ({relevancia:.2f})")
                elif resposta_local and similaridade <= 0.45:
                    # Se similaridade for baixa, descarta resposta local
                    resposta_local = None
                    similaridade = 0
                    logger.info(f"[BUSCA] ⚠️ Resposta local descartada por baixa similaridade ({similaridade:.2f})")
            
            # Usa fallback apropriado
            if is_pergunta_reciprocidade:
                logger.warning(f"[CHAT] OpenAI falhou para pergunta de reciprocidade - usando fallback")
                respostas_reciprocidade_fallback = [
                    "Meu dia está sendo muito bom! Estou aqui aprendendo e conversando com pessoas incríveis como você. Cada conversa me ensina algo novo e me deixa feliz em poder ajudar e apoiar. E o seu dia, como está sendo? Conte-me, aconteceu algo especial hoje?",
                    "Estou muito bem, obrigada por perguntar! Estou aqui, pronta para conversar e ajudar no que você precisar. É sempre bom quando alguém se importa em saber como estou também. E você, como está? Como está se sentindo hoje?",
                    "Meu dia está sendo tranquilo, aprendendo e conversando com pessoas incríveis como você. Cada conversa me ensina algo novo e me deixa feliz em poder ajudar. E o seu dia, como está sendo? Conte-me mais sobre você!"
                ]
                resposta_final = random.choice(respostas_reciprocidade_fallback)
                fonte = "resposta_reciprocidade_fallback"
            elif resposta_local:
                # Usa resposta local humanizada como fallback
                resposta_final = self.humanizar_resposta_local(resposta_local, pergunta)
                fonte = "local_humanizada_fallback"
                logger.info(f"[CHAT] ✅ Usando resposta local como fallback (categoria: {categoria})")
            elif is_saudacao:
                # Para saudações, cria resposta humanizada manualmente
                respostas_saudacao_fallback = [
                    "Oi! Que bom te ver por aqui! Como você está se sentindo hoje? Há algo específico em que posso te ajudar ou você só queria conversar? Estou aqui para te ouvir e apoiar no que precisar.",
                    "Olá! Fico feliz que você esteja aqui! Como você está? O que você gostaria de conversar hoje? Pode me contar sobre como você está se sentindo ou sobre o que está passando?",
                    "Oi! Estou aqui para te ajudar. Conte-me: como você está? Há algo que você gostaria de compartilhar ou alguma dúvida que eu possa ajudar a esclarecer?"
                ]
                resposta_final = random.choice(respostas_saudacao_fallback)
                fonte = "saudacao_humanizada_fallback"
            else:
                # Fallback generico
                resposta_final = "Desculpe, não consegui processar sua pergunta. Como posso te ajudar hoje?"
                fonte = "fallback"
            
            # Salva dados na memoria (apenas dados, nao conversas)
            self._salvar_dados_memoria(user_id, pergunta, resposta_final)
            
            out = {
                "resposta": resposta_final,
                "fonte": fonte,
                "categoria": categoria,
                "contexto_tags": []  # Fallback não tem tags de contexto
            }
            # Request ID para diagnóstico quando Groq falhou (rede/timeout/5xx)
            rid = getattr(self, "_last_groq_request_id", None)
            if rid:
                out["request_id"] = rid
            return out

# Inicializa instância global do chatbot (após definição da classe)
chatbot = ChatbotPuerperio()
app.chatbot = chatbot
logger.info("[CHATBOT] ✅ Instância global do chatbot criada com sucesso")
print("[CHATBOT] ✅ Instância global do chatbot criada com sucesso")

try:
    from backend.version import get_build_version
except Exception:
    def get_build_version():
        return "dev"

try:
    from backend.monitoring.appinsights import log_emergency_search
except Exception:
    log_emergency_search = None


@app.route("/version.json")
def version_json():
    resp = make_response(jsonify({"version": get_build_version()}), 200)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Vary"] = "Cookie"
    return resp


# Feature flags (SUS/esfera) expostas como JSON
@app.route("/flags.json")
def flags_json():
    show_sus = os.environ.get("SHOW_SUS_BADGES", "0").lower() in ("1", "true", "yes")
    show_own = os.environ.get("SHOW_OWNERSHIP_BADGES", "0").lower() in ("1", "true", "yes")
    resp = make_response(jsonify({"show_sus_badges": show_sus, "show_ownership_badges": show_own}), 200)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp


# Service Worker em /sw.js (escopo raiz; boot.js só registra quando page != login)
@app.route('/sw.js')
def sw_js():
    from flask import send_from_directory
    r = send_from_directory(app.static_folder, 'sw.js', mimetype='application/javascript')
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return r

# Rota raiz - renderiza a página principal
@app.route('/emergencia')
def emergencia():
    """
    Página de emergência obstétrica - Encontra maternidades próximas
    """
    return render_template('emergencia.html')

@app.route('/')
def index():
    """Rota principal que renderiza a interface do chatbot"""
    # Cache busting: usa get_build_version() para garantir que cada deploy gere URLs novas.
    # Evita que o usuário precise apagar o cache manualmente para ver melhorias.
    timestamp = get_build_version()
    
    # Verifica se arquivos minificados existem
    css_min_path = os.path.join(app.static_folder, 'css', 'style.min.css')
    js_min_path = os.path.join(app.static_folder, 'js', 'chat.min.js')
    # TEMPORARIAMENTE DESABILITADO: Minificação está quebrando o código
    # has_minified = os.path.exists(css_min_path) and os.path.exists(js_min_path)
    has_minified = False  # Usar versão não-minificada até corrigir o script de minificação
    
    # Code-splitting: login não carrega chat.js; parse error em chat.js não quebra login
    page = 'login' if not current_user.is_authenticated else 'app'
    login_error = request.args.get('login_error')
    return render_template('index.html', timestamp=timestamp, has_minified=has_minified, page=page, login_error=login_error)


# /conteudos e /api/educational migrados para backend.blueprints.edu_routes (edu_bp)


@app.route("/privacidade")
def page_privacidade():
    return render_template("legal_privacidade.html")


@app.route("/termos")
def page_termos():
    return render_template("legal_termos.html")


# /api/educational migrado para backend.blueprints.edu_routes (edu_bp)

# NOTA: A integração do FastAPI está DESABILITADA
# O Flask responde diretamente em todas as rotas (/api/* e /)
# Se precisar do FastAPI, rode-o em processo/porta separados (ex.: uvicorn backend.api.main:app --port 8000)

# Rotas /api/v1/facilities, /api/v1/emergency, /api/v1/health, /api/v1/debug/* → backend.blueprints.health_routes (health_bp)

@app.route("/healthz", methods=["GET"])
def health():
    """Health check simples para load balancer / Render (path exato /healthz)."""
    return "ok", 200


@app.route('/__debug/routes', methods=['GET'])
def __debug_routes():
    """Lista endpoints registrados (inspeção). Remover em produção se desejar."""
    skip = {'HEAD', 'OPTIONS'}
    url_map = getattr(app, 'url_map', None)
    rules = list(url_map.iter_rules()) if url_map else []
    routes = sorted([
        f"{','.join(sorted(m for m in rule.methods if m not in skip))} {rule.rule}"
        for rule in rules
        if rule.rule != '/static/<path:filename>'
    ])
    return jsonify(routes)



@app.route('/api/test', methods=['GET'])
def api_test():
    """Rota de teste para verificar se o Flask está funcionando"""
    try:
        return jsonify({
            "status": "ok",
            "message": "Flask está funcionando!",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"[TEST] Erro na rota de teste: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/favicon.ico', methods=['GET', 'HEAD'])
def favicon():
    """Rota para favicon.ico - retorna 204 (No Content) para evitar 404"""
    from flask import Response
    response = Response(status=204)
    response.headers['Content-Type'] = 'image/x-icon'
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # Cache por 1 ano
    return response

# ------------------------------------------------------------------------
# Dummies para evitar 500 enquanto autenticacao nao esta ativa
# ------------------------------------------------------------------------
# Rotas dummy removidas - usando rotas reais abaixo

@app.route('/static/favicon.ico', methods=['GET', 'HEAD'])
def static_favicon():
    """Rota para /static/favicon.ico - retorna 204 (No Content) para evitar 404"""
    from flask import Response
    response = Response(status=204)
    response.headers['Content-Type'] = 'image/x-icon'
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # Cache por 1 ano
    return response

@app.route('/manifest.json', methods=['GET', 'HEAD'])
def manifest_json():
    """Serve manifest PWA - evita 404 que alguns navegadores solicitam ao ver meta mobile-web-app-capable"""
    return app.send_static_file('manifest.json')

@app.route('/static/img/edu/cancer-mama.png', methods=['GET', 'HEAD'])
def edu_cancer_mama_png():
    """Serve imagem Câncer de Mama de forma persistente."""
    from flask import send_from_directory, abort
    path = os.path.join(app.static_folder, 'img', 'edu')
    filename = 'cancer-mama.png'
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        # Fallback: tenta variações do nome
        for alt_name in ['Cancer de Mama.png', 'Câncer de Mama.png', 'cancer-mama.jpg']:
            alt_path = os.path.join(path, alt_name)
            if os.path.exists(alt_path):
                return send_from_directory(path, alt_name, mimetype='image/png')
        abort(404)
    return send_from_directory(path, filename, mimetype='image/png')

@app.route('/static/img/edu/doacao-leite-materno.png', methods=['GET', 'HEAD'])
def edu_doacao_leite_png():
    """Serve imagem Doação de Leite via URL sem acentos (evita 404 em alguns navegadores/proxies)."""
    from flask import send_from_directory, abort
    path = os.path.join(app.static_folder, 'img', 'edu')
    # Lista todos os arquivos na pasta e procura por arquivos relacionados a "leite" ou "doacao"
    try:
        all_files = os.listdir(path)
        # Procura arquivo que contenha "leite" ou "doacao" no nome (case-insensitive)
        for filename in all_files:
            filename_lower = filename.lower()
            if ('leite' in filename_lower or 'doacao' in filename_lower) and filename_lower.endswith('.png'):
                file_path = os.path.join(path, filename)
                if os.path.exists(file_path):
                    return send_from_directory(path, filename, mimetype='image/png')
    except Exception as e:
        logger.warning(f"[EDU] Erro ao listar arquivos: {e}")
    
    # Fallback: tenta nomes conhecidos
    candidates = ['Doação de Leite Materno.png', 'doacao-leite-materno.png', 
                  'Doacao de Leite Materno.png', 'doacao-de-leite.png']
    for filename in candidates:
        file_path = os.path.join(path, filename)
        if os.path.exists(file_path):
            return send_from_directory(path, filename, mimetype='image/png')
    abort(404)

@app.route('/static/img/edu/aleitamento.png', methods=['GET', 'HEAD'])
def edu_aleitamento_png():
    """Serve imagem Aleitamento de forma persistente."""
    from flask import send_from_directory, abort
    path = os.path.join(app.static_folder, 'img', 'edu')
    filename = 'aleitamento.png'
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        # Fallback: tenta variações do nome
        for alt_name in ['Aleitamento.png', 'Aleitamento Materno.png', 'Amamentação.png', 
                        'aleitamento.jpg', 'breastfeeding.png']:
            alt_path = os.path.join(path, alt_name)
            if os.path.exists(alt_path):
                return send_from_directory(path, alt_name, mimetype='image/png')
        abort(404)
    return send_from_directory(path, filename, mimetype='image/png')

# Rota /forgot-password → backend.blueprints.auth_routes (auth_bp)
# Rotas /api/chat, /api/historico, /api/categorias, /api/alertas, /api/guias, /api/cuidados, /api/triagem-emocional, /api/limpar-memoria-ia → backend.blueprints.chat_routes (chat_bp)

# get_user_context: usado pelo chat_bp para contexto do usuário (baby_profile, próxima vacina)
def get_user_context(user_id):
    """Busca contexto do usuário: baby_profile e próxima vacina. Usado por chat_bp."""
    if not user_id:
        return None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, birth_date FROM baby_profiles WHERE user_id = ? LIMIT 1', (user_id,))
        baby_row = cursor.fetchone()
        if not baby_row:
            conn.close()
            return None
        baby = dict(baby_row)
        birth_date = datetime.strptime(baby['birth_date'], '%Y-%m-%d').date()
        today = date.today()
        age_delta = relativedelta(today, birth_date)
        age_days = (today - birth_date).days
        age_months = age_delta.months + (age_delta.years * 12)
        cursor.execute('''
            SELECT vaccine_name, recommended_date FROM vaccination_schedule
            WHERE baby_profile_id = ? AND status = 'pending' AND recommended_date IS NOT NULL
            ORDER BY recommended_date ASC LIMIT 1
        ''', (baby['id'],))
        next_vaccine_row = cursor.fetchone()
        conn.close()
        contexto = {'baby_name': baby['name'], 'baby_age_days': age_days, 'baby_age_months': age_months}
        if next_vaccine_row:
            next_vaccine = dict(next_vaccine_row)
            recommended_date = datetime.strptime(next_vaccine['recommended_date'], '%Y-%m-%d').date()
            contexto['next_vaccine_name'] = next_vaccine['vaccine_name']
            contexto['next_vaccine_date'] = next_vaccine['recommended_date']
            contexto['next_vaccine_days_until'] = (recommended_date - today).days
        return contexto
    except Exception as e:
        logger.error("Erro ao buscar contexto do usuário: %s", e, exc_info=True)
        return None

app.get_user_context = get_user_context

# ENDPOINT DESATIVADO: Funcionalidade de vídeos removida temporariamente
# @app.route('/api/youtube-search', methods=['POST'])
def api_youtube_search_disabled():
    """
    Busca vídeos no YouTube usando YouTube Data API v3.
    Usado para preencher vídeos dinamicamente quando video_id é null no JSON.
    WHITELIST: Apenas canais oficiais verificados são permitidos.
    """
    try:
        if not YOUTUBE_API_KEY:
            return jsonify({
                "erro": "YouTube API não configurada",
                "fallback": True
            }), 503
        
        data = request.get_json() or {}
        query = data.get('query', '')
        channel_id = data.get('channel_id', '')  # ID do canal (opcional)
        max_results = data.get('max_results', 5)
        order = data.get('order', 'relevance')  # relevance, date, rating, viewCount
        
        if not query:
            return jsonify({"erro": "Query de busca não fornecida"}), 400
        
        # Importa requests se necessário
        try:
            import requests
            import re
        except ImportError:
            return jsonify({"erro": "Biblioteca requests não instalada"}), 500
        
        # WHITELIST DE CANAIS OFICIAIS
        # Canais permitidos (nomes de usuário/@handles dos canais oficiais)
        ALLOWED_CHANNEL_HANDLES = [
            '@ministeriodasaude',
            '@canalsaudeoficial',
            '@fisioterapiasaudepelvicaobstetricahcfmusp',
            '@hcfmuspoficial'
        ]
        
        # TAGS DE RELEVÂNCIA: Adiciona termos obrigatórios à query se não estiverem presentes
        relevant_terms = ['pós-parto', 'saúde da mulher', 'cuidados com o bebê', 'puerpério']
        query_lower = query.lower()
        missing_terms = [term for term in relevant_terms if term not in query_lower]
        if missing_terms:
            # Adiciona pelo menos um termo de relevância se nenhum estiver presente
            query = query + ' ' + ' '.join(relevant_terms[:1])
        
        # Monta URL da API
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': min(max_results, 50),  # Limita a 50 (máximo da API)
            'order': order,
            'key': YOUTUBE_API_KEY,
            'safeSearch': 'strict',  # FILTRO DE SEGURANÇA: Modo seguro obrigatório
            'relevanceLanguage': 'pt'  # Prioriza conteúdo em português
        }
        
        # NOTA: A API do YouTube não aceita handles (@username) diretamente no channelId
        # A verificação de canais será feita pós-busca usando channelTitle
        # O channel_id fornecido é usado apenas para melhorar a relevância da busca
        
        # Faz requisição para API
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({
                "erro": "Nenhum vídeo encontrado",
                "fallback": True
            }), 404
        
        # Mapeia resultados e FILTRA por canais verificados
        videos = []
        for item in items:
            snippet = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId')
            channel_title = snippet.get('channelTitle', '')
            channel_id_api = snippet.get('channelId', '')
            
            if not video_id:
                continue
            
            # VERIFICAÇÃO MANUAL: Verifica se o vídeo é de um canal verificado
            # Verifica pelo channelTitle (nome do canal) e keywords específicas
            is_verified_channel = False
            
            # Nomes de canais oficiais verificados (case-insensitive)
            verified_channel_names = [
                'ministério da saúde',
                'ministerio da saude',
                'canal saúde',
                'canal saude',
                'fiocruz',
                'hospital das clínicas',
                'hcfmusp',
                'fisioterapia',
                'saúde pélvica',
                'saude pelvica'
            ]
            
            # Verifica se o nome do canal contém algum dos nomes verificados
            channel_title_lower = channel_title.lower()
            for verified_name in verified_channel_names:
                if verified_name in channel_title_lower:
                    is_verified_channel = True
                    logger.info(f"[YOUTUBE] ✅ Canal verificado: {channel_title}")
                    break
            
            # APENAS ADICIONA VÍDEOS DE CANAIS VERIFICADOS
            if not is_verified_channel:
                logger.warning(f"[YOUTUBE] ❌ Vídeo rejeitado - canal não verificado: '{channel_title}' (ID: {channel_id_api})")
                continue
            
            videos.append({
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', '')[:200] + '...' if len(snippet.get('description', '')) > 200 else snippet.get('description', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url') or snippet.get('thumbnails', {}).get('medium', {}).get('url') or snippet.get('thumbnails', {}).get('default', {}).get('url'),
                'channel_title': channel_title,
                'channel_id': channel_id_api,
                'published_at': snippet.get('publishedAt', ''),
                'embed_url': f'https://www.youtube.com/embed/{video_id}'
            })
        
        # Retorna lista de resultados ou um resultado específico
        if videos:
            # Se foi solicitado índice específico, retorna esse vídeo
            index = data.get('index', None)
            if index is not None and index >= 0 and index < len(videos):
                return jsonify(videos[index])
            # Se foi solicitado aleatório, retorna um aleatório
            if data.get('random', False):
                import random
                return jsonify(random.choice(videos))
            # Por padrão, retorna todos os resultados
            return jsonify({
                "videos": videos,
                "count": len(videos)
            })
        
        return jsonify({
            "erro": "Nenhum vídeo válido encontrado",
            "fallback": True
        }), 404
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[YOUTUBE] Erro na requisição à API: {e}")
        return jsonify({
            "erro": f"Erro ao buscar vídeos: {str(e)}",
            "fallback": True
        }), 500
    except Exception as e:
        logger.error(f"[YOUTUBE] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "erro": "Erro inesperado ao buscar vídeos",
            "fallback": True
        }), 500
# Rotas /api/vacinas/*, /api/baby_profile, /api/vaccination/* → backend.blueprints.health_routes (health_bp)
# Rotas de auth (login, cadastro, user, logout, forgot-password, reset, verify-email) → backend.blueprints.auth_routes (auth_bp)

@app.route('/api/feedback', methods=['POST'])
@login_required
def api_feedback():
    """Recebe feedback do usuário e salva em logs/user_feedback.log"""
    try:
        data = request.get_json()
        rating = data.get('rating', '')
        comment = data.get('comment', '')
        question1 = data.get('question1', '')
        question2 = data.get('question2', '')
        
        if not rating:
            return jsonify({'error': 'Rating (emoji) é obrigatório'}), 400
        
        # Cria pasta logs se não existir
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(backend_dir) if backend_dir else os.getcwd()
        logs_dir = os.path.join(project_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        feedback_log_file = os.path.join(logs_dir, 'user_feedback.log')
        
        # Busca informações do usuário
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email FROM users WHERE id = ?', (int(current_user.id),))
        user_data = cursor.fetchone()
        conn.close()
        
        user_id = user_data[0] if user_data else 'unknown'
        user_name = user_data[1] if user_data else 'unknown'
        user_email = user_data[2] if user_data else 'unknown'
        
        # Formata entrada de log (inclui User-Agent para identificar dispositivo)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_agent = request.headers.get('User-Agent', 'N/A')
        feedback_entry = f"""
{'='*80}
FEEDBACK - {timestamp}
{'='*80}
User ID: {user_id}
Nome: {user_name}
Email: {user_email}
User-Agent: {user_agent}
Rating: {rating}
Pergunta 1: {question1}
Pergunta 2: {question2}
Comentário: {comment}
{'='*80}

"""
        
        # Salva no arquivo de log
        try:
            with open(feedback_log_file, 'a', encoding='utf-8') as f:
                f.write(feedback_entry)
            logger.info(f"[FEEDBACK] ✅ Feedback salvo de usuário {user_id} ({user_name})")
            print(f"[FEEDBACK] ✅ Feedback salvo em: {feedback_log_file}")
        except Exception as log_error:
            logger.error(f"[FEEDBACK] ❌ Erro ao salvar feedback: {log_error}")
            return jsonify({'error': 'Erro ao salvar feedback'}), 500
        
        # Mensagem de agradecimento definida pela Mary (Analyst)
        # Ver docs/PERGUNTAS_FEEDBACK_MARY.md
        return jsonify({
            'success': True,
            'message': 'Obrigada por nos ajudar a cuidar melhor de você! 💕'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar feedback: {e}", exc_info=True)
        return jsonify({'error': f'Erro ao processar feedback: {str(e)}'}), 500

# Rota para teste
@app.route('/teste')
def teste():
    return jsonify({
        "status": "funcionando",
        "base_conhecimento": len(base_conhecimento),
        "mensagens_apoio": len(mensagens_apoio),
        "telefones_carregados": bool(telefones_uteis),
        "guias_praticos": len(guias_praticos),
        "cuidados_gestacao": len(cuidados_gestacao),
        "cuidados_pos_parto": len(cuidados_pos_parto),
        "vacinas": "mae e bebe carregadas",
        "rotas_api": 9,
        "openai_disponivel": openai_client is not None
    })

if PERF_LOG or PERF_EXPOSE:
    _PERF_IMPORT_MS = round((time.perf_counter() - _T_IMPORT_START) * 1000, 0)
    app._perf_import_ms = _PERF_IMPORT_MS
    app._perf_first_req_ms = getattr(app, "_perf_first_req_ms", None)
    app._perf_first_req_at = getattr(app, "_perf_first_req_at", None)
    _perf_logger.info("[PERF] import backend.app: %.0f ms", _PERF_IMPORT_MS)

if __name__ == "__main__":
    print("="*50)
    print("Chatbot do Puerperio - Sistema Completo!")
    print("="*50)
    print("Base de conhecimento:", len(base_conhecimento), "categorias")
    print("Mensagens de apoio:", len(mensagens_apoio), "mensagens")
    print("Telefones úteis: Carregado ✓")
    print("Guias práticos:", len(guias_praticos), "guias")
    print("Cuidados gestação:", len(cuidados_gestacao), "trimestres")
    print("Cuidados puerpério:", len(cuidados_pos_parto), "períodos")
    print("Vacinas: Mãe e bebê carregadas ✓")
    logger.info("[llm] OpenAI disponível: %s", "Sim" if openai_client else "Não")
    print("Total de rotas API:", 12)
    print("="*50)
    
    # Descobre o IP local automaticamente
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "192.168.0.10"  # Fallback
    
    port = int(os.environ.get("PORT", 5000))
    
    print("\n🚀 Servidor iniciando...")
    print("\n💻 Acesse no COMPUTADOR:")
    print(f"   http://localhost:{port}")
    print(f"   http://127.0.0.1:{port}")
    print("\n📱 Acesse no CELULAR (mesma rede WiFi):")
    print(f"   http://{local_ip}:{port}")
    print("\nIMPORTANTE:")
    print("   - Celular e computador devem estar na MESMA rede WiFi")
    print("   - Se nao funcionar, verifique o firewall do Windows")
    print("="*50)
    
    # Configura tratamento de sinais para shutdown limpo
    import signal
    import atexit
    
    def shutdown_handler(signum=None, frame=None):
        """Handler para shutdown limpo"""
        print("\n\nEncerrando servidor...")
        try:
            # Tenta fazer shutdown limpo
            if hasattr(app, 'do_teardown_appcontext'):
                app.do_teardown_appcontext()
        except:
            pass
        sys.exit(0)
    
    # Registra handlers
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    atexit.register(shutdown_handler)
    
    # Configura APScheduler para tarefas agendadas (lembretes de vacinação)
    try:
        from backend.tasks.vaccination_reminders import send_vaccination_reminders
        
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(
            func=send_vaccination_reminders,
            trigger=CronTrigger(hour=9, minute=0),  # Diariamente às 09:00
            id='vaccination_reminders',
            name='Lembretes de Vacinação',
            replace_existing=True
        )
        scheduler.start()
        logger.info("[SCHEDULER] ✅ APScheduler iniciado - Lembretes agendados para 09:00 diariamente")
        print("[SCHEDULER] ✅ APScheduler iniciado - Lembretes agendados para 09:00 diariamente")
        
        # Garante que o scheduler é parado ao encerrar a aplicação
        atexit.register(lambda: scheduler.shutdown(wait=False) if 'scheduler' in locals() else None)
    except Exception as e:
        logger.error(f"[SCHEDULER] ❌ Erro ao configurar APScheduler: {e}")
        print(f"[SCHEDULER] ❌ Erro ao configurar APScheduler: {e}")
        # Continua a aplicação mesmo se o scheduler falhar
    
    # Rotas do chatbot
    try:
        from backend.chat.router import CHAT_BP
        app.register_blueprint(CHAT_BP)
        logger.info("[CHAT] ✅ Chat router registrado")
    except Exception as e:
        logger.warning("[CHAT] ⚠️ Chat router indisponível: %s", e)
    
    # Rota admin para playground do chat (protegida)
    @app.get("/admin/chat")
    def admin_chat_playground():
        """Playground do chatbot (protegido por admin)."""
        ok, err = _admin_allowed()
        if not ok:
            msg, code = err if err else ("disabled", 404)
            return jsonify({"ok": False, "error": msg}), code
        from flask import send_from_directory
        return send_from_directory("backend/static", "chat-playground.html")
    
    # Configura Flask para shutdown mais limpo
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False, threaded=True)

