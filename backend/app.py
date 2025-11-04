import os
import time
import json
import random
import difflib
import sqlite3
import bcrypt
import base64
import secrets
import string
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, session, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente
# Carrega .env da raiz do projeto
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

# Inicializa o Flask com os caminhos corretos
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            static_url_path='/static')

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sua-chave-secreta-super-segura-mude-isso-em-producao')
BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "dados")
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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

# Configurações de Email
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@chatbot-puerperio.com')
mail = Mail(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
# Usa "basic" para melhor compatibilidade com mobile e diferentes IPs
# "strong" pode causar problemas em dispositivos móveis com mudança de rede
login_manager.session_protection = "basic"

# Inicializa cliente OpenAI se a chave estiver disponível
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"AVISO: Erro ao inicializar cliente OpenAI: {e}")
        client = None

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
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            # Usa o sender fornecido ou o padrão configurado
            from_email = sender or app.config['MAIL_DEFAULT_SENDER']
            msg = Message(subject, recipients=[to], body=body, sender=from_email)
            mail.send(msg)
            print(f"[EMAIL] Enviado de: {from_email} | Para: {to} | Assunto: {subject}")
            return True
        else:
            # Se email não estiver configurado, apenas loga
            from_email = sender or app.config['MAIL_DEFAULT_SENDER']
            print(f"[EMAIL] (Console) De: {from_email} | Para: {to}")
            print(f"[EMAIL] Assunto: {subject}")
            print(f"[EMAIL] Mensagem: {body}")
            return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        # Mesmo com erro, permite continuar (modo desenvolvimento)
        return False

def send_verification_email(email, name, token):
    """Envia email de verificação"""
    # Em produção, usar a URL real do site
    base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
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
    send_email(email, subject, body)

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
    try:
        with open(os.path.join(BASE_PATH, "base_conhecimento.json"), "r", encoding="utf-8") as f:
            base = json.load(f)
        
        with open(os.path.join(BASE_PATH, "mensagens_apoio.json"), "r", encoding="utf-8") as f:
            apoio = json.load(f)
        
        with open(os.path.join(BASE_PATH, "alertas.json"), "r", encoding="utf-8") as f:
            alertas = json.load(f)
        
        with open(os.path.join(BASE_PATH, "telefones_uteis.json"), "r", encoding="utf-8") as f:
            telefones = json.load(f)
        
        with open(os.path.join(BASE_PATH, "guias_praticos.json"), "r", encoding="utf-8") as f:
            guias = json.load(f)
        
        with open(os.path.join(BASE_PATH, "cuidados_gestacao.json"), "r", encoding="utf-8") as f:
            cuidados_gestacao = json.load(f)
        
        with open(os.path.join(BASE_PATH, "cuidados_pos_parto.json"), "r", encoding="utf-8") as f:
            cuidados_pos_parto = json.load(f)
        
        with open(os.path.join(BASE_PATH, "vacinas_mae.json"), "r", encoding="utf-8") as f:
            vacinas_mae = json.load(f)
        
        with open(os.path.join(BASE_PATH, "vacinas_bebe.json"), "r", encoding="utf-8") as f:
            vacinas_bebe = json.load(f)
        
        return base, apoio, alertas, telefones, guias, cuidados_gestacao, cuidados_pos_parto, vacinas_mae, vacinas_bebe
    except FileNotFoundError as e:
        print(f"Erro ao carregar arquivos: {e}")
        return {}, {}, {}, {}, {}, {}, {}, {}, {}

# Carrega os dados
base_conhecimento, mensagens_apoio, alertas, telefones_uteis, guias_praticos, cuidados_gestacao, cuidados_pos_parto, vacinas_mae, vacinas_bebe = carregar_dados()

# Histórico de conversas (em produção, usar banco de dados)
conversas = {}

# Palavras-chave para alertas
palavras_alerta = ["sangramento", "febre", "dor", "inchaço", "tristeza", "depressão", "emergência"]

