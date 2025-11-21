# -*- coding: utf-8 -*-
import os
import sys

# Configura encoding UTF-8 para Windows (antes de qualquer print com emojis)
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

import time
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
import unicodedata
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, session, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from dotenv import load_dotenv
from collections import defaultdict, Counter

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
except ImportError:
    NLTK_AVAILABLE = False
except Exception as e:
    NLTK_AVAILABLE = False
    # Logger ainda não está configurado aqui, usa print temporariamente
    print(f"[NLTK] ⚠️ NLTK não disponível: {e}")

# Configuração de logging (após imports básicos, antes de usar logger)
if not logging.getLogger().handlers:  # Evita reconfigurar se já foi configurado
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
logger = logging.getLogger(__name__)

# Agora pode usar logger para NLTK
if NLTK_AVAILABLE:
    logger.info("[NLTK] ✅ NLTK importado com sucesso")
else:
    logger.info("[NLTK] ℹ️ NLTK não disponível (opcional - usando fallback)")

# Verifica se openai está disponível
OPENAI_AVAILABLE = False
openai_client = None
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    logger.info("[OPENAI] Biblioteca openai importada com sucesso")
    print("[OPENAI] Biblioteca openai importada com sucesso")
except ImportError as e:
    OPENAI_AVAILABLE = False
    openai_client = None
    logger.warning(f"[OPENAI] ERRO ao importar openai: {e}")
    print(f"[OPENAI] ERRO ao importar openai: {e}")
    print("[OPENAI] Execute: pip install openai")
except Exception as e:
    OPENAI_AVAILABLE = False
    openai_client = None
    logger.error(f"[OPENAI] ERRO inesperado ao importar openai: {e}")
    print(f"[OPENAI] ERRO inesperado ao importar openai: {e}")
    import traceback
    traceback.print_exc()

# Logger já foi configurado acima (antes da importação do NLTK)

# Carrega variáveis de ambiente
# Carrega .env da raiz do projeto (múltiplos caminhos possíveis)
env_paths = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),  # Raiz do projeto
    os.path.join(os.path.dirname(__file__), ".env"),  # Pasta backend
    ".env",  # Caminho relativo atual
]

env_loaded = False
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        logger.info(f"[ENV] ✅ Arquivo .env carregado de: {env_path}")
        print(f"[ENV] ✅ Arquivo .env carregado de: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    logger.warning("[ENV] ⚠️ Arquivo .env não encontrado em nenhum dos caminhos testados")
    print("[ENV] ⚠️ Arquivo .env não encontrado - tentando carregar do diretório atual")
    load_dotenv()  # Tenta carregar do diretório atual

# Verifica se as variáveis de email foram carregadas (após load_dotenv)
mail_username_env = os.getenv('MAIL_USERNAME')
mail_password_env = os.getenv('MAIL_PASSWORD')
mail_server_env = os.getenv('MAIL_SERVER')

if mail_username_env and mail_password_env:
    logger.info(f"[ENV] ✅ Variáveis de email carregadas: MAIL_USERNAME={mail_username_env[:5]}...")
    print(f"[ENV] ✅ Variáveis de email carregadas: MAIL_USERNAME={mail_username_env}")
else:
    logger.warning("[ENV] ⚠️ MAIL_USERNAME ou MAIL_PASSWORD não encontrados no .env")
    print("[ENV] ⚠️ MAIL_USERNAME ou MAIL_PASSWORD não encontrados no .env")
    print("[ENV]    - Verifique se o arquivo .env existe e contém essas variáveis")
    print("[ENV]    - Em desenvolvimento, emails serão apenas logados no console")

# Inicializa o Flask com os caminhos corretos
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            static_url_path='/static')

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sua-chave-secreta-super-segura-mude-isso-em-producao')
BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "dados")
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")
# Flag para controlar uso de IA (permite desabilitar completamente)
USE_AI = os.getenv("USE_AI", "true").lower() == "true"
logger.info(f"[IA] 🔍 USE_AI configurado: {USE_AI}")
print(f"[IA] 🔍 USE_AI configurado: {USE_AI}")

# Carrega OPENAI_API_KEY com múltiplas tentativas (apenas se USE_AI estiver habilitado)
OPENAI_API_KEY = None
OPENAI_ASSISTANT_ID = None
if USE_AI:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
    if not OPENAI_API_KEY:
        # Tenta recarregar se não encontrou
        logger.warning("[OPENAI] OPENAI_API_KEY não encontrada na primeira tentativa, recarregando .env...")
        print("[OPENAI] OPENAI_API_KEY não encontrada na primeira tentativa, recarregando .env...")
        for env_path in env_paths:
            if os.path.exists(env_path):
                logger.info(f"[OPENAI] Recarregando .env de: {env_path}")
                print(f"[OPENAI] Recarregando .env de: {env_path}")
                load_dotenv(env_path, override=True)
                OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
                OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
                if OPENAI_API_KEY:
                    logger.info(f"[OPENAI] OPENAI_API_KEY carregada após recarregar (length: {len(OPENAI_API_KEY)})")
                    print(f"[OPENAI] OPENAI_API_KEY carregada após recarregar (length: {len(OPENAI_API_KEY)})")
                    break

    if OPENAI_API_KEY:
        logger.info(f"[OPENAI] OPENAI_API_KEY encontrada (length: {len(OPENAI_API_KEY)})")
        print(f"[OPENAI] OPENAI_API_KEY encontrada (length: {len(OPENAI_API_KEY)})")
    else:
        logger.error("[OPENAI] OPENAI_API_KEY NAO encontrada após todas as tentativas!")
else:
    logger.info("[IA] USE_AI=false - IA desabilitada, usando apenas base local humanizada")
    print("[IA] USE_AI=false - IA desabilitada, usando apenas base local humanizada")

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

# Headers de cache e performance para recursos estáticos
@app.after_request
def add_cache_headers(response):
    """Adiciona headers de cache e compressão para melhorar performance"""
    # API endpoints de dados JSON não devem ser cacheados (sempre atualizados)
    if request.path.startswith('/api/'):
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.cache_control.must_revalidate = True
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Cache para recursos estáticos (CSS, JS, imagens)
    elif request.endpoint == 'static' or request.path.startswith('/static/'):
        # Cache de 1 ano para recursos estáticos com versionamento
        if '?v=' in request.path or request.path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.woff', '.woff2')):
            response.cache_control.max_age = 31536000  # 1 ano
            response.cache_control.public = True
            response.cache_control.immutable = True
        else:
            # Cache menor para outros recursos
            response.cache_control.max_age = 3600  # 1 hora
            response.cache_control.public = True
    
    # Headers de segurança e performance
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Compressão (se disponível via servidor proxy/reverse proxy)
    if request.path.endswith(('.css', '.js', '.html', '.json')):
        response.headers['Vary'] = 'Accept-Encoding'
    
    return response

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
# Usa "basic" para melhor compatibilidade com mobile e diferentes IPs
# "strong" pode causar problemas em dispositivos móveis com mudança de rede
login_manager.session_protection = "basic"

