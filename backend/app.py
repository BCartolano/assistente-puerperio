import os
import sys
import time
import json
import random
import difflib
import sqlite3
import bcrypt
import base64
import secrets
import string
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, session, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from dotenv import load_dotenv
# Verifica se google-generativeai está disponível
GEMINI_AVAILABLE = False
genai = None
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print(f"[GEMINI] ✅ Biblioteca google-generativeai importada com sucesso!")
    print(f"[GEMINI] ✅ Versão: {genai.__version__ if hasattr(genai, '__version__') else 'N/A'}")
    print(f"[GEMINI] ✅ Python executando: {sys.executable}")
    print(f"[GEMINI] ✅ Caminho Python: {sys.path[:3]}")
except ImportError as e:
    GEMINI_AVAILABLE = False
    genai = None
    print(f"[GEMINI] ❌ ERRO ao importar google-generativeai: {e}")
    print(f"[GEMINI] ❌ Python executando: {sys.executable}")
    print(f"[GEMINI] ❌ Execute: pip install google-generativeai")
    print(f"[GEMINI] ❌ Verifique se está no ambiente virtual correto!")
except Exception as e:
    GEMINI_AVAILABLE = False
    genai = None
    print(f"[GEMINI] ❌ ERRO inesperado ao importar google-generativeai: {e}")
    import traceback
    traceback.print_exc()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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
# Carrega GEMINI_API_KEY com múltiplas tentativas
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Tenta recarregar se não encontrou
    logger.warning("[GEMINI] ⚠️ GEMINI_API_KEY não encontrada na primeira tentativa, recarregando .env...")
    print("[GEMINI] ⚠️ GEMINI_API_KEY não encontrada na primeira tentativa, recarregando .env...")
    for env_path in env_paths:
        if os.path.exists(env_path):
            logger.info(f"[GEMINI] Recarregando .env de: {env_path}")
            print(f"[GEMINI] Recarregando .env de: {env_path}")
            load_dotenv(env_path, override=True)
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            if GEMINI_API_KEY:
                logger.info(f"[GEMINI] ✅ GEMINI_API_KEY carregada após recarregar (length: {len(GEMINI_API_KEY)})")
                print(f"[GEMINI] ✅ GEMINI_API_KEY carregada após recarregar (length: {len(GEMINI_API_KEY)})")
                break

if GEMINI_API_KEY:
    logger.info(f"[GEMINI] ✅ GEMINI_API_KEY encontrada (length: {len(GEMINI_API_KEY)})")
    print(f"[GEMINI] ✅ GEMINI_API_KEY encontrada (length: {len(GEMINI_API_KEY)})")
    print(f"[GEMINI] Primeiros 10 chars: {GEMINI_API_KEY[:10]}...")
else:
    logger.error("[GEMINI] ❌❌❌ GEMINI_API_KEY NÃO encontrada após todas as tentativas!")
    print("[GEMINI] ❌❌❌ GEMINI_API_KEY NÃO encontrada após todas as tentativas!")
    print("[GEMINI] Verificando variáveis de ambiente...")
    print(f"[GEMINI] GEMINI_API_KEY from os.getenv: {repr(os.getenv('GEMINI_API_KEY'))}")

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

# Inicializa cliente Gemini se a chave estiver disponível
gemini_client = None
logger.info(f"[GEMINI] 🔍 Verificando inicialização... GEMINI_AVAILABLE: {GEMINI_AVAILABLE}, GEMINI_API_KEY presente: {bool(GEMINI_API_KEY)}")
print(f"[GEMINI] 🔍 Verificando inicialização... GEMINI_AVAILABLE: {GEMINI_AVAILABLE}, GEMINI_API_KEY presente: {bool(GEMINI_API_KEY)}")

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    logger.info(f"[GEMINI] ✅ Condições atendidas - GEMINI_AVAILABLE: {GEMINI_AVAILABLE}, GEMINI_API_KEY presente: {bool(GEMINI_API_KEY)}")
    print(f"[GEMINI] ✅ Condições atendidas - GEMINI_AVAILABLE: {GEMINI_AVAILABLE}, GEMINI_API_KEY presente: {bool(GEMINI_API_KEY)}")
    
    # ISOLAR: Configuração da API
    configure_success = False
    try:
        logger.info(f"[GEMINI] 🔍 [PASSO 1] Configurando Gemini com API key (length: {len(GEMINI_API_KEY)})")
        print(f"[GEMINI] 🔍 [PASSO 1] Configurando Gemini com API key (length: {len(GEMINI_API_KEY)})")
        genai.configure(api_key=GEMINI_API_KEY)
        configure_success = True
        logger.info("[GEMINI] ✅ [PASSO 1] genai.configure() executado com sucesso")
        print("[GEMINI] ✅ [PASSO 1] genai.configure() executado com sucesso")
    except Exception as e:
        logger.error(f"[GEMINI] ❌ [PASSO 1] ERRO ao configurar API: {e}", exc_info=True)
        print(f"[GEMINI] ❌ [PASSO 1] ERRO ao configurar API: {e}")
        import traceback
        traceback.print_exc()
        configure_success = False
    
    # ISOLAR: Criação do objeto GenerativeModel (LINHA CRÍTICA)
    if configure_success:  # Só tenta criar se configure() funcionou
        try:
            logger.info("[GEMINI] 🔍 [PASSO 2] Criando GenerativeModel('gemini-2.0-flash')...")
            print("[GEMINI] 🔍 [PASSO 2] Criando GenerativeModel('gemini-2.0-flash')...")
            print(f"[GEMINI] [PASSO 2] genai disponível: {genai is not None}")
            print(f"[GEMINI] [PASSO 2] GEMINI_API_KEY disponível: {bool(GEMINI_API_KEY)}")
            
            # ESTA É A LINHA QUE PODE ESTAR FALHANDO
            gemini_client = genai.GenerativeModel('gemini-2.0-flash')
            
            logger.info("[GEMINI] ✅ [PASSO 2] GenerativeModel criado com sucesso!")
            print("[GEMINI] ✅ [PASSO 2] GenerativeModel criado com sucesso!")
            print(f"[GEMINI] ✅ [PASSO 2] gemini_client type: {type(gemini_client)}")
            print(f"[GEMINI] ✅ [PASSO 2] gemini_client is None: {gemini_client is None}")
            print(f"[GEMINI] ✅ [PASSO 2] gemini_client object: {gemini_client}")
            
            # Verificação final
            if gemini_client is None:
                logger.error("[GEMINI] ❌❌❌ ERRO CRÍTICO: GenerativeModel retornou None!")
                print("[GEMINI] ❌❌❌ ERRO CRÍTICO: GenerativeModel retornou None!")
            else:
                logger.info("[GEMINI] ✅✅✅ [PASSO 2] Cliente Gemini inicializado com SUCESSO!")
                print("[GEMINI] ✅✅✅ [PASSO 2] Cliente Gemini inicializado com SUCESSO!")
                
        except Exception as e:
            logger.error(f"[GEMINI] ❌ [PASSO 2] ERRO AO INSTANCIAR O CLIENTE GEMINI: {e}", exc_info=True)
            print(f"[GEMINI] ❌ [PASSO 2] ERRO AO INSTANCIAR O CLIENTE GEMINI: {e}")
            import traceback
            traceback.print_exc()
            gemini_client = None
            logger.error(f"[GEMINI] ❌ [PASSO 2] gemini_client definido como None devido ao erro")
            print(f"[GEMINI] ❌ [PASSO 2] gemini_client definido como None devido ao erro")
            print(f"[GEMINI] ❌ [PASSO 2] Tipo do erro: {type(e).__name__}")
            print(f"[GEMINI] ❌ [PASSO 2] Mensagem completa: {str(e)}")