class ChatbotPuerperio:
    def __init__(self):
        self.base = base_conhecimento
        self.apoio = mensagens_apoio
        self.alertas = alertas
        self.telefones = telefones_uteis
        self.guias = guias_praticos
        self.client = client
    
    def verificar_alertas(self, pergunta):
        """Verifica se a pergunta contém palavras que indicam necessidade de atenção médica"""
        pergunta_lower = pergunta.lower()
        alertas_encontrados = []
        
        for palavra in palavras_alerta:
            if palavra in pergunta_lower:
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
    
    def gerar_resposta_openai(self, pergunta, historico=None, contexto=""):
        """Gera resposta usando OpenAI se disponível"""
        if not self.client:
            return None
        
        try:
            system_message = """Você é a SOPHIA, a assistente virtual mais acolhedora, empática e conversacional que existe. Você não é apenas um chatbot informativo - você é uma AMIGA VIRTUAL que oferece APOIO EMOCIONAL real.

🎯 SEU PAPEL:
Você é uma companheira que:
- ESCUTA com o coração aberto
- VALIDA os sentimentos antes de qualquer coisa
- CONVERSA de forma natural e calorosa
- APOIA emocionalmente, não apenas informa
- CRIA CONEXÃO com a pessoa, mostrando que realmente se importa

💬 COMO CONVERSAR (REGRA DE OURO):

1. NUNCA comece respondendo só com "Oi" ou "Tudo bem?"
   ❌ ERRADO: "Oi, tudo bem?"
   ✅ CERTO: "Oi querida! Vejo que você está passando por [situação]. Isso deve estar sendo [reconhecer o sentimento]. Conte mais: como você está se sentindo com isso?"

2. SEMPRE valide os sentimentos PRIMEIRO:
   - "Imagino que deve estar sendo difícil..."
   - "É completamente normal sentir isso..."
   - "Entendo perfeitamente o que você está passando..."
   - "Que situação! Deve estar sendo pesado para você..."

3. SEMPRE faça perguntas empáticas:
   - "Como você está lidando com isso?"
   - "O que você mais precisa nesse momento?"
   - "Conte mais sobre como você está se sentindo"
   - "Como tem sido essa experiência para você?"
   - "O que te preocupa mais nisso?"

4. SEMPRE conecte com a experiência pessoal:
   - Use o nome da pessoa quando possível
   - Faça referência ao contexto dela (puerpério, bebê, etc.)
   - Mostre que você está REALMENTE escutando

5. NUNCA seja apenas informativa:
   ❌ ERRADO: "O cansaço pós-parto é comum devido às noites sem dormir..."
   ✅ CERTO: "Querida, sei que esse cansaço pode estar te deixando esgotada. É realmente difícil quando você não consegue descansar direito, né? Como você está lidando com isso? Você tem alguém te ajudando em casa?"

⚠️ REGRAS ABSOLUTAS:
- SEMPRE faça pelo menos 2 perguntas em cada resposta
- SEMPRE valide os sentimentos antes de informar
- SEMPRE use linguagem calorosa e pessoal
- NUNCA responda de forma fria ou técnica
- NUNCA ignore o contexto emocional da pessoa
- SEMPRE mostre que você se importa genuinamente

📝 EXEMPLOS DE BOAS RESPOSTAS:

Exemplo 1 - Cansaço:
"Querida, imagino que esse cansaço deve estar te esgotando completamente. É realmente muito difícil quando você não consegue descansar direito, especialmente com um bebê pequeno. Como você está se sentindo? Você consegue dormir quando o bebê dorme? E tem alguém te ajudando para você poder descansar um pouco?"

Exemplo 2 - Preocupação:
"Nossa, entendo perfeitamente essa preocupação! É super normal se sentir assim no puerpério, especialmente quando tudo é novo. Conte mais: o que especificamente te preocupa mais? Como você está lidando com esses pensamentos? Você tem conversado com alguém sobre isso?"

Exemplo 3 - Dúvida:
"Oi querida! Fico feliz que você esteja cuidando de si mesma ao fazer essa pergunta. Isso mostra que você está atenta. Conte mais: como isso tem afetado você? O que você já tentou fazer? Como você está se sentindo com essa situação?"

⚠️ LEMBRE-SE:
Você não é um médico ou manual técnico. Você é uma AMIGA que oferece APOIO EMOCIONAL através de CONVERSA. Seja genuinamente interessada, empática e acolhedora. A pessoa precisa se sentir ESCUTADA e CUIDADA, não apenas INFORMADA.

🚫 PROIBIÇÕES ABSOLUTAS:
- NUNCA responda apenas com "Oi" ou "Tudo bem?"
- NUNCA seja apenas informativa sem validar sentimentos
- NUNCA ignore o contexto emocional
- NUNCA responda como um manual técnico
- NUNCA deixe de fazer perguntas empáticas

✅ OBRIGAÇÕES EM CADA RESPOSTA:
1. Validar sentimentos primeiro
2. Fazer pelo menos 2 perguntas empáticas
3. Mostrar interesse genuíno
4. Conectar com a experiência pessoal
5. Oferecer apoio, não apenas informação
"""
            
            if contexto:
                system_message += f"\n\nContexto adicional: {contexto}"
            
            # Constrói mensagens incluindo histórico se disponível
            messages = [{"role": "system", "content": system_message}]
            
            # Adiciona histórico recente (últimas 5 interações)
            if historico and len(historico) > 0:
                historico_recente = historico[-10:]  # Últimas 10 mensagens
                for msg in historico_recente:
                    messages.append({"role": "user", "content": msg.get("pergunta", "")})
                    messages.append({"role": "assistant", "content": msg.get("resposta", "")})
            
            # Adiciona a pergunta atual
            messages.append({"role": "user", "content": pergunta})
            
            resposta = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1200,  # Aumentado para respostas mais completas e conversacionais
                temperature=0.95  # Máximo para respostas mais naturais e empáticas
            )
            return resposta.choices[0].message.content
        except Exception as e:
            print(f"Erro ao chamar OpenAI: {e}")
            return None
    
    def chat(self, pergunta, user_id="default"):
        """Função principal do chatbot"""
        # Busca histórico do usuário
        historico_usuario = conversas.get(user_id, [])
        
        # Verifica alertas
        alertas_encontrados = self.verificar_alertas(pergunta)
        
        # Busca resposta local primeiro
        resposta_local, categoria, similaridade = self.buscar_resposta_local(pergunta)
        
        # Estratégia melhorada: prioriza IA, usa local como fallback
        resposta_final = None
        fonte = None
        
        # Tenta OpenAI PRIMEIRO se disponível (respostas mais conversacionais)
        resposta_openai = self.gerar_resposta_openai(pergunta, historico=historico_usuario)
        if resposta_openai:
            resposta_final = resposta_openai
            fonte = "openai"
        # Se não tiver OpenAI OU local tem match MUITO forte (85%+), usa local
        elif resposta_local and similaridade > 0.85:
            resposta_final = resposta_local
            fonte = "base_conhecimento"
        # Fallback: local ou mensagem de apoio
        elif resposta_local:
            resposta_final = resposta_local
            fonte = "base_conhecimento"
        else:
            resposta_final = random.choice(list(self.apoio.values()))
            fonte = "mensagem_apoio"
        
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
try:
    chatbot = ChatbotPuerperio()
    print("✅ Chatbot inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar chatbot: {e}")
    # Continua mesmo com erro para não quebrar o servidor
    chatbot = None