# Inicializa cliente OpenAI se a chave estiver disponível E USE_AI estiver habilitado
if USE_AI and OPENAI_AVAILABLE and OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("[OPENAI] Cliente OpenAI inicializado com sucesso")
        print("[OPENAI] Cliente OpenAI inicializado com sucesso")
        
        # Cria ou obtém assistente Sophia se não tiver ID
        if not OPENAI_ASSISTANT_ID:
            logger.info("[OPENAI] Criando assistente Sophia...")
            print("[OPENAI] Criando assistente Sophia...")
            # O assistente será criado na primeira chamada se necessário
        else:
            logger.info(f"[OPENAI] Usando assistente existente: {OPENAI_ASSISTANT_ID}")
            print(f"[OPENAI] Usando assistente existente: {OPENAI_ASSISTANT_ID}")
    except Exception as e:
        logger.error(f"[OPENAI] Erro ao inicializar OpenAI: {e}")
        print(f"[OPENAI] Erro ao inicializar OpenAI: {e}")
        openai_client = None
else:
    openai_client = None
    if not USE_AI:
        logger.info("[IA] IA desabilitada (USE_AI=false) - usando apenas base local humanizada")
        print("[IA] IA desabilitada (USE_AI=false) - usando apenas base local humanizada")
    elif not OPENAI_AVAILABLE:
        logger.warning("[OPENAI] Biblioteca openai nao instalada - execute: pip install openai")
        print("[OPENAI] Biblioteca nao instalada - execute: pip install openai")
    elif not OPENAI_API_KEY:
        logger.warning("[OPENAI] OPENAI_API_KEY nao configurada - respostas serao da base local (humanizadas)")
        print("[OPENAI] OPENAI_API_KEY nao configurada - respostas serao da base local (humanizadas)")

logger.info(f"[OPENAI] Status final: openai_client = {openai_client is not None}")
print(f"[OPENAI] Status final: openai_client disponivel = {openai_client is not None}")

# Classe User para Flask-Login
class User(UserMixin):
    def __init__(self, user_id, name, email, baby_name=None):
        self.id = str(user_id)
        self.name = name
        self.email = email
        self.baby_name = baby_name

# Função para inicializar banco de dados
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifica se as colunas já existem (para migração)
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Cria tabela users com novos campos
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
    
    # Adiciona novas colunas se não existirem (migração)
    if 'email_verified' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0')
    if 'email_verification_token' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN email_verification_token TEXT')
    if 'reset_password_token' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN reset_password_token TEXT')
    if 'reset_password_expires' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN reset_password_expires TIMESTAMP')
    
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

# Inicializa DB na startup
init_db()

# Funções auxiliares
def generate_token(length=32):
    """Gera um token seguro"""
    return secrets.token_urlsafe(length)

