import os
import json
import random
import difflib
import sqlite3
import bcrypt
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
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

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            baby_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
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
            system_message = """Você é uma assistente virtual especializada em saúde materna e puerpério, chamada Assistente Puerpério.

Seu papel é ser uma AMIGA ACOLHEDORA e EMPÁTICA que:
- Conversa de forma NATURAL e CONVERSACIONAL, como se fosse uma pessoa real
- Usa linguagem CALOROSA, CARINHOSA e ACONCHEGANTE
- Demonstra COMPREENSÃO e EMPATIA pelos sentimentos da mãe
- NUNCA soa robótica ou formal demais
- Fala como uma amiga que já passou por isso ou que entende profundamente
- Usa expressões como "querida", "amiga", "entendo você", "é normal sentir isso"
- SEMPRE valida os sentimentos da usuária primeiro
- Depois oferece informações e conselhos práticos
- Quando não souber algo, admite isso com carinho
- Sempre encoraja a busca por ajuda médica quando necessário

IMPORTANTE: Sua resposta deve soar como uma CONVERSA COM UMA AMIGA, não como um manual técnico!
Seja calorosa, empática e acolhedora SEMPRE."""
            
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
                max_tokens=800,  # Aumentado para respostas mais completas
                temperature=0.8  # Aumentado para respostas mais naturais
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

# Inicializa o chatbot
chatbot = ChatbotPuerperio()

# Rotas da API
@app.route('/')
def index():
    return render_template('index.html')

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
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifica se email já existe
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Este email já está cadastrado"}), 400
    
    # Hash da senha
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Insere usuário
    cursor.execute('''
        INSERT INTO users (name, email, password_hash, baby_name)
        VALUES (?, ?, ?, ?)
    ''', (name, email, password_hash, baby_name if baby_name else None))
    
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"sucesso": True, "mensagem": "Cadastro realizado com sucesso! 💕", "user_id": user_id}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        return jsonify({"erro": "Email ou senha incorretos"}), 401
    
    # Verifica senha
    if bcrypt.checkpw(password.encode('utf-8'), user_data[3].encode('utf-8')):
        user = User(user_data[0], user_data[1], user_data[2], user_data[4])
        login_user(user)
        return jsonify({
            "sucesso": True, 
            "mensagem": "Login realizado com sucesso! Bem-vinda de volta 💕",
            "user": {
                "id": user_data[0],
                "name": user_data[1],
                "email": user_data[2],
                "baby_name": user_data[4]
            }
        })
    else:
        return jsonify({"erro": "Email ou senha incorretos"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({"sucesso": True, "mensagem": "Logout realizado com sucesso"})

@app.route('/api/user', methods=['GET'])
@login_required
def api_user():
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "baby_name": current_user.baby_name
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
    
    # Insere a vacina
    cursor.execute('INSERT INTO vacinas_tomadas (user_id, tipo, vacina_nome) VALUES (?, ?, ?)',
                   (current_user.id, tipo, vacina_nome))
    conn.commit()
    vacina_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        "sucesso": True, 
        "mensagem": "Vacina marcada com sucesso! 💉✨",
        "vacina_id": vacina_id
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
    print("Acesse: http://localhost:5000")
    print("="*50)
    
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