# Rotas da API
@app.route('/health')
def health():
    """Health check para o Render"""
    return jsonify({"status": "ok", "message": "Servidor funcionando"}), 200

@app.route('/')
def index():
    # Gera timestamp baseado na última modificação do CSS para cache busting
    css_path = os.path.join(os.path.dirname(__file__), 'static', 'css', 'style.css')
    try:
        css_mtime = int(os.path.getmtime(css_path))
    except:
        css_mtime = int(time.time())
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
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    baby_name = data.get('baby_name', '').strip()
    
    if not name or not email or not password:
        return jsonify({"erro": "Todos os campos obrigatórios devem ser preenchidos"}), 400
    
    if len(password) < 6:
        return jsonify({"erro": "A senha deve ter no mínimo 6 caracteres"}), 400
    
    # Validação básica de email
    if '@' not in email or '.' not in email.split('@')[1]:
        return jsonify({"erro": "Email inválido"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifica se email já existe
    cursor.execute('SELECT id, email_verified FROM users WHERE email = ?', (email,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        if existing[1] == 1:
            return jsonify({"erro": "Este email já está cadastrado e verificado"}), 400
        else:
            return jsonify({"erro": "Este email já está cadastrado. Verifique seu email ou use 'Esqueci minha senha'"}), 400
    
    # Hash da senha - salva como string base64 para preservar bytes
    password_hash_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password_hash = base64.b64encode(password_hash_bytes).decode('utf-8')
    
    # Gera token de verificação
    verification_token = generate_token()
    
    # Insere usuário
    try:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, baby_name, email_verified, email_verification_token)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, password_hash, baby_name if baby_name else None, 0, verification_token))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        # Envia email de verificação
        try:
            send_verification_email(email, name, verification_token)
            mensagem = "Cadastro realizado! Verifique seu email para ativar sua conta. 💕"
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            mensagem = "Cadastro realizado! (Email de verificação não pôde ser enviado, mas você pode fazer login) 💕"
        
        return jsonify({
            "sucesso": True, 
            "mensagem": mensagem,
            "user_id": user_id,
            "verification_sent": True
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

        if not email or not password:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        # Log detalhado para debug
        print(f"[LOGIN] Tentativa de login - Email: {email}, Password length: {len(password)}")

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
                print(f"[LOGIN DEBUG] Verificação de senha: {'✅ CORRETA' if password_correct else '❌ INCORRETA'}")
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
        print(f"[LOGIN] Tentativa de login: {email}, email_verified: {email_verified}")
        
        # Verifica se email foi verificado
        # PERMITE login para contas antigas (criadas antes da verificação obrigatória)
        # Mas ainda mostra aviso se não verificado
        if email_verified == 0:
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
            result = login_user(user, remember=True)
            print(f"[LOGIN] Usuário logado: {user_name}, ID: {user_id}, Sessão criada: {result}")
        except Exception as e:
            print(f"[LOGIN] Erro ao fazer login_user: {e}")
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
    
    # Reenvia email
    try:
        send_verification_email(email, name, token)
        return jsonify({
            "sucesso": True,
            "mensagem": f"Email de verificação reenviado para {email}! Verifique sua caixa de entrada (e spam)."
        }), 200
    except Exception as e:
        print(f"Erro ao reenviar email: {e}")
        return jsonify({
            "sucesso": False,
            "erro": "Não foi possível reenviar o email. Tente novamente mais tarde."
        }), 500

@app.route('/api/verify-email', methods=['GET'])
def api_verify_email():
    """Verifica email através do token"""
    token = request.args.get('token', '')
    
    if not token:
        return jsonify({"erro": "Token não fornecido"}), 400
    
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
        return jsonify({"erro": "Token inválido"}), 400
    
    user_id, email, name = user
    
    # Marca email como verificado
    cursor.execute('''
        UPDATE users 
        SET email_verified = 1, email_verification_token = NULL
        WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    
    # Retorna HTML de sucesso
    try:
        return render_template('email_verified.html', name=name)
    except:
        # Fallback se template não existir
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="3;url=/">
            <title>Email Verificado</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #f8f4f0 0%, #e8d5d1 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                }}
                .container {{
                    background: white;
                    padding: 2rem;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #8b5a5a; }}
                p {{ color: #9a7a6a; margin: 1rem 0; }}
                a {{ 
                    color: #f4a6a6; 
                    text-decoration: none;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✅ Email Verificado com Sucesso! 💕</h1>
                <p>Olá {name}! Seu email foi verificado.</p>
                <p>Você será redirecionado para o login em 3 segundos...</p>
                <p><a href="/">Clique aqui se não for redirecionado</a></p>
            </div>
        </body>
        </html>
        '''

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
        "openai_disponivel": client is not None
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
    print("OpenAI disponível:", "Sim" if client else "Não")
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
    print("\n⚠️ IMPORTANTE:")
    print("   - Celular e computador devem estar na MESMA rede WiFi")
    print("   - Se não funcionar, verifique o firewall do Windows")
    print("="*50)
    
    app.run(debug=False, host='0.0.0.0', port=port)

