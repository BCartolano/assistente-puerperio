import os
import json
import random
import difflib
from datetime import datetime
from flask import Flask, request, jsonify, render_template
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
BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "dados")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializa cliente OpenAI se a chave estiver disponível
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"AVISO: Erro ao inicializar cliente OpenAI: {e}")
        client = None

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
        """Busca resposta na base de conhecimento local"""
        pergunta_lower = pergunta.lower()
        melhor_match = None
        maior_similaridade = 0
        categoria = None
        
        for tema, conteudo in self.base.items():
            pergunta_base = conteudo["pergunta"].lower()
            similaridade = difflib.SequenceMatcher(None, pergunta_lower, pergunta_base).ratio()
            
            if similaridade > maior_similaridade:
                maior_similaridade = similaridade
                melhor_match = conteudo["resposta"]
                categoria = tema
        
        if maior_similaridade > 0.5:
            return melhor_match, categoria, maior_similaridade
        
        return None, None, 0
    
    def gerar_resposta_openai(self, pergunta, contexto=""):
        """Gera resposta usando OpenAI se disponível"""
        if not self.client:
            return None
        
        try:
            system_message = """Você é um assistente especializado em saúde materna e puerpério. 
            Forneça informações empáticas, acolhedoras e baseadas em evidências científicas.
            Sempre encoraje a busca por atendimento médico quando necessário.
            Use linguagem simples e acolhedora."""
            
            if contexto:
                system_message += f"\n\nContexto adicional: {contexto}"
            
            resposta = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": pergunta}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return resposta.choices[0].message.content
        except Exception as e:
            print(f"Erro ao chamar OpenAI: {e}")
            return None
    
    def chat(self, pergunta, user_id="default"):
        """Função principal do chatbot"""
        # Verifica alertas
        alertas_encontrados = self.verificar_alertas(pergunta)
        
        # Busca resposta local primeiro
        resposta_local, categoria, similaridade = self.buscar_resposta_local(pergunta)
        
        # Se encontrou resposta local com boa similaridade, usa ela
        if resposta_local and similaridade > 0.7:
            resposta_final = resposta_local
            fonte = "base_conhecimento"
        else:
            # Tenta OpenAI se disponível
            resposta_openai = self.gerar_resposta_openai(pergunta)
            if resposta_openai:
                resposta_final = resposta_openai
                fonte = "openai"
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