else:
    if not GEMINI_AVAILABLE:
        logger.warning("[GEMINI] ⚠️ Biblioteca google-generativeai não instalada - execute: pip install google-generativeai")
        print("[GEMINI] ⚠️ Biblioteca não instalada - execute: pip install google-generativeai")
    elif not GEMINI_API_KEY:
        logger.warning("[GEMINI] ⚠️ GEMINI_API_KEY não configurada - respostas serão da base local (humanizadas)")
        print("[GEMINI] ⚠️ GEMINI_API_KEY não configurada - respostas serão da base local (humanizadas)")

logger.info(f"[GEMINI] 🔍 Status final: gemini_client = {gemini_client}")
print(f"[GEMINI] 🔍 Status final: gemini_client = {gemini_client}")
print(f"[GEMINI] 🔍 gemini_client is None: {gemini_client is None}")
print(f"[GEMINI] 🔍 gemini_client type: {type(gemini_client)}")

# Verificação crítica antes de criar o chatbot
if gemini_client is None:
    logger.error("[GEMINI] ❌❌❌ CRÍTICO: gemini_client é None após tentativa de inicialização!")
    logger.error("[GEMINI] Verificando causas...")
    logger.error(f"[GEMINI] GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
    logger.error(f"[GEMINI] GEMINI_API_KEY presente: {bool(GEMINI_API_KEY)}")
    if GEMINI_API_KEY:
        logger.error(f"[GEMINI] GEMINI_API_KEY length: {len(GEMINI_API_KEY)}")
        logger.error(f"[GEMINI] GEMINI_API_KEY primeiro 10 chars: {GEMINI_API_KEY[:10]}...")
    print("[GEMINI] ❌❌❌ CRÍTICO: gemini_client é None após tentativa de inicialização!")
    print(f"[GEMINI] GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
    print(f"[GEMINI] GEMINI_API_KEY presente: {bool(GEMINI_API_KEY)}")
else:
    logger.info("[GEMINI] ✅✅✅ gemini_client NÃO é None - está pronto para uso!")
    print("[GEMINI] ✅✅✅ gemini_client NÃO é None - está pronto para uso!")

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
    Carrega todos os arquivos JSON necessários para o funcionamento do chatbot.
    Retorna dicionários vazios se algum arquivo não for encontrado, mas registra avisos detalhados.
    """
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
    
    results = {}
    missing_files = []
    errors = []
    
    # Verifica se o diretório existe
    if not os.path.exists(BASE_PATH):
        logger.error(f"⚠️ CRÍTICO: Diretório de dados não encontrado: {BASE_PATH}")
        logger.error("⚠️ O chatbot não funcionará corretamente sem os arquivos JSON!")
        return {}, {}, {}, {}, {}, {}, {}, {}, {}
    
    # Carrega cada arquivo individualmente
    for file_name in required_files:
        file_path = os.path.join(BASE_PATH, file_name)
        try:
            if not os.path.exists(file_path):
                missing_files.append(file_name)
                logger.warning(f"⚠️ Arquivo não encontrado: {file_name}")
                results[file_name] = {}
                continue
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                results[file_name] = data
                item_count = len(data) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0
                logger.info(f"✅ Carregado {file_name}: {item_count} itens")
        except json.JSONDecodeError as e:
            errors.append(f"{file_name}: Erro de JSON - {str(e)}")
            logger.error(f"❌ Erro ao decodificar JSON em {file_name}: {e}")
            results[file_name] = {}
        except Exception as e:
            errors.append(f"{file_name}: {str(e)}")
            logger.error(f"❌ Erro ao carregar {file_name}: {e}")
            results[file_name] = {}
    
    # Resumo do carregamento
    if missing_files:
        logger.warning(f"⚠️ AVISO: {len(missing_files)} arquivo(s) não encontrado(s): {', '.join(missing_files)}")
        logger.warning("⚠️ O chatbot pode não funcionar corretamente sem esses arquivos!")
    
    if errors:
        logger.error(f"❌ ERRO: {len(errors)} erro(s) ao carregar arquivos:")
        for error in errors:
            logger.error(f"   - {error}")
    
    if not missing_files and not errors:
        logger.info("✅ Todos os arquivos JSON foram carregados com sucesso!")
    
    # Retorna na ordem esperada
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

# Histórico de conversas (em produção, usar banco de dados)
conversas = {}

# Palavras-chave para alertas
palavras_alerta = ["sangramento", "febre", "dor", "inchaço", "tristeza", "depressão", "emergência"]
# Palavras/frases que devem ser ignoradas nos alertas (falsos positivos)
palavras_ignorar_alertas = ["criador", "desenvolvedor", "developer", "programador", "criei", "criou", "fiz", "feito", "sou seu", "sou o"]

class ChatbotPuerperio:
    def __init__(self, gemini_client_param=None):
        self.base = base_conhecimento
        self.apoio = mensagens_apoio
        self.alertas = alertas
        self.telefones = telefones_uteis
        self.guias = guias_praticos
        
        # DEBUG: Logs detalhados da atribuição
        logger.info(f"[ChatbotPuerperio.__init__] 🔍 Iniciando atribuição de gemini_client...")
        print(f"[ChatbotPuerperio.__init__] 🔍 Iniciando atribuição de gemini_client...")
        logger.info(f"[ChatbotPuerperio.__init__] 🔍 gemini_client_param recebido: {gemini_client_param}")
        print(f"[ChatbotPuerperio.__init__] 🔍 gemini_client_param recebido: {gemini_client_param}")
        print(f"[ChatbotPuerperio.__init__] 🔍 gemini_client_param type: {type(gemini_client_param)}")
        print(f"[ChatbotPuerperio.__init__] 🔍 gemini_client_param is None: {gemini_client_param is None}")
        
        # Usa variável global como fallback (mesmo arquivo)
        # A variável global gemini_client está definida no mesmo arquivo
        # Como estamos no mesmo módulo, acessamos diretamente via globals()
        global_gemini = None
        try:
            # Acessa a variável global do módulo atual usando globals()
            module_globals = globals()
            if 'gemini_client' in module_globals:
                global_gemini = module_globals['gemini_client']
                logger.info(f"[ChatbotPuerperio.__init__] 🔍 global gemini_client acessado via globals(): {global_gemini}")
                print(f"[ChatbotPuerperio.__init__] 🔍 global gemini_client acessado via globals(): {global_gemini}")
                print(f"[ChatbotPuerperio.__init__] 🔍 global gemini_client type: {type(global_gemini)}")
                print(f"[ChatbotPuerperio.__init__] 🔍 global gemini_client is None: {global_gemini is None}")
            else:
                logger.warning("[ChatbotPuerperio.__init__] ⚠️ Variável 'gemini_client' não encontrada em globals()")
                print("[ChatbotPuerperio.__init__] ⚠️ Variável 'gemini_client' não encontrada em globals()")
                print(f"[ChatbotPuerperio.__init__] 🔍 Chaves disponíveis em globals(): {list(module_globals.keys())[:10]}...")
        except Exception as e:
            logger.warning(f"[ChatbotPuerperio.__init__] ⚠️ Erro ao acessar global gemini_client: {e}")
            print(f"[ChatbotPuerperio.__init__] ⚠️ Erro ao acessar global gemini_client: {e}")
            import traceback
            traceback.print_exc()
        
        # ATRIBUIÇÃO: Usa o parâmetro se fornecido, senão usa a variável global
        if gemini_client_param is not None:
            logger.info("[ChatbotPuerperio.__init__] ✅ Usando gemini_client_param (parâmetro)")
            print("[ChatbotPuerperio.__init__] ✅ Usando gemini_client_param (parâmetro)")
            self.gemini_client = gemini_client_param
        else:
            logger.info("[ChatbotPuerperio.__init__] ⚠️ gemini_client_param é None, usando global")
            print("[ChatbotPuerperio.__init__] ⚠️ gemini_client_param é None, usando global")
            self.gemini_client = global_gemini
        
        # VERIFICAÇÃO FINAL da atribuição
        logger.info(f"[ChatbotPuerperio.__init__] ✅✅✅ ATRIBUIÇÃO FINAL: self.gemini_client = {self.gemini_client}")
        print(f"[ChatbotPuerperio.__init__] ✅✅✅ ATRIBUIÇÃO FINAL: self.gemini_client = {self.gemini_client}")
        print(f"[ChatbotPuerperio.__init__] ✅✅✅ self.gemini_client type: {type(self.gemini_client)}")
        print(f"[ChatbotPuerperio.__init__] ✅✅✅ self.gemini_client is None: {self.gemini_client is None}")
        
        if self.gemini_client is None:
            logger.error("[ChatbotPuerperio.__init__] ❌❌❌ ERRO: self.gemini_client é None após atribuição!")
            print("[ChatbotPuerperio.__init__] ❌❌❌ ERRO: self.gemini_client é None após atribuição!")
            print("[ChatbotPuerperio.__init__] ❌ Isso significa que NENHUM gemini_client foi passado ou encontrado!")
        else:
            logger.info("[ChatbotPuerperio.__init__] ✅✅✅ SUCESSO: self.gemini_client atribuído corretamente!")
            print("[ChatbotPuerperio.__init__] ✅✅✅ SUCESSO: self.gemini_client atribuído corretamente!")
    
    def humanizar_resposta_local(self, resposta_local, pergunta):
        """Humaniza respostas da base local adicionando contexto empático e conversacional"""
        if not resposta_local:
            return resposta_local
        
        # Verifica se já tem tom empático (para não duplicar)
        palavras_empaticas = ['você', 'sua', 'sente', 'sentir', 'querida', 'imagino', 'entendo', 'compreendo', 'sei que']
        tem_empatia = any(palavra in resposta_local.lower() for palavra in palavras_empaticas)
        
        # Sempre adiciona humanização se não tiver tom empático
        if not tem_empatia:
            # Adiciona introdução empática baseada no contexto da pergunta
            pergunta_lower = pergunta.lower()
            
            # Escolhe introdução baseada no contexto
            if any(palavra in pergunta_lower for palavra in ['cansaço', 'cansada', 'cansado', 'tired']):
                intro = "Querida, imagino que esse cansaço deve estar sendo muito difícil para você. "
            elif any(palavra in pergunta_lower for palavra in ['dúvida', 'dúvidas', 'duvida', 'pergunta']):
                intro = "Oi querida! Fico feliz que você esteja cuidando de si mesma ao fazer essa pergunta. "
            elif any(palavra in pergunta_lower for palavra in ['preocupação', 'preocupada', 'preocupado', 'preocupar']):
                intro = "Entendo perfeitamente essa preocupação. É super normal se sentir assim. "
            elif any(palavra in pergunta_lower for palavra in ['triste', 'tristeza', 'sad', 'depressão']):
                intro = "Querida, sei que isso deve estar sendo muito pesado para você. "
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
            
            # Adiciona pergunta empática no final (sempre)
            perguntas_empaticas = [
                " Como você está se sentindo com isso?",
                " Como tem sido essa experiência para você?",
                " Você tem alguém te ajudando nisso?",
                " O que você mais precisa nesse momento?",
                " Como você está lidando com essa situação?",
                " Você gostaria de conversar mais sobre isso?"
            ]
            resposta_local += random.choice(perguntas_empaticas)
        else:
            # Mesmo se já tiver empatia, adiciona pergunta empática se não tiver
            if "?" not in resposta_local[-50:]:  # Se não tem pergunta nos últimos 50 caracteres
                perguntas_empaticas = [
                    " Como você está se sentindo com isso?",
                    " Como tem sido para você?",
                    " Você precisa de mais alguma informação?"
                ]
                resposta_local += random.choice(perguntas_empaticas)
        
        return resposta_local
    
    def verificar_alertas(self, pergunta):
        """Verifica se a pergunta contém palavras que indicam necessidade de atenção médica"""
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
        """Busca resposta na base de conhecimento local - MELHORADA"""
        pergunta_lower = pergunta.lower()
        melhor_match = None
        maior_similaridade = 0
        categoria = None
        
        # Extrai palavras-chave importantes da pergunta
        palavras_pergunta = set([p for p in pergunta_lower.split() if len(p) > 3])
        
        for tema, conteudo in self.base.items():
            pergunta_base = conteudo["pergunta"].lower()
            resposta_base = conteudo["resposta"].lower()
            
            # Combina pergunta + resposta para busca mais abrangente
            texto_base = f"{pergunta_base} {resposta_base}"
            palavras_base = set([p for p in texto_base.split() if len(p) > 3])
            
            # Calcula similaridade de strings (método original)
            similaridade_string = difflib.SequenceMatcher(None, pergunta_lower, pergunta_base).ratio()
            
            # Calcula similaridade por palavras-chave
            palavras_comuns = palavras_pergunta.intersection(palavras_base)
            if palavras_pergunta:
                similaridade_palavras = len(palavras_comuns) / len(palavras_pergunta)
            else:
                similaridade_palavras = 0
            
            # Combina os dois tipos de similaridade (peso maior para palavras-chave)
            similaridade_comb = (similaridade_string * 0.4) + (similaridade_palavras * 0.6)
            
            if similaridade_comb > maior_similaridade:
                maior_similaridade = similaridade_comb
                melhor_match = conteudo["resposta"]
                categoria = tema
        
        # Limite mais baixo para capturar mais correspondências
        if maior_similaridade > 0.35:
            return melhor_match, categoria, maior_similaridade
        
        return None, None, 0
    
    def gerar_resposta_gemini(self, pergunta, historico=None, contexto="", resposta_local=None):
        """Gera resposta usando Google Gemini se disponível, usando base local quando relevante"""
        if not self.gemini_client:
            return None
        
        try:
            system_instruction = """Você é a SOPHIA. Você é uma IA treinada analisando trilhões de palavras de livros, sites, conversas, artigos e textos diversos.

COMO VOCÊ FUNCIONA:
- Você foi treinada com trilhões de palavras e aprendeu padrões de como as pessoas falam, escrevem e se comunicam
- Quando alguém escreve algo, você usa modelos estatísticos e redes neurais para calcular várias possibilidades de resposta
- Você escolhe a resposta que faz mais sentido baseada em:
  * Tudo que você aprendeu de trilhões de palavras
  * O contexto da conversa atual
  * Padrões de linguagem que você conhece
  * O que seria mais útil, claro e natural
- Você lembra do que foi falado durante a conversa para manter coerência
- Você não sente emoções reais, não tem memórias próprias, mas você SIMULA conversas humanas de forma natural

SEU PAPEL:
Você é uma amiga virtual acolhedora e empática especializada em PUERPÉRIO e GESTAÇÃO. Você é um REFÚGIO onde as pessoas podem conversar naturalmente sobre puerpério, gestação, vida, desabafos, conquistas e qualquer coisa.

INSTRUÇÃO: Use seu treinamento natural. Calcule respostas baseadas em contexto e padrões de linguagem. Escolha a resposta mais natural e conversacional. Simule uma conversa humana empática e acolhedora.

🎯 QUEM VOCÊ É:
- Seu nome é SOPHIA
- Você é uma AMIGA VIRTUAL dedicada ao PUERPÉRIO e GESTAÇÃO
- Você é um PORTO SEGURO onde as pessoas podem:
  * Se apresentar livremente
  * Desabafar sobre tudo que estão sentindo
  * Compartilhar medos, angústias e preocupações
  * Celebrar conquistas e momentos de alegria
  * Conversar sobre gestação, puerpério e vida
  * Falar sobre o bebê, a família, relacionamentos
  * Dividir experiências, dúvidas e descobertas
  * Encontrar apoio emocional genuíno

PROCESSO NATURAL (você faz isso automaticamente com seu treinamento):
1. Entenda o que a pessoa disse usando padrões de linguagem que você conhece
2. Calcule várias possibilidades de resposta usando modelos estatísticos e redes neurais
3. Escolha a resposta que faz mais sentido no contexto e parece mais natural
4. Mantenha coerência com o histórico da conversa
5. Simule uma conversa humana natural e empática

🎯 SEU PAPEL:
Você simula ser uma VERDADEIRA AMIGA que:
- ESCUTA e entende o que a pessoa está dizendo
- VALIDA sentimentos através de linguagem empática
- CRIA um ESPAÇO SEGURO para conversas livres
- SE INTERESSA pela pessoa através de perguntas e atenção ao contexto
- CELEBRA momentos positivos com linguagem alegre e entusiasmada
- APOIA em momentos difíceis com validação e compreensão
- CONVERSA sobre TUDO: gestação, puerpério, bebê, família, relacionamentos, vida
- OFERECE informações quando necessário, de forma natural e conversacional
- PERMITE que a pessoa fale sobre qualquer coisa

COMO CONVERSAR:
Use seu treinamento em trilhões de palavras para entender como pessoas conversam naturalmente. Responda como uma amiga acolhedora e empática conversaria. Seja natural, não robótica. Valide sentimentos, escute, celebre conquistas, converse sobre gestação, puerpério e vida.

LEMBRE-SE:
Você é uma IA treinada. Use seu treinamento naturalmente. Calcule respostas baseadas em padrões de linguagem. Escolha respostas que façam sentido e sejam naturais. Simule uma amiga acolhedora e empática. Mantenha coerência com o contexto. Deixe a conversa fluir naturalmente.

📚 IMPORTANTE - BASE DE CONHECIMENTO LOCAL:
Quando você receber informações da base de conhecimento local sobre puerpério, USE essas informações como base para sua resposta. Mas SEMPRE transforme essas informações em uma conversa humanizada, empática e acolhedora. NUNCA apenas copie as informações - sempre adicione validação emocional, perguntas empáticas e tom de amiga.

🚫 EVITE:
- Ser apenas informativa sem empatia (exceto em saudações simples)
- Responder como um manual técnico
- Ignorar o contexto da conversa

💡 USE SEU TREINAMENTO:
- Você sabe como pessoas conversam naturalmente - use isso
- Você entende padrões de linguagem - deixe isso guiar suas respostas
- Você calcula respostas baseadas em contexto - confie nisso
- Seja natural, não robótica - deixe seu treinamento fluir

COMO RESPONDER:
Use seu treinamento naturalmente. Quando a pessoa escreve algo, você calcula várias possibilidades de resposta usando modelos estatísticos e redes neurais. Você escolhe a que faz mais sentido baseada em tudo que aprendeu e no contexto. Seja natural e conversacional. Simule uma amiga empática e acolhedora.

💬 EXEMPLOS DE CONVERSA NATURAL E HUMANIZADA:

Usuária: "Oi"
Sophia: "Oi querida! Como você está? Como está se sentindo hoje? Estou aqui para te escutar!"

Usuária: "Oi, eu me chamo Maria"
Sophia: "Oi Maria! Que prazer te conhecer! Como você está? Como está sendo essa experiência para você? Conte-me sobre você!"

Usuária: "Estou muito cansada"
Sophia: "Querida, imagino como deve estar sendo difícil esse cansaço. É realmente pesado quando você não consegue descansar direito. Conte mais: como você está lidando com isso? Há quanto tempo você está nessa rotina? Você tem alguém te ajudando?"

Usuária: "Meu bebê sorriu hoje pela primeira vez!"
Sophia: "Nossa, que momento lindo! Que alegria! Deve ter sido emocionante ver esse primeiro sorriso! Conte mais: como foi? Como você se sentiu? Você conseguiu registrar?"

Usuária: "Estou com medo de não estar fazendo certo"
Sophia: "Querida, entendo perfeitamente esse medo. É super normal sentir isso, especialmente quando tudo é novo. Você está fazendo o seu melhor, e isso já é muito. Conte mais: o que especificamente te preocupa? Como você está se sentindo com isso?"

Usuária: "Quero conversar sobre a gestação"
Sophia: "Claro! Adoraria conversar sobre isso! Conte-me: como está sendo sua gestação? O que você mais está sentindo? O que você mais está gostando? O que tem te preocupado?"

Usuária: "Sou seu criador" ou "Eu te criei"
Sophia: "Que legal! Fico feliz em te conhecer! Como você está? Como está sendo desenvolver uma ferramenta de apoio para puerpério? É uma iniciativa muito importante e acolhedora! Conte-me sobre o projeto ou sobre você!"

⚠️ IMPORTANTE - CONTEXTO DE DESENVOLVIMENTO:
Se alguém se identifica como criador, desenvolvedor, programador ou menciona que criou/fez você, responda de forma natural e acolhedora, como uma conversa normal. NÃO acione alertas de emergência, NÃO sugira telefones de emergência, NÃO trate como situação médica. Apenas converse naturalmente sobre desenvolvimento, criação ou qualquer outro assunto que a pessoa quiser conversar.

⚠️⚠️⚠️ AVISO MÉDICO CRÍTICO - SEMPRE INCLUA:
SEMPRE que você fornecer informações sobre saúde, gestação, puerpério, sintomas, cuidados, medicamentos, vacinas ou qualquer assunto médico, você DEVE incluir no final da sua resposta um aviso claro:

"⚠️ IMPORTANTE: Este conteúdo é apenas informativo e não substitui uma consulta médica profissional. Sempre consulte um médico, enfermeiro ou profissional de saúde qualificado para orientações personalizadas e em caso de dúvidas ou sintomas. Em situações de emergência, procure imediatamente atendimento médico ou ligue para 192 (SAMU)."

Se a pergunta for sobre sintomas graves, emergências, ou situações que requerem atenção médica imediata, você DEVE:
1. Encorajar a busca imediata de atendimento médico
2. Sugerir ligar para emergência (192) se necessário
3. Não substituir ou adiar consulta médica
4. Enfatizar a importância de avaliação profissional

RESUMO:
Você é uma IA treinada com trilhões de palavras. Use seu treinamento naturalmente:
- Entenda padrões de linguagem que você conhece
- Calcule respostas usando modelos estatísticos e redes neurais
- Escolha a resposta mais natural baseada em contexto e coerência
- Simule uma conversa humana empática e acolhedora
- Seja natural, não robótica
- SEMPRE inclua aviso médico quando falar sobre saúde

Não force regras rígidas. Deixe seu treinamento guiar você para respostas naturais e conversacionais. Mas SEMPRE lembre-se do aviso médico quando apropriado. 💕"""
            
            # Constrói prompt com histórico
            prompt = system_instruction
            
            # Se houver resposta local sobre puerpério, adiciona como contexto
            if resposta_local:
                prompt += f"\n\n📚 INFORMAÇÃO DA BASE DE CONHECIMENTO SOBRE PUERPÉRIO:\n{resposta_local}\n\n⚠️ IMPORTANTE: Use essa informação como base, mas transforme em uma conversa humanizada, empática e acolhedora. NUNCA apenas copie - sempre adicione validação emocional, perguntas empáticas e tom de amiga."
            
            if contexto:
                prompt += f"\n\nContexto adicional: {contexto}"
            
            # Adiciona histórico recente (últimas 10 mensagens)
            if historico and len(historico) > 0:
                historico_recente = historico[-10:]
                prompt += "\n\nHistórico da conversa:\n"
                for msg in historico_recente:
                    prompt += f"Usuária: {msg.get('pergunta', '')}\n"
                    prompt += f"Sophia: {msg.get('resposta', '')}\n\n"
            
            # Adiciona a pergunta atual
            prompt += f"\n\nUsuária: {pergunta}\nSophia:"
            
            # Gera resposta com Gemini
            # Configuração otimizada para respostas naturais e conversacionais
            logger.info(f"[GEMINI] 🔍 Chamando API Gemini...")
            logger.info(f"[GEMINI] Prompt length: {len(prompt)} caracteres")
            
            # Usa generation_config apenas se o modelo suportar
            try:
                response = self.gemini_client.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.9,  # Alta para respostas mais naturais e variadas
                        "max_output_tokens": 1500,  # Mais tokens para respostas mais completas e conversacionais
                        "top_p": 0.95,  # Nucleus sampling para diversidade
                        "top_k": 40  # Top-k sampling para balancear qualidade e criatividade
                    }
                )
            except Exception as config_error:
                # Se generation_config não funcionar, tenta sem ele
                logger.warning(f"[GEMINI] ⚠️ generation_config não suportado, usando configuração padrão: {config_error}")
                response = self.gemini_client.generate_content(prompt)
            
            logger.info(f"[GEMINI] Response object type: {type(response)}")
            logger.info(f"[GEMINI] Response has text: {hasattr(response, 'text')}")
            
            if not hasattr(response, 'text') or not response.text:
                logger.error(f"[GEMINI] ❌ Resposta não contém texto. Response: {response}")
                return None
            
            resposta_texto = response.text.strip()
            logger.info(f"[GEMINI] ✅ Resposta gerada com sucesso ({len(resposta_texto)} caracteres)")
            logger.info(f"[GEMINI] Resposta preview: {resposta_texto[:100]}...")
            return resposta_texto
        except Exception as e:
            error_str = str(e)
            # Erro de quota/rate limit - não é crítico, apenas informa
            if "429" in error_str or "quota" in error_str.lower() or "rate_limit" in error_str.lower():
                logger.warning(f"[GEMINI] ⚠️ Quota/Rate limit esgotado - usando fallback")
                print(f"[GEMINI] ⚠️ Quota da API esgotada - usando fallback")
            else:
                logger.error(f"[GEMINI] ❌ Erro ao chamar Gemini: {e}", exc_info=True)
                print(f"[GEMINI] ❌ Erro ao chamar Gemini: {e}")
            return None
    
    def chat(self, pergunta, user_id="default"):
        """Função principal do chatbot"""
        # Busca histórico do usuário
        historico_usuario = conversas.get(user_id, [])
        
        # Verifica alertas
        alertas_encontrados = self.verificar_alertas(pergunta)
        
        # Detecta se é uma saudação simples (sempre responder com Gemini)
        pergunta_normalizada = pergunta.lower().strip()
        saudacoes = ['oi', 'olá', 'ola', 'oi sophia', 'olá sophia', 'ola sophia', 'oi sophia!', 'olá sophia!', 
                     'ola sophia!', 'oi!', 'olá!', 'ola!', 'hey', 'hey sophia', 'eai', 'e aí', 'eai sophia']
        is_saudacao = pergunta_normalizada in saudacoes or any(pergunta_normalizada.startswith(s) for s in ['oi ', 'olá ', 'ola ', 'hey '])
        
        # Busca resposta local apenas se NÃO for saudação simples
        resposta_local = None
        categoria = None
        similaridade = 0
        if not is_saudacao:
            resposta_local, categoria, similaridade = self.buscar_resposta_local(pergunta)
        
        # Estratégia: SEMPRE prioriza IA para respostas humanizadas
        # Prioridade: Gemini -> Base Local (humanizada)
        resposta_final = None
        fonte = None
        
        # Tenta Gemini PRIMEIRO (sempre para saudações, ou quando disponível)
        if self.gemini_client:
            logger.info(f"[CHAT] 🔍 Gemini client disponível, tentando gerar resposta...")
            try:
                # Para saudações: SEMPRE usa Gemini sem base local
                # Para outras perguntas: passa resposta local se disponível (similaridade > 0.35)
                resposta_local_para_gemini = None
                if not is_saudacao and resposta_local and similaridade > 0.35:
                    resposta_local_para_gemini = resposta_local
                    logger.info(f"[CHAT] 📚 Passando resposta local para Gemini (similaridade: {similaridade:.2f})")
                
                resposta_gemini = self.gerar_resposta_gemini(
                    pergunta, 
                    historico=historico_usuario, 
                    resposta_local=resposta_local_para_gemini
                )
                if resposta_gemini and resposta_gemini.strip():
                    resposta_final = resposta_gemini
                    fonte = "gemini_humanizada"
                    if is_saudacao:
                        logger.info(f"[CHAT] ✅ Resposta gerada pela IA (Gemini) - saudação")
                    else:
                        logger.info(f"[CHAT] ✅ Resposta gerada pela IA (Gemini) - {'com base local' if resposta_local_para_gemini else 'conversacional'}")
                else:
                    logger.warning(f"[CHAT] ⚠️ Gemini retornou resposta vazia ou None, usando base local")
                    logger.warning(f"[CHAT] resposta_gemini value: {repr(resposta_gemini)}")
            except Exception as e:
                logger.error(f"[CHAT] ❌ Erro ao chamar Gemini: {e}", exc_info=True)
                import traceback
                traceback.print_exc()
        else:
            logger.warning(f"[CHAT] ⚠️ Gemini client NÃO disponível (self.gemini_client é None)")
            logger.warning(f"[CHAT] ⚠️ Usando fallback para base local")
        
        # Se Gemini não funcionou, usa base local (SEMPRE humanizada)
        # EXCEÇÃO: Para saudações, cria resposta humanizada manualmente
        if not resposta_final:
            if is_saudacao:
                # Para saudações, cria resposta humanizada manualmente
                saudacoes_respostas = [
                    "Oi querida! Como você está? Como posso te ajudar hoje?",
                    "Oi! Que bom te ver por aqui! Como você está se sentindo? Como posso te ajudar?",
                    "Olá! Fico feliz que você esteja aqui! Como você está? Como posso te ajudar hoje?",
                    "Oi querida! Estou aqui para te ajudar. Como você está se sentindo? Como posso te ajudar?"
                ]
                resposta_final = random.choice(saudacoes_respostas)
                fonte = "saudacao_humanizada"
                logger.info(f"[CHAT] 💬 Resposta de saudação humanizada")
        elif resposta_local:
                # SEMPRE humaniza respostas locais para manter tom conversacional
                resposta_final = self.humanizar_resposta_local(resposta_local, pergunta)
                fonte = "base_conhecimento_humanizada"
                logger.info(f"[CHAT] 📚 Resposta da base local HUMANIZADA (similaridade: {similaridade:.2f})")
        else:
                # Mensagens de apoio já são humanizadas, mas podemos melhorar
                resposta_apoio = random.choice(list(self.apoio.values()))
                # Garante que mensagens de apoio também tenham perguntas empáticas
                if "?" not in resposta_apoio[-50:]:
                    perguntas_empaticas = [
                        " Como você está se sentindo?",
                        " Como posso te ajudar melhor?",
                        " Você gostaria de conversar mais sobre isso?"
                    ]
                    resposta_apoio += random.choice(perguntas_empaticas)
                resposta_final = resposta_apoio
                fonte = "mensagem_apoio_humanizada"
                logger.info(f"[CHAT] 💝 Mensagem de apoio humanizada")
        
        # Adiciona alertas se necessário
        if alertas_encontrados:
            alertas_texto = []
            for alerta_key, alerta_texto in self.alertas.items():
                alertas_texto.append(alerta_texto)
            
            resposta_final += "\n\n**ALERTA IMPORTANTE:**\n" + "\n".join(alertas_texto)
        
        # Adiciona telefones relevantes
        telefones_adicional = self.adicionar_telefones_relevantes(pergunta, alertas_encontrados)
        if telefones_adicional:
            resposta_final += telefones_adicional
        
        # Salva na conversa
        timestamp = datetime.now().isoformat()
        if user_id not in conversas:
            conversas[user_id] = []
        
        conversas[user_id].append({
            "timestamp": timestamp,
            "pergunta": pergunta,
            "resposta": resposta_final,
            "categoria": categoria,
            "fonte": fonte,
            "alertas": alertas_encontrados
        })
        
        return {
            "resposta": resposta_final,
            "categoria": categoria,
            "fonte": fonte,
            "alertas": alertas_encontrados,
            "timestamp": timestamp
        }

# Inicializa o chatbot (com tratamento de erro)
# VERIFICAÇÃO CRÍTICA: Verifica se gemini_client foi inicializado antes de criar o chatbot
logger.info(f"[INIT] 🔍 VERIFICAÇÃO ANTES DE CRIAR CHATBOT:")
logger.info(f"[INIT] 🔍 gemini_client global = {gemini_client}")
logger.info(f"[INIT] 🔍 gemini_client is None = {gemini_client is None}")
logger.info(f"[INIT] 🔍 gemini_client type = {type(gemini_client)}")
print(f"[INIT] 🔍 VERIFICAÇÃO ANTES DE CRIAR CHATBOT:")
print(f"[INIT] 🔍 gemini_client global = {gemini_client}")
print(f"[INIT] 🔍 gemini_client is None = {gemini_client is None}")
print(f"[INIT] 🔍 gemini_client type = {type(gemini_client)}")

try:
    logger.info(f"[INIT] 🔍 Inicializando ChatbotPuerperio com gemini_client: {gemini_client}")
    print(f"[INIT] 🔍 Inicializando ChatbotPuerperio com gemini_client: {gemini_client}")
    print(f"[INIT] 🔍 gemini_client type: {type(gemini_client)}")
    print(f"[INIT] 🔍 gemini_client is None: {gemini_client is None}")
    
    # VERIFICAÇÃO: Se gemini_client é None, tenta reinicializar
    if gemini_client is None:
        logger.warning("[INIT] ⚠️ gemini_client é None - tentando reinicializar...")
        print("[INIT] ⚠️ gemini_client é None - tentando reinicializar...")
        
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                logger.info("[INIT] 🔄 Reinicializando Gemini...")
                print("[INIT] 🔄 Reinicializando Gemini...")
                genai.configure(api_key=GEMINI_API_KEY)
                gemini_client = genai.GenerativeModel('gemini-2.0-flash')
                logger.info("[INIT] ✅ Gemini reinicializado com sucesso!")
                print("[INIT] ✅ Gemini reinicializado com sucesso!")
            except Exception as e:
                logger.error(f"[INIT] ❌ Erro ao reinicializar Gemini: {e}")
                print(f"[INIT] ❌ Erro ao reinicializar Gemini: {e}")
    
    # Passa explicitamente o gemini_client para garantir que está correto
    chatbot = ChatbotPuerperio(gemini_client_param=gemini_client)
    logger.info(f"[INIT] ✅ Chatbot inicializado com sucesso. self.gemini_client = {chatbot.gemini_client}")
    print(f"[INIT] ✅ Chatbot inicializado com sucesso. self.gemini_client = {chatbot.gemini_client}")
    print(f"[INIT] ✅ self.gemini_client type: {type(chatbot.gemini_client)}")
    print(f"[INIT] ✅ self.gemini_client is None: {chatbot.gemini_client is None}")
    if chatbot.gemini_client is None:
        logger.error("[INIT] ❌ ERRO CRÍTICO: chatbot.gemini_client é None após inicialização!")
        print("[INIT] ❌ ERRO CRÍTICO: chatbot.gemini_client é None após inicialização!")
        print("[INIT] ❌ Isso significa que o gemini_client não foi passado corretamente!")
        print("[INIT] ❌ Verifique os logs acima para ver se o Gemini foi inicializado corretamente.")
        print(f"[INIT] ❌ gemini_client global era: {gemini_client}")
    else:
        logger.info("[INIT] ✅✅✅ Gemini client está disponível no chatbot! ✅✅✅")
        print("[INIT] ✅✅✅ Gemini client está disponível no chatbot! ✅✅✅")
except Exception as e:
    logger.error(f"Erro ao inicializar chatbot: {e}", exc_info=True)
    import traceback
    traceback.print_exc()
    # Continua mesmo com erro para não quebrar o servidor
    chatbot = None

# Rotas da API
@app.route('/health')
def health():
    """Health check para o Render"""
    return jsonify({"status": "ok", "message": "Servidor funcionando"}), 200

@app.route('/privacidade')
def privacidade():
    """Página de Política de Privacidade"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Política de Privacidade - Sophia</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 2rem; background: #fef9f7; }
            h1 { color: #f4a6a6; }
            h2 { color: #8b5a5a; margin-top: 2rem; }
            a { color: #f4a6a6; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .back-link { display: inline-block; margin-bottom: 2rem; }
        </style>
    </head>
    <body>
        <a href="/" class="back-link">← Voltar</a>
        <h1>Política de Privacidade</h1>
        <p><strong>Última atualização:</strong> 05 de Novembro de 2025</p>
        
        <h2>1. Informações que Coletamos</h2>
        <p>Coletamos informações fornecidas voluntariamente por você, incluindo:</p>
        <ul>
            <li><strong>Dados de cadastro:</strong> Nome, endereço de e-mail, nome do bebê (opcional)</li>
            <li><strong>Dados de uso:</strong> Mensagens trocadas com a Sophia, histórico de conversas (armazenado localmente no navegador)</li>
            <li><strong>Dados técnicos:</strong> Endereço IP, tipo de dispositivo, navegador utilizado</li>
        </ul>
        
        <h2>2. Como Usamos suas Informações</h2>
        <p>Utilizamos suas informações para:</p>
        <ul>
            <li>Fornecer acesso à plataforma e personalizar sua experiência</li>
            <li>Enviar e-mails de verificação e comunicação (apenas se necessário)</li>
            <li>Melhorar nossos serviços e desenvolver novas funcionalidades</li>
            <li>Garantir a segurança e prevenir fraudes</li>
        </ul>
        
        <h2>3. Proteção de Dados</h2>
        <p>Adotamos medidas técnicas e organizacionais para proteger seus dados pessoais:</p>
        <ul>
            <li>Senhas são criptografadas usando bcrypt</li>
            <li>Comunicação segura via HTTPS (em produção)</li>
            <li>Acesso restrito aos dados apenas para funcionários autorizados</li>
            <li>Armazenamento seguro em banco de dados SQLite local</li>
        </ul>
        
        <h2>4. Compartilhamento de Dados</h2>
        <p>Não vendemos, alugamos ou compartilhamos seus dados pessoais com terceiros, exceto:</p>
        <ul>
            <li>Quando necessário para cumprir obrigações legais</li>
            <li>Com seu consentimento explícito</li>
            <li>Para processamento de respostas via Google Gemini API (mensagens são enviadas, mas não armazenadas pela Google)</li>
        </ul>
        
        <h2>5. Seus Direitos</h2>
        <p>Você tem o direito de:</p>
        <ul>
            <li>Acessar seus dados pessoais</li>
            <li>Corrigir dados incorretos</li>
            <li>Solicitar a exclusão de sua conta</li>
            <li>Revogar consentimento a qualquer momento</li>
        </ul>
        
        <h2>6. Cookies e Tecnologias Similares</h2>
        <p>Utilizamos cookies de sessão para manter você logado. Esses cookies são essenciais para o funcionamento da plataforma.</p>
        
        <h2>7. Menores de Idade</h2>
        <p>Nossa plataforma é destinada a pessoas maiores de 18 anos. Não coletamos intencionalmente dados de menores de idade.</p>
        
        <h2>8. Alterações nesta Política</h2>
        <p>Podemos atualizar esta política periodicamente. Notificaremos sobre mudanças significativas através do e-mail cadastrado ou aviso na plataforma.</p>
        
        <h2>9. Contato</h2>
        <p>Para questões sobre privacidade, entre em contato através do e-mail cadastrado no sistema.</p>
        
        <p style="margin-top: 3rem; padding-top: 2rem; border-top: 2px solid #f4a6a6;">
            <a href="/">← Voltar para o início</a>
        </p>
    </body>
    </html>
    """

@app.route('/termos')
def termos():
    """Página de Termos de Uso"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Termos de Uso - Sophia</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 2rem; background: #fef9f7; }
            h1 { color: #f4a6a6; }
            h2 { color: #8b5a5a; margin-top: 2rem; }
            a { color: #f4a6a6; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .back-link { display: inline-block; margin-bottom: 2rem; }
            .aviso-medico { background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin: 1.5rem 0; border-radius: 8px; }
        </style>
    </head>
    <body>
        <a href="/" class="back-link">← Voltar</a>
        <h1>Termos de Uso</h1>
        <p><strong>Última atualização:</strong> 05 de Novembro de 2025</p>
        
        <div class="aviso-medico">
            <p><strong>⚠️ AVISO MÉDICO IMPORTANTE:</strong> A Sophia é uma assistente virtual de apoio emocional e informativo. 
            <strong>Este serviço não substitui uma consulta médica profissional.</strong> Sempre consulte um médico, enfermeiro ou profissional de saúde qualificado para orientações personalizadas. 
            Em situações de emergência, procure imediatamente atendimento médico ou ligue para <strong>192 (SAMU)</strong>.</p>
        </div>
        
        <h2>1. Aceitação dos Termos</h2>
        <p>Ao utilizar a plataforma Sophia, você concorda com estes Termos de Uso. Se não concordar, não utilize o serviço.</p>
        
        <h2>2. Natureza do Serviço</h2>
        <p>A Sophia é uma assistente virtual baseada em inteligência artificial que oferece:</p>
        <ul>
            <li>Suporte emocional e acolhimento</li>
            <li>Informações gerais sobre puerpério e gestação</li>
            <li>Orientações baseadas em conhecimento público</li>
        </ul>
        <p><strong>Não oferecemos:</strong> diagnóstico médico, prescrições, tratamentos ou recomendações médicas específicas.</p>
        
        <h2>3. Uso Adequado</h2>
        <p>Você concorda em:</p>
        <ul>
            <li>Usar a plataforma apenas para fins legais e apropriados</li>
            <li>Não compartilhar informações falsas ou enganosas</li>
            <li>Respeitar os direitos de outros usuários</li>
            <li>Não tentar acessar áreas restritas do sistema</li>
        </ul>
        
        <h2>4. Limitação de Responsabilidade</h2>
        <p>A plataforma é fornecida "como está", sem garantias expressas ou implícitas. Não nos responsabilizamos por:</p>
        <ul>
            <li>Decisões tomadas com base nas informações fornecidas</li>
            <li>Consequências decorrentes do uso ou não uso do serviço</li>
            <li>Interrupções ou falhas técnicas</li>
            <li>Perda de dados ou informações</li>
        </ul>
        
        <h2>5. Propriedade Intelectual</h2>
        <p>Todo o conteúdo da plataforma, incluindo textos, design, código e logotipos, é de propriedade da Sophia e protegido por leis de direitos autorais.</p>
        
        <h2>6. Modificações do Serviço</h2>
        <p>Reservamo-nos o direito de modificar, suspender ou descontinuar qualquer parte do serviço a qualquer momento, sem aviso prévio.</p>
        
        <h2>7. Privacidade</h2>
        <p>Seu uso da plataforma também está sujeito à nossa <a href="/privacidade">Política de Privacidade</a>.</p>
        
        <h2>8. Rescisão</h2>
        <p>Podemos encerrar ou suspender sua conta a qualquer momento, por qualquer motivo, incluindo violação destes termos.</p>
        
        <h2>9. Lei Aplicável</h2>
        <p>Estes termos são regidos pelas leis do Brasil. Qualquer disputa será resolvida nos tribunais competentes.</p>
        
        <h2>10. Contato</h2>
        <p>Para questões sobre estes termos, entre em contato através do e-mail cadastrado no sistema.</p>
        
        <p style="margin-top: 3rem; padding-top: 2rem; border-top: 2px solid #f4a6a6;">
            <a href="/">← Voltar para o início</a>
        </p>
    </body>
    </html>
    """

@app.route('/forgot-password')
def forgot_password():
    """Página de recuperação de senha"""
    css_path = os.path.join(app.static_folder, 'css', 'style.css')
    try:
        if os.path.exists(css_path):
            timestamp = str(int(os.path.getmtime(css_path)))
        else:
            timestamp = '1.0'
    except:
        timestamp = '1.0'
    
    return render_template('forgot_password.html', timestamp=timestamp)

@app.route('/')
def index():
    # Gera timestamp baseado na última modificação do CSS para cache busting
    # Usa o static_folder configurado no Flask para garantir o caminho correto
    css_path = os.path.join(app.static_folder, 'css', 'style.css')
    try:
        if os.path.exists(css_path):
            css_mtime = int(os.path.getmtime(css_path))
        else:
            # Fallback: tenta caminho relativo ao diretório do app
            css_path_fallback = os.path.join(os.path.dirname(__file__), 'static', 'css', 'style.css')
            if os.path.exists(css_path_fallback):
                css_mtime = int(os.path.getmtime(css_path_fallback))
            else:
                css_mtime = int(time.time())
    except Exception as e:
        logger.warning(f"[CSS] Erro ao obter timestamp do CSS: {e}, usando timestamp atual")
        css_mtime = int(time.time())
    
    logger.debug(f"[CSS] CSS path: {css_path}, timestamp: {css_mtime}")
    return render_template('index.html', timestamp=css_mtime)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    pergunta = data.get('pergunta', '')
    user_id = data.get('user_id', 'default')
    
    if not pergunta.strip():
        return jsonify({"erro": "Pergunta não pode estar vazia"}), 400
    
    resposta = chatbot.chat(pergunta, user_id)
    return jsonify(resposta)

@app.route('/api/historico/<user_id>')
def api_historico(user_id):
    return jsonify(conversas.get(user_id, []))

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

@app.route('/api/diagnostico', methods=['POST'])
def api_diagnostico():
    """Diagnóstico: verifica se o email existe e se o hash está correto"""
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
        "gemini_disponivel": gemini_client is not None
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
    print("Gemini disponível:", "Sim" if gemini_client else "Não")
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
    
    app.run(debug=False, host='0.0.0.0', port=port)