def send_email(to, subject, body, sender=None):
    """Envia um email (fallback se não configurado)"""
    try:
        # Log detalhado ANTES de tentar enviar
        logger.info(f"[EMAIL] 🔍 Iniciando envio de email...")
        logger.info(f"[EMAIL] 🔍 MAIL_USERNAME configurado: {bool(app.config.get('MAIL_USERNAME'))}")
        logger.info(f"[EMAIL] 🔍 MAIL_PASSWORD configurado: {bool(app.config.get('MAIL_PASSWORD'))}")
        logger.info(f"[EMAIL] 🔍 MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        logger.info(f"[EMAIL] 🔍 MAIL_PORT: {app.config.get('MAIL_PORT')}")
        logger.info(f"[EMAIL] 🔍 MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"[EMAIL] 🔍 Iniciando envio de email...")
        print(f"[EMAIL] 🔍 MAIL_USERNAME configurado: {bool(app.config.get('MAIL_USERNAME'))}")
        print(f"[EMAIL] 🔍 MAIL_PASSWORD configurado: {bool(app.config.get('MAIL_PASSWORD'))}")
        print(f"[EMAIL] 🔍 MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"[EMAIL] 🔍 MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"[EMAIL] 🔍 MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
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
            # Se email não estiver configurado, apenas loga
            from_email = sender or app.config['MAIL_DEFAULT_SENDER']
            logger.warning(f"[EMAIL] ⚠️ EMAIL NÃO CONFIGURADO - Email seria enviado (apenas logado no console)")
            logger.warning(f"[EMAIL] Para: {to}")
            logger.warning(f"[EMAIL] Assunto: {subject}")
            logger.warning(f"[EMAIL] Configure MAIL_USERNAME e MAIL_PASSWORD no arquivo .env para enviar emails reais")
            print(f"[EMAIL] ⚠️ (Console - Email não configurado) De: {from_email} | Para: {to}")
            print(f"[EMAIL] Assunto: {subject}")
            print(f"[EMAIL] Mensagem: {body}")
            print(f"[EMAIL] ⚠️ Configure MAIL_USERNAME e MAIL_PASSWORD no arquivo .env para enviar emails reais")
            return True
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
    
    subject = "Verifique seu email - Assistente Puerpério 💕"
    body = f"""
Olá {name}! 💕

Bem-vinda ao Assistente Puerpério! Para ativar sua conta, clique no link abaixo:

{verification_url}

Este link é válido por 24 horas.

Se você não criou esta conta, pode ignorar este email.

Com carinho,
Equipe Assistente Puerpério 🤱
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
    """Envia email de recuperação de senha"""
    base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
    reset_url = f"{base_url}/reset-password?token={token}"
    
    subject = "Recuperação de Senha - Assistente Puerpério 🔐"
    body = f"""
Olá {name}! 💕

Você solicitou a recuperação de senha. Clique no link abaixo para redefinir sua senha:

{reset_url}

Este link é válido por 1 hora.

Se você não solicitou esta recuperação, pode ignorar este email.

Com carinho,
Equipe Assistente Puerpério 🤱
"""
    send_email(email, subject, body)

# User loader para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_PATH)
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

# Histórico de conversas em memória (cache para performance)
# As conversas também são salvas no banco de dados para persistência
conversas = {}

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
        
        # Armazena clientes OpenAI e threads por usuário
        self.openai_client = openai_client
        self.assistant_id = OPENAI_ASSISTANT_ID
        self.user_threads = {}  # {user_id: thread_id}
        
        # Cria assistente Sophia se não existir
        if self.openai_client and not self.assistant_id:
            logger.info(f"[ChatbotPuerperio] Criando assistente Sophia...")
            print(f"[ChatbotPuerperio] Criando assistente Sophia...")
            self.assistant_id = self._criar_assistente_sophia()
            if self.assistant_id:
                logger.info(f"[ChatbotPuerperio] ✅ Assistente criado: {self.assistant_id}")
                print(f"[ChatbotPuerperio] ✅ Assistente criado: {self.assistant_id}")
            else:
                logger.error(f"[ChatbotPuerperio] ❌ Falha ao criar assistente na inicialização")
                print(f"[ChatbotPuerperio] ❌ Falha ao criar assistente na inicialização")
        
        logger.info(f"[ChatbotPuerperio] Inicializado. OpenAI disponivel: {self.openai_client is not None}, Assistant ID: {self.assistant_id is not None}")
        print(f"[ChatbotPuerperio] Inicializado. OpenAI disponivel: {self.openai_client is not None}, Assistant ID: {self.assistant_id is not None}")
    
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

Lembre-se: Você é a Sophia, uma amiga empática que está sempre pronta para ajudar, apoiar e acolher durante esse momento especial do puerpério."""
            
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
    
    def _gerar_resposta_openai(self, pergunta, user_id, historico=None, contexto_pessoal=""):
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
            
            # Aguarda conclusão
            while run.status in ['queued', 'in_progress', 'cancelling']:
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
    
    def humanizar_resposta_local(self, resposta_local, pergunta):
        """Humaniza respostas da base local adicionando contexto empático e conversacional"""
        if not resposta_local:
            return resposta_local
        
        # ⚠️ LIMITE DE TAMANHO: Trunca respostas muito grandes antes de humanizar (máximo 800 caracteres)
        # Isso evita respostas enormes da base local
        TAMANHO_MAXIMO_RESPOSTA_LOCAL = 800
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
            
            # Monta contexto formatado
            contexto_parts = []
            if nomes:
                contexto_parts.append(f"Nomes mencionados anteriormente: {', '.join(set(nomes)[:5])}")
            if lugares:
                contexto_parts.append(f"Lugares mencionados anteriormente: {', '.join(set(lugares)[:5])}")
            if comidas:
                contexto_parts.append(f"Comidas/preferências mencionadas anteriormente: {', '.join(set(comidas)[:5])}")
            
            if contexto_parts:
                contexto = "Dados memorizados da conversa anterior:\n" + "\n".join(contexto_parts)
                logger.info(f"[MEMORIA] Dados carregados para user_id {user_id}: {len(nomes)} nomes, {len(lugares)} lugares, {len(comidas)} comidas")
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
    
    def chat(self, pergunta, user_id="default"):
        """Função principal do chatbot"""
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
        
        # Tenta OpenAI PRIMEIRO (SEMPRE, para TODAS as conversas)
        # Se o assistente não existir, tenta criar agora
        if self.openai_client and not self.assistant_id:
            logger.warning(f"[CHAT] ⚠️ Assistente não encontrado, tentando criar agora...")
            print(f"[CHAT] ⚠️ Assistente não encontrado, tentando criar agora...")
            self.assistant_id = self._criar_assistente_sophia()
            if self.assistant_id:
                logger.info(f"[CHAT] ✅ Assistente criado com sucesso: {self.assistant_id}")
                print(f"[CHAT] ✅ Assistente criado com sucesso: {self.assistant_id}")
            else:
                logger.error(f"[CHAT] ❌ Falha ao criar assistente - usando fallback")
                print(f"[CHAT] ❌ Falha ao criar assistente - usando fallback")
        
        if self.openai_client and self.assistant_id:
            logger.info(f"[CHAT] OpenAI client disponivel (assistant_id: {self.assistant_id[:20]}...), tentando gerar resposta...")
            print(f"[CHAT] OpenAI client disponivel, tentando gerar resposta...")
            try:
                # Prepara contexto para OpenAI
                contexto_pessoal = ""
                
                # Carrega dados memorizados da Sophia (nomes, lugares, comidas)
                dados_memoria = self._obter_dados_memoria(user_id)
                if dados_memoria:
                    contexto_pessoal += dados_memoria + "\n\n"
                
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
                
                # Gera resposta usando OpenAI
                resposta_openai = self._gerar_resposta_openai(
                    pergunta,
                    user_id,
                    historico=historico_para_openai,
                    contexto_pessoal=contexto_pessoal or ""
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
                        "categoria": categoria
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
        else:
            # Log detalhado do por que não está usando OpenAI
            if not self.openai_client:
                logger.warning(f"[CHAT] ⚠️ OpenAI client não disponível - usando fallback")
                print(f"[CHAT] ⚠️ OpenAI client não disponível - usando fallback")
            elif not self.assistant_id:
                logger.warning(f"[CHAT] ⚠️ Assistant ID não disponível (openai_client existe mas assistant_id é None) - usando fallback")
                print(f"[CHAT] ⚠️ Assistant ID não disponível - usando fallback")
        
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
                    "Meu dia esta sendo muito bom! Estou aqui aprendendo e conversando com pessoas incriveis como voce. Cada conversa me ensina algo novo e me deixa feliz em poder ajudar e apoiar. E o seu dia, como esta sendo? Conte-me, aconteceu algo especial hoje?",
                    "Estou muito bem, obrigada por perguntar! Estou aqui, pronta para conversar e ajudar no que voce precisar. E sempre bom quando alguem se importa em saber como estou tambem. E voce, como esta? Como esta se sentindo hoje?",
                    "Meu dia esta sendo tranquilo, aprendendo e conversando com pessoas incriveis como voce. Cada conversa me ensina algo novo e me deixa feliz em poder ajudar. E o seu dia, como esta sendo? Conte-me mais sobre voce!"
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
                    "Oi! Que bom te ver por aqui! Como voce esta se sentindo hoje? Ha algo especifico em que posso te ajudar ou voce so queria conversar? Estou aqui para te ouvir e apoiar no que precisar.",
                    "Ola! Fico feliz que voce esteja aqui! Como voce esta? O que voce gostaria de conversar hoje? Pode me contar sobre como voce esta se sentindo ou sobre o que esta passando?",
                    "Oi! Estou aqui para te ajudar. Conte-me: como voce esta? Ha algo que voce gostaria de compartilhar ou alguma duvida que eu possa ajudar a esclarecer?"
                ]
                resposta_final = random.choice(respostas_saudacao_fallback)
                fonte = "saudacao_humanizada_fallback"
            else:
                # Fallback generico
                resposta_final = "Desculpe, nao consegui processar sua pergunta. Como posso te ajudar hoje?"
                fonte = "fallback"
            
            # Salva dados na memoria (apenas dados, nao conversas)
            self._salvar_dados_memoria(user_id, pergunta, resposta_final)
            
            return {
                "resposta": resposta_final,
                "fonte": fonte,
                "categoria": categoria
            }

# Inicializa instância global do chatbot (após definição da classe)
chatbot = ChatbotPuerperio()
logger.info("[CHATBOT] ✅ Instância global do chatbot criada com sucesso")
print("[CHATBOT] ✅ Instância global do chatbot criada com sucesso")

# Rota raiz - renderiza a página principal
@app.route('/')
def index():
    """Rota principal que renderiza a interface do chatbot"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    pergunta = data.get('pergunta', '')
    user_id = data.get('user_id', 'default')
    
    if not pergunta.strip():
        return jsonify({"erro": "Pergunta não pode estar vazia"}), 400
    
    # Log de diagnóstico
    logger.info(f"[API_CHAT] Recebida pergunta: {pergunta[:50]}...")
    logger.info(f"[API_CHAT] chatbot.openai_client disponível: {chatbot.openai_client is not None}")
    print(f"[API_CHAT] chatbot.openai_client disponível: {chatbot.openai_client is not None}")
    
    resposta = chatbot.chat(pergunta, user_id)
    
    # Log da resposta
    logger.info(f"[API_CHAT] ✅ Resposta gerada - fonte: {resposta.get('fonte', 'desconhecida')}")
    print(f"[API_CHAT] ✅ Resposta gerada - fonte: {resposta.get('fonte', 'desconhecida')}")
    
    return jsonify(resposta)

@app.route('/api/limpar-memoria-ia', methods=['POST'])
@login_required
def limpar_memoria_ia():
    """Limpa TODA a memória da Sophia: conversas, informações pessoais e dados memorizados (nomes, lugares, comidas)"""
    try:
        user_id = session.get('user_id') or current_user.id if current_user.is_authenticated else 'default'
        
        # Limpa apenas da memória em tempo de execução (NÃO limpa do banco, pois não salva mais conversas lá)
        global conversas
        conversas_count = sum(len(conv) for conv in conversas.values())
        conversas.clear()
        
        # Limpa informações pessoais do banco (user_info)
        info_apagadas = 0
        memoria_sophia_apagadas = 0
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Limpa user_info (informações pessoais gerais)
            cursor.execute('DELETE FROM user_info WHERE user_id = ?', (str(user_id),))
            info_apagadas = cursor.rowcount
            
            # Limpa memoria_sophia (dados memorizados: nomes, lugares, comidas)
            cursor.execute('DELETE FROM memoria_sophia WHERE user_id = ?', (str(user_id),))
            memoria_sophia_apagadas = cursor.rowcount
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"[LIMPAR_MEMORIA] ⚠️ Erro ao limpar dados do banco: {e}")
        
        # Limpa threads do OpenAI para o usuário (se existir)
        if chatbot and hasattr(chatbot, 'user_threads') and user_id in chatbot.user_threads:
            del chatbot.user_threads[user_id]
            logger.info(f"[LIMPAR_MEMORIA] Thread OpenAI removida para user_id {user_id}")
        
        # Limpa últimas respostas do controle de repetição
        if chatbot and hasattr(chatbot, 'ultimas_respostas') and user_id in chatbot.ultimas_respostas:
            del chatbot.ultimas_respostas[user_id]
        
        # NÃO limpa conversas do banco (desabilitado conforme solicitado)
        # cursor.execute('DELETE FROM conversas')
        # conversas_apagadas = cursor.rowcount
        
        total_apagado = conversas_count + info_apagadas + memoria_sophia_apagadas
        logger.info(f"[LIMPAR_MEMORIA] ✅ Memória da Sophia limpa para user_id {user_id}: {conversas_count} conversas da memória, {info_apagadas} informações pessoais e {memoria_sophia_apagadas} dados memorizados apagados")
        print(f"[LIMPAR_MEMORIA] ✅ Memória da Sophia limpa: {conversas_count} conversas da memória, {info_apagadas} informações pessoais e {memoria_sophia_apagadas} dados memorizados apagados")
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Memória da Sophia limpa com sucesso! {total_apagado} item(ns) removido(s): {conversas_count} conversas da memória, {info_apagadas} informações pessoais e {memoria_sophia_apagadas} dados memorizados (nomes, lugares, comidas).",
            "conversas_apagadas": conversas_count,
            "info_apagadas": info_apagadas,
            "memoria_sophia_apagadas": memoria_sophia_apagadas,
            "total_apagado": total_apagado
        }), 200
    except Exception as e:
        logger.error(f"[LIMPAR_MEMORIA] ❌ Erro ao limpar memória: {e}", exc_info=True)
        return jsonify({
            "sucesso": False,
            "erro": f"Erro ao limpar memória: {str(e)}"
        }), 500

@app.route('/api/historico/<user_id>', methods=['GET', 'DELETE'])
def api_historico(user_id):
    """Retorna ou limpa histórico de conversas do usuário"""
    if request.method == 'DELETE':
        # Limpa apenas da memória (NÃO limpa do banco, pois não salva mais lá)
        try:
            # Limpa da memória
            if user_id in conversas:
                conversas[user_id] = []
            
            # NÃO limpa do banco de dados (desabilitado conforme solicitado)
            # conn = sqlite3.connect(DB_PATH)
            # cursor = conn.cursor()
            # cursor.execute('DELETE FROM conversas WHERE user_id = ?', (user_id,))
            # conn.commit()
            # conn.close()
            
            logger.info(f"[MEMORIA] ✅ Histórico limpo da memória para user_id: {user_id}")
            return jsonify({"success": True, "message": "Histórico limpo com sucesso"})
        except Exception as e:
            logger.error(f"[MEMORIA] ❌ Erro ao limpar histórico: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # GET: Retorna histórico apenas da memória (NÃO carrega do banco)
    historico = conversas.get(user_id, [])
    
    # NÃO carrega do banco de dados (desabilitado conforme solicitado)
    # if not historico:
    #     historico = carregar_historico_db(user_id)
    #     if historico:
    #         conversas[user_id] = historico  # Atualiza cache
    
    return jsonify(historico)

@app.route('/api/categorias')
def api_categorias():
    categorias = list(base_conhecimento.keys())
    return jsonify(categorias)

@app.route('/api/alertas')
def api_alertas():
    return jsonify(alertas)

@app.route('/api/telefones')
def api_telefones():
    return jsonify(telefones_uteis)

@app.route('/api/guias')
def api_guias():
    return jsonify(guias_praticos)

@app.route('/api/guias/<guia_id>')
def api_guia_especifico(guia_id):
    guia = guias_praticos.get(guia_id)
    if guia:
        return jsonify(guia)
    return jsonify({"erro": "Guia não encontrado"}), 404

@app.route('/api/cuidados/gestacao')
def api_cuidados_gestacao():
    return jsonify(cuidados_gestacao)

@app.route('/api/cuidados/gestacao/<trimestre>')
def api_trimestre_especifico(trimestre):
    trimestre_data = cuidados_gestacao.get(trimestre)
    if trimestre_data:
        return jsonify(trimestre_data)
    return jsonify({"erro": "Trimestre não encontrado"}), 404

@app.route('/api/cuidados/puerperio')
def api_cuidados_puerperio():
    return jsonify(cuidados_pos_parto)

@app.route('/api/cuidados/puerperio/<periodo>')
def api_periodo_especifico(periodo):
    periodo_data = cuidados_pos_parto.get(periodo)
    if periodo_data:
        return jsonify(periodo_data)
    return jsonify({"erro": "Período não encontrado"}), 404

@app.route('/api/vacinas/mae')
def api_vacinas_mae():
    return jsonify(vacinas_mae)

@app.route('/api/vacinas/bebe')
def api_vacinas_bebe():
    return jsonify(vacinas_bebe)

# Auth routes
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    logger.info(f"[REGISTER] Tentativa de cadastro recebida: {data}")
    print(f"[REGISTER] Dados recebidos: {data}")
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    baby_name = data.get('baby_name', '').strip()
    
    logger.info(f"[REGISTER] Campos processados - name: {name[:3]}..., email: {email}, password length: {len(password) if password else 0}")
    print(f"[REGISTER] Campos processados - name: {name}, email: {email}, password length: {len(password) if password else 0}")
    
    if not name or not email or not password:
        erro_msg = "Todos os campos obrigatórios devem ser preenchidos"
        logger.warning(f"[REGISTER] {erro_msg} - name: {bool(name)}, email: {bool(email)}, password: {bool(password)}")
        print(f"[REGISTER] ❌ {erro_msg}")
        return jsonify({"erro": erro_msg}), 400
    
    if len(password) < 6:
        erro_msg = "A senha deve ter no mínimo 6 caracteres"
        logger.warning(f"[REGISTER] {erro_msg} - password length: {len(password)}")
        print(f"[REGISTER] ❌ {erro_msg}")
        return jsonify({"erro": erro_msg}), 400
    
    # Validação básica de email
    if '@' not in email or '.' not in email.split('@')[1]:
        erro_msg = "Email inválido"
        logger.warning(f"[REGISTER] {erro_msg} - email: {email}")
        print(f"[REGISTER] ❌ {erro_msg}")
        return jsonify({"erro": erro_msg}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifica se email já existe
    cursor.execute('SELECT id, email_verified FROM users WHERE email = ?', (email,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        if existing[1] == 1:
            erro_msg = "Este email já está cadastrado e verificado"
            logger.warning(f"[REGISTER] {erro_msg} - email: {email}")
            print(f"[REGISTER] ❌ {erro_msg}")
            return jsonify({"erro": erro_msg}), 400
        else:
            erro_msg = "Este email já está cadastrado. Verifique seu email ou use 'Esqueci minha senha'"
            logger.warning(f"[REGISTER] {erro_msg} - email: {email}")
            print(f"[REGISTER] ❌ {erro_msg}")
            return jsonify({"erro": erro_msg}), 400
    
    # Hash da senha - salva como string base64 para preservar bytes
    password_hash_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password_hash = base64.b64encode(password_hash_bytes).decode('utf-8')
    
    # Gera token de verificação
    verification_token = generate_token()
    
    # Verifica se email está configurado (modo desenvolvimento vs produção)
    email_configurado = bool(app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'))
    
    # Em desenvolvimento (sem email configurado), marca como verificado automaticamente
    email_verified_value = 1 if not email_configurado else 0
    
    # Insere usuário
    try:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, baby_name, email_verified, email_verification_token)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, password_hash, baby_name if baby_name else None, email_verified_value, verification_token))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        # Envia email de verificação apenas se estiver configurado
        mensagem = ""
        verification_sent = False
        
        if email_configurado:
            try:
                logger.info(f"[REGISTER] Enviando email de verificação para: {email}")
                print(f"[REGISTER] Tentando enviar email de verificação para: {email}")
                
                # Chama a função e verifica se realmente foi enviado
                email_sent = send_verification_email(email, name, verification_token)
                
                if email_sent:
                    mensagem = "Cadastro realizado! Verifique seu email para ativar sua conta. 💕"
                    verification_sent = True
                    logger.info(f"[REGISTER] ✅ Email de verificação enviado com sucesso para: {email}")
                    print(f"[REGISTER] ✅ Email de verificação enviado com sucesso para: {email}")
                else:
                    # Se retornou False, houve erro silencioso
                    raise Exception("send_email retornou False - verifique os logs acima")
                    
            except Exception as e:
                logger.error(f"[REGISTER] ❌ Erro ao enviar email de verificação: {e}", exc_info=True)
                print(f"[REGISTER] ❌ Erro ao enviar email de verificação: {e}")
                print(f"[REGISTER] Verifique os logs acima para detalhes do erro")
                import traceback
                traceback.print_exc()
                # Se falhar ao enviar, marca como verificado para não bloquear o usuário
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET email_verified = 1 WHERE id = ?', (user_id,))
                conn.commit()
                conn.close()
                mensagem = "Cadastro realizado! (O email de verificação não pôde ser enviado, mas sua conta foi ativada automaticamente. Você já pode fazer login!) 💕"
                verification_sent = False
        else:
            # Modo desenvolvimento: conta já está verificada
            logger.warning(f"[REGISTER] ⚠️ EMAIL NÃO CONFIGURADO - Conta marcada como verificada automaticamente (modo desenvolvimento)")
            logger.warning(f"[REGISTER] Para ativar envio de emails, configure MAIL_USERNAME e MAIL_PASSWORD no arquivo .env")
            print(f"[REGISTER] ⚠️ EMAIL NÃO CONFIGURADO - conta marcada como verificada automaticamente (modo desenvolvimento)")
            print(f"[REGISTER] Para ativar envio de emails, configure MAIL_USERNAME e MAIL_PASSWORD no arquivo .env")
            mensagem = "Cadastro realizado com sucesso! Você já pode fazer login. 💕"
            verification_sent = False
        
        return jsonify({
            "sucesso": True, 
            "mensagem": mensagem,
            "user_id": user_id,
            "verification_sent": verification_sent,
            "email_verified": email_verified_value == 1
        }), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"erro": "Este email já está cadastrado"}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"erro": "Dados de login não fornecidos"}), 400
        
        # Normaliza email e senha (remove espaços, converte email para lowercase)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()  # Remove espaços da senha também
        remember_me = data.get('remember_me', False)  # Se deve lembrar o usuário

        if not email or not password:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        # Log detalhado para debug (inclui informações do dispositivo)
        user_agent = request.headers.get('User-Agent', 'Desconhecido')
        client_ip = request.remote_addr
        logger.info(f"[LOGIN] Tentativa de login - Email: {email}, Password length: {len(password)}, IP: {client_ip}, User-Agent: {user_agent[:100]}")
        print(f"[LOGIN] Tentativa de login - Email: {email}, Password length: {len(password)}, IP: {client_ip}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Seleciona campos específicos para garantir ordem correta
        # Email já foi normalizado (lowercase e trim) no Python acima
        cursor.execute('''
            SELECT id, name, email, password_hash, baby_name, email_verified
            FROM users
            WHERE email = ?
        ''', (email,))
        user_data = cursor.fetchone()
        conn.close()

        if not user_data:
            logger.warning(f"[LOGIN] Email não encontrado: {email} (IP: {client_ip})")
            print(f"[LOGIN] Email não encontrado: {email}")
            return jsonify({"erro": "Email ou senha incorretos"}), 401

        # Extrai dados (ordem: id, name, email, password_hash, baby_name, email_verified)
        user_id = user_data[0]
        user_name = user_data[1]
        user_email = user_data[2]
        stored_hash_str = user_data[3]  # password_hash
        baby_name = user_data[4]
        email_verified = user_data[5] if len(user_data) > 5 else 1  # email_verified (default 1 para compatibilidade)

        print(f"[LOGIN] Usuário encontrado: {user_email}, email_verified: {email_verified}")

        if not stored_hash_str:
            print(f"[LOGIN] Hash de senha não encontrado para usuário: {email}")
            return jsonify({"erro": "Conta com problema. Use 'Esqueci minha senha' para corrigir."}), 401

        stored_hash = None
        hash_format = "desconhecido"

        # Tenta diferentes formatos de hash
        try:
            # Formato novo: base64 (mais comum em registros recentes)
            try:
                stored_hash = base64.b64decode(stored_hash_str.encode('utf-8'))
                hash_format = "base64"
                print(f"[LOGIN DEBUG] Hash decodificado como base64")
            except Exception:
                # Se não for base64 válido, tenta outros formatos
                # Formato antigo: string bcrypt direta
                if isinstance(stored_hash_str, str) and stored_hash_str.startswith('$2'):
                    stored_hash = stored_hash_str.encode('utf-8')
                    hash_format = "string bcrypt"
                    print(f"[LOGIN DEBUG] Hash processado como string bcrypt")
                elif isinstance(stored_hash_str, bytes):
                    stored_hash = stored_hash_str
                    hash_format = "bytes diretos"
                    print(f"[LOGIN DEBUG] Hash processado como bytes diretos")
                else:
                    # Hash corrompido ou formato desconhecido
                    print(f"[LOGIN DEBUG] Hash em formato desconhecido. Tipo: {type(stored_hash_str)}, Início: {str(stored_hash_str)[:50] if stored_hash_str else 'N/A'}...")
                    return jsonify({"erro": "Conta com problema. Use 'Esqueci minha senha' para corrigir."}), 401
        except Exception as e:
            print(f"[LOGIN DEBUG] Erro ao processar hash: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"erro": "Erro ao verificar senha. Use 'Esqueci minha senha'."}), 401

        # Verifica senha
        password_correct = False
        if stored_hash:
            try:
                # Garante que a senha está em bytes
                password_bytes = password.encode('utf-8')
                password_correct = bcrypt.checkpw(password_bytes, stored_hash)
                logger.debug(f"[LOGIN DEBUG] Verificação de senha: {'CORRETA' if password_correct else 'INCORRETA'}")
                print(f"[LOGIN DEBUG] Hash formato: {hash_format}")
                print(f"[LOGIN DEBUG] Hash length: {len(stored_hash)} bytes")
                print(f"[LOGIN DEBUG] Password length: {len(password_bytes)} bytes")
            except Exception as e:
                print(f"[LOGIN DEBUG] Erro ao verificar senha: {e}")
                import traceback
                traceback.print_exc()
                password_correct = False
        else:
            print(f"[LOGIN DEBUG] stored_hash é None, não é possível verificar senha")
    except Exception as e:
        print(f"[LOGIN] Erro inesperado no login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"erro": "Erro interno ao processar login. Tente novamente."}), 500
    
    if password_correct:
        # Log para debug
        logger.info(f"[LOGIN] Senha correta para: {email}, email_verified: {email_verified}")
        print(f"[LOGIN] Tentativa de login: {email}, email_verified: {email_verified}")
        
        # Verifica se email foi verificado
        # PERMITE login para contas antigas (criadas antes da verificação obrigatória)
        # Mas ainda mostra aviso se não verificado
        if email_verified == 0:
            logger.warning(f"[LOGIN] Tentativa de login com email não verificado: {email}")
            print(f"[LOGIN] Tentativa de login com email não verificado: {email}")
            # Para desenvolvimento: permite login mas avisa
            # Em produção, pode ser descomentado para bloquear:
            # return jsonify({
            #     "erro": "Email não verificado",
            #     "mensagem": f"Por favor, verifique seu email ({email}) antes de fazer login. Procure por um email da Sophia com o assunto 'Verifique seu email'. Se não recebeu, verifique a pasta de spam ou clique em 'Esqueci minha senha'.",
            #     "pode_login": False,
            #     "email": email
            # }), 403
            print(f"[LOGIN] AVISO: Email não verificado, mas permitindo login (modo desenvolvimento)")
        
        # Cria usuário e faz login
        try:
            user = User(user_id, user_name, user_email, baby_name)
            # Usa remember_me do frontend para criar sessão persistente
            result = login_user(user, remember=remember_me)
            logger.info(f"[LOGIN] Usuário logado com sucesso: {user_name} (ID: {user_id}), Sessão criada: {result}, Remember me: {remember_me}, IP: {client_ip}")
            print(f"[LOGIN] Usuário logado: {user_name}, ID: {user_id}, Sessão criada: {result}, Remember me: {remember_me}")
            
            # Log de cookies/sessão para debug em mobile
            session_id = session.get('_id', 'N/A')
            logger.debug(f"[LOGIN] Session ID: {session_id}, Cookies enviados: {request.cookies}")
        except Exception as e:
            logger.error(f"[LOGIN] Erro ao fazer login_user: {e}", exc_info=True)
            print(f"[LOGIN] Erro ao fazer login_user: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"erro": "Erro interno ao criar sessão"}), 500
        
        return jsonify({
            "sucesso": True, 
            "mensagem": "Login realizado com sucesso! Bem-vinda de volta 💕",
            "user": {
                "id": user_id,
                "name": user_name,
                "email": user_email,
                "baby_name": baby_name
            }
        })
    else:
        logger.warning(f"[LOGIN] Senha incorreta para: {email} (IP: {client_ip})")
        print(f"[LOGIN] Senha incorreta para: {email}")
        print(f"[LOGIN DEBUG] stored_hash disponível: {stored_hash is not None}")
        print(f"[LOGIN DEBUG] hash_format usado: {hash_format}")
        if stored_hash_str:
            print(f"[LOGIN DEBUG] Hash string (primeiros 50 chars): {stored_hash_str[:50]}...")
        print(f"[LOGIN DEBUG] Password recebido (primeiros 10 chars): {password[:10]}... (length: {len(password)})")
        return jsonify({"erro": "Email ou senha incorretos"}), 401

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """Solicita recuperação de senha - envia email com token"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if not user:
        # Por segurança, não revela se email existe ou não
        conn.close()
        return jsonify({
            "sucesso": True,
            "mensagem": "Se o email existir, um link de recuperação foi enviado."
        }), 200
    
    user_id, name = user
    
    # Gera token de recuperação
    reset_token = generate_token()
    expires = datetime.now() + timedelta(hours=1)
    
    # Salva token no banco
    cursor.execute('''
        UPDATE users 
        SET reset_password_token = ?, reset_password_expires = ?
        WHERE id = ?
    ''', (reset_token, expires.isoformat(), user_id))
    
    conn.commit()
    conn.close()
    
    # Envia email
    try:
        send_password_reset_email(email, name, reset_token)
        return jsonify({
            "sucesso": True,
            "mensagem": "Email de recuperação enviado! Verifique sua caixa de entrada. 💕"
        }), 200
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return jsonify({
            "sucesso": True,
            "mensagem": "Token gerado. Em desenvolvimento, verifique os logs do servidor."
        }), 200

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """Redefine a senha usando token"""
    data = request.get_json()
    token = data.get('token', '').strip()
    new_password = data.get('password', '')
    
    if not token or not new_password:
        return jsonify({"erro": "Token e nova senha são obrigatórios"}), 400
    
    if len(new_password) < 6:
        return jsonify({"erro": "A senha deve ter no mínimo 6 caracteres"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, email, reset_password_expires 
        FROM users 
        WHERE reset_password_token = ?
    ''', (token,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({"erro": "Token inválido ou expirado"}), 400
    
    user_id, email, expires_str = user
    
    # Verifica se token não expirou
    if expires_str:
        try:
            expires = datetime.fromisoformat(expires_str)
            if datetime.now() > expires:
                conn.close()
                return jsonify({"erro": "Token expirado. Solicite uma nova recuperação."}), 400
        except:
            pass
    
    # Gera novo hash com formato correto
    password_hash_bytes = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    password_hash = base64.b64encode(password_hash_bytes).decode('utf-8')
    
    # Atualiza a senha e limpa token
    cursor.execute('''
        UPDATE users 
        SET password_hash = ?, reset_password_token = NULL, reset_password_expires = NULL, email_verified = 1
        WHERE id = ?
    ''', (password_hash, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "sucesso": True,
        "mensagem": "Senha redefinida com sucesso! Agora você pode fazer login. 💕"
    }), 200

@app.route('/api/resend-verification', methods=['POST'])
def api_resend_verification():
    """Reenvia email de verificação"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, email_verified, email_verification_token 
        FROM users 
        WHERE email = ?
    ''', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({"erro": "Email não encontrado"}), 404
    
    user_id, name, email_verified, token = user
    
    if email_verified == 1:
        return jsonify({
            "sucesso": True,
            "mensagem": "Seu email já está verificado! Você pode fazer login normalmente."
        }), 200
    
    # Gera novo token se não existir
    if not token:
        token = generate_token()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET email_verification_token = ?
            WHERE id = ?
        ''', (token, user_id))
        conn.commit()
        conn.close()
    
    # Verifica se email está configurado
    email_configurado = bool(app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'))
    
    if not email_configurado:
        # Se email não estiver configurado, marca como verificado automaticamente
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET email_verified = 1 WHERE email = ?', (email,))
        conn.commit()
        conn.close()
        return jsonify({
            "sucesso": True,
            "mensagem": f"Email não configurado no servidor. Sua conta foi ativada automaticamente. Você pode fazer login agora! 💕"
        }), 200
    
    # Reenvia email
    try:
        logger.info(f"[RESEND] Tentando reenviar email de verificação para: {email}")
        email_sent = send_verification_email(email, name, token)
        
        if email_sent:
            logger.info(f"[RESEND] ✅ Email de verificação reenviado com sucesso para: {email}")
            return jsonify({
                "sucesso": True,
                "mensagem": f"Email de verificação reenviado para {email}! Verifique sua caixa de entrada e também a pasta de spam/lixo eletrônico. 💕"
            }), 200
        else:
            raise Exception("send_email retornou False - verifique os logs acima")
            
    except Exception as e:
        logger.error(f"[RESEND] ❌ Erro ao reenviar email: {e}", exc_info=True)
        print(f"[RESEND] ❌ Erro ao reenviar email: {e}")
        print(f"[RESEND] Verifique os logs acima para detalhes do erro")
        import traceback
        traceback.print_exc()
        return jsonify({
            "sucesso": False,
            "erro": f"Não foi possível reenviar o email. Erro: {str(e)}. Verifique se o email está configurado corretamente no servidor."
        }), 500

@app.route('/api/verify-email', methods=['GET'])
def api_verify_email():
    """Verifica email através do token"""
    token = request.args.get('token', '')
    
    if not token:
        logger.warning("[VERIFY] Tentativa de verificação sem token")
        # Retorna página de erro amigável
        base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
        return render_template('email_verified.html',
                             base_url=base_url,
                             error=True,
                             message="Token não fornecido"), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, email, name 
        FROM users 
        WHERE email_verification_token = ?
    ''', (token,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        logger.warning(f"[VERIFY] Token inválido: {token[:20]}...")
        # Retorna página de erro amigável
        base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
        return render_template('email_verified.html',
                             base_url=base_url,
                             error=True,
                             message="Token inválido ou expirado"), 400
    
    user_id, email, name = user
    
    # Verifica se já estava verificado
    cursor.execute('SELECT email_verified FROM users WHERE id = ?', (user_id,))
    already_verified_result = cursor.fetchone()
    already_verified = already_verified_result[0] if already_verified_result else 0
    
    # Marca email como verificado (PERMANENTEMENTE no banco de dados)
    cursor.execute('''
        UPDATE users 
        SET email_verified = 1, email_verification_token = NULL
        WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    
    # Verifica se foi salvo corretamente
    cursor.execute('SELECT email_verified FROM users WHERE id = ?', (user_id,))
    verification_status = cursor.fetchone()[0]
    
    conn.close()
    
    if verification_status == 1:
        logger.info(f"[VERIFY] ✅ Email verificado e SALVO PERMANENTEMENTE no banco: {email} (ID: {user_id})")
        logger.info(f"[VERIFY] ✅ Status de verificação persistido: email_verified = {verification_status}")
    else:
        logger.error(f"[VERIFY] ❌ ERRO: Email não foi salvo como verificado! {email} (ID: {user_id})")
    
    # Retorna página de confirmação com o mesmo estilo do menu inicial
    base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
    return render_template('email_verified.html',
                         base_url=base_url,
                         error=False,
                         email=email,
                         name=name)

@app.route('/api/auto-verify', methods=['POST'])
def api_auto_verify():
    """Marca automaticamente a conta como verificada se o email não estiver configurado (modo desenvolvimento)"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400
    
    # Verifica se email está configurado
    email_configurado = bool(app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'))
    
    if email_configurado:
        return jsonify({
            "erro": "Email está configurado. Use a verificação normal por email."
        }), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, email_verified FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({"erro": "Email não encontrado"}), 404
    
    user_id, email_verified = user
    
    if email_verified == 1:
        conn.close()
        return jsonify({
            "sucesso": True,
            "mensagem": "Conta já está verificada!"
        }), 200
    
    # Marca como verificado
    cursor.execute('UPDATE users SET email_verified = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({
        "sucesso": True,
        "mensagem": "Conta marcada como verificada! Agora você pode fazer login. 💕"
    }), 200

@app.route('/api/delete-user', methods=['POST'])
def api_delete_user():
    """Deleta um usuário do banco de dados (para permitir novo cadastro)"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({"sucesso": True, "mensagem": "Usuário não encontrado (pode fazer novo cadastro)"}), 200
    
    user_id = user[0]
    
    # Deleta vacinas associadas
    cursor.execute('DELETE FROM vacinas_tomadas WHERE user_id = ?', (user_id,))
    # Deleta usuário
    cursor.execute('DELETE FROM users WHERE email = ?', (email,))
    
    conn.commit()
    conn.close()
    
    return jsonify({"sucesso": True, "mensagem": "Conta deletada com sucesso! Agora você pode fazer um novo cadastro. 💕"}), 200

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Realiza logout do usuário"""
    try:
        logout_user()
        session.clear()  # Limpa a sessão completamente
        print(f"[LOGOUT] Logout realizado com sucesso")
    except Exception as e:
        print(f"[LOGOUT] Erro (mas continua): {e}")
        session.clear()  # Limpa mesmo com erro
    return jsonify({"sucesso": True, "mensagem": "Logout realizado com sucesso"})

@app.route('/api/user', methods=['GET'])
def api_user():
    """Verifica se o usuário está logado"""
    try:
        if current_user.is_authenticated:
            return jsonify({
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "baby_name": current_user.baby_name
            }), 200
        else:
            return jsonify({"erro": "Não autenticado"}), 401
    except Exception as e:
        print(f"[AUTH] Erro ao verificar usuário: {e}")
        return jsonify({"erro": "Não autenticado"}), 401

@app.route('/api/verificacao', methods=['POST'])
def api_verificacao():
    """Verificação: verifica se o email existe e se o hash está correto"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, password_hash FROM users WHERE email = ?', (email,))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        return jsonify({
            "encontrado": False,
            "mensagem": "Email não encontrado no banco de dados. Você pode fazer um novo cadastro."
        })
    
    stored_hash_str = user_data[3]
    hash_valido = False
    formato_hash = "desconhecido"
    
    # Verifica o formato do hash
    try:
        # Tenta decodificar como base64
        base64.b64decode(stored_hash_str.encode('utf-8'))
        formato_hash = "base64 (correto)"
        hash_valido = True
    except:
        if isinstance(stored_hash_str, bytes):
            formato_hash = "bytes"
            hash_valido = True
        elif stored_hash_str.startswith('$2'):
            formato_hash = "string bcrypt (pode estar corrompido)"
        else:
            formato_hash = "corrompido ou inválido"
    
    return jsonify({
        "encontrado": True,
        "nome": user_data[1],
        "email": user_data[2],
        "formato_hash": formato_hash,
        "hash_valido": hash_valido,
        "mensagem": "Usuário encontrado. " + (
            "Hash parece estar correto." if hash_valido 
            else "Hash pode estar corrompido. Use 'Redefinir Senha' ou delete a conta."
        )
    })

@app.route('/api/vacinas/status', methods=['GET'])
@login_required
def api_vacinas_status():
    """Retorna o status das vacinas tomadas pelo usuário"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT tipo, vacina_nome, data_tomada FROM vacinas_tomadas WHERE user_id = ?', (current_user.id,))
    vacinas = cursor.fetchall()
    conn.close()
    
    status = {}
    for vacina in vacinas:
        tipo = vacina[0]
        if tipo not in status:
            status[tipo] = []
        status[tipo].append({
            "nome": vacina[1],
            "data": vacina[2]
        })
    
    return jsonify(status)

@app.route('/api/vacinas/marcar', methods=['POST'])
@login_required
def api_vacinas_marcar():
    """Marca uma vacina como tomada"""
    data = request.get_json()
    tipo = data.get('tipo', '').strip()  # 'mae' ou 'bebe'
    vacina_nome = data.get('vacina_nome', '').strip()
    
    if not tipo or not vacina_nome:
        return jsonify({"erro": "Tipo e nome da vacina são obrigatórios"}), 400
    
    if tipo not in ['mae', 'bebe']:
        return jsonify({"erro": "Tipo deve ser 'mae' ou 'bebe'"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifica se já foi marcada
    cursor.execute('SELECT id FROM vacinas_tomadas WHERE user_id = ? AND tipo = ? AND vacina_nome = ?', 
                   (current_user.id, tipo, vacina_nome))
    if cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Esta vacina já foi marcada"}), 400
    
    # Busca informações do usuário (incluindo nome do bebê)
    cursor.execute('SELECT name, baby_name FROM users WHERE id = ?', (current_user.id,))
    user_data = cursor.fetchone()
    user_name = user_data[0] if user_data else current_user.name
    baby_name = user_data[1] if user_data and user_data[1] else None
    
    # Insere a vacina
    cursor.execute('INSERT INTO vacinas_tomadas (user_id, tipo, vacina_nome) VALUES (?, ?, ?)',
                   (current_user.id, tipo, vacina_nome))
    conn.commit()
    vacina_id = cursor.lastrowid
    conn.close()
    
    # Mensagem personalizada
    if tipo == 'bebe' and baby_name:
        mensagem = f"Vacina marcada com sucesso! Parabéns, {baby_name}! E parabéns para você também, {user_name}! 💉✨🎉"
    elif tipo == 'bebe':
        mensagem = f"Vacina marcada com sucesso! Parabéns para você e seu bebê! 💉✨🎉"
    else:
        mensagem = f"Vacina marcada com sucesso! Parabéns, {user_name}! 💉✨"
    
    return jsonify({
        "sucesso": True, 
        "mensagem": mensagem,
        "vacina_id": vacina_id,
        "tipo": tipo,
        "baby_name": baby_name,
        "user_name": user_name
    }), 201

@app.route('/api/vacinas/desmarcar', methods=['POST'])
@login_required
def api_vacinas_desmarcar():
    """Remove uma vacina das vacinas tomadas"""
    data = request.get_json()
    tipo = data.get('tipo', '').strip()
    vacina_nome = data.get('vacina_nome', '').strip()
    
    if not tipo or not vacina_nome:
        return jsonify({"erro": "Tipo e nome da vacina são obrigatórios"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vacinas_tomadas WHERE user_id = ? AND tipo = ? AND vacina_nome = ?',
                   (current_user.id, tipo, vacina_nome))
    conn.commit()
    conn.close()
    
    return jsonify({"sucesso": True, "mensagem": "Vacina removida"})

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
    print("OpenAI disponível:", "Sim" if openai_client else "Não")
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
    
    # Configura Flask para shutdown mais limpo
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False, threaded=True)

