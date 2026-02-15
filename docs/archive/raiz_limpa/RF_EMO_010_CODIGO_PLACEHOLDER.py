# ============================================================================
# RF.EMO.010 - CÓDIGO PLACEHOLDER PARA IMPLEMENTAÇÃO
# Triagem de Isolamento e Sobrecarga (Burnout Materno)
# ============================================================================

# ============================================================================
# 1. FUNÇÃO GENÉRICA DE TRIAGEM EMOCIONAL (REFATORADA)
# ============================================================================

def detectar_triagem_emocional(perfil_id, mensagem, user_id=None):
    """
    Função genérica de triagem emocional.
    Suporta múltiplos perfis emocionais (RF.EMO.009, RF.EMO.010, etc.)
    
    Args:
        perfil_id: ID do perfil ("mae_ansiosa", "mae_isolada_sobrecarga")
        mensagem: Texto da mensagem do usuário
        user_id: ID do usuário (opcional)
    
    Returns:
        {
            "detectado": True/False,
            "nivel": "leve"/"moderada"/"alta"/None,
            "perfil": perfil_id,
            "resposta": "...",
            "recursos": {...},
            "indicadores_encontrados": int,
            "palavras_encontradas": [...],
            "frases_encontradas": [...]
        }
    """
    if not TRIAGEM_EMOCIONAL or "perfis_emocionais" not in TRIAGEM_EMOCIONAL:
        return {"detectado": False}
    
    perfil = TRIAGEM_EMOCIONAL.get("perfis_emocionais", {}).get(perfil_id, {})
    if not perfil:
        return {"detectado": False}
    
    padroes = perfil.get("padroes_deteccao", {})
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
    
    # Se não tem contexto relevante, pode ser não relacionado à maternidade
    # Mas ainda assim detectamos se houver muitos indicadores
    if not tem_contexto and indicadores_encontrados < 3:
        return {"detectado": False}
    
    # Se não encontrou indicadores suficientes
    if indicadores_encontrados == 0:
        return {"detectado": False}
    
    # Determina nível baseado nos indicadores
    # Adapta-se à estrutura de níveis do perfil (ansiedade tem 3, isolamento tem 2)
    nivel = None
    
    # Para ansiedade (3 níveis)
    if perfil_id == "mae_ansiosa":
        if indicadores_encontrados >= 5 or len(frases_encontradas) >= 2:
            nivel = "alta"
        elif indicadores_encontrados >= 3 or len(frases_encontradas) >= 1:
            nivel = "moderada"
        elif indicadores_encontrados >= 1:
            nivel = "leve"
    
    # Para isolamento/sobrecarga (2 níveis)
    elif perfil_id == "mae_isolada_sobrecarga":
        if indicadores_encontrados >= 4 or len(frases_encontradas) >= 2:
            nivel = "moderada"
        elif indicadores_encontrados >= 1:
            nivel = "leve"
    
    # Busca resposta apropriada
    # Adapta-se à estrutura de níveis do perfil
    if perfil_id == "mae_ansiosa":
        niveis_data = perfil.get("niveis_ansiedade", {})
    else:
        niveis_data = perfil.get("niveis", {})
    
    resposta_data = niveis_data.get(nivel, {})
    respostas_disponiveis = resposta_data.get("respostas", [])
    
    # Seleciona resposta (usa contador se user_id fornecido)
    resposta = ""
    if respostas_disponiveis:
        if user_id:
            # Usa contador para variar respostas
            contador = CONTADOR_ALERTA.get(user_id, 0)
            indice = contador % len(respostas_disponiveis)
            resposta = respostas_disponiveis[indice]
        else:
            resposta = respostas_disponiveis[0]
    else:
        # Resposta padrão se não houver específica
        resposta = (
            f"Entendo que você esteja passando por um momento difícil. 💛\n\n"
            f"Se precisar de apoio emocional imediato:\n"
            f"- **CVV (188)** - disponível 24 horas, gratuito e sigiloso\n"
            f"- **Disque Saúde (136)** - orientação em saúde"
        )
    
    # Busca recursos de apoio
    recursos_apoio = perfil.get("recursos_apoio", {})
    telefones = recursos_apoio.get("telefones", [])
    orientacoes = recursos_apoio.get("orientacoes", [])
    
    logger.info(f"[TRIAGEM] ✅ {perfil_id} detectado - Nível: {nivel}, Indicadores: {indicadores_encontrados}")
    
    return {
        "detectado": True,
        "nivel": nivel,
        "perfil": perfil_id,
        "resposta": resposta,
        "recursos": {
            "telefones": telefones,
            "orientacoes": orientacoes
        },
        "indicadores_encontrados": indicadores_encontrados,
        "palavras_encontradas": palavras_encontradas[:5],  # Limita a 5 para não sobrecarregar
        "frases_encontradas": frases_encontradas
    }


# ============================================================================
# 2. FUNÇÕES WRAPPER (MANTÉM COMPATIBILIDADE)
# ============================================================================

def detectar_triagem_ansiedade(mensagem, user_id=None):
    """
    RF.EMO.009 - Wrapper para manter compatibilidade.
    Detecta sinais de ansiedade em mães gestantes ou no puerpério.
    """
    return detectar_triagem_emocional("mae_ansiosa", mensagem, user_id)


def detectar_triagem_isolamento_sobrecarga(mensagem, user_id=None):
    """
    RF.EMO.010 - Detecta sinais de isolamento e sobrecarga (burnout materno).
    Integrado com BMad Core para triagem emocional.
    
    Retorna:
    {
        "detectado": True/False,
        "nivel": "leve"/"moderada"/None,
        "perfil": "mae_isolada_sobrecarga"/None,
        "resposta": "resposta personalizada",
        "recursos": [lista de recursos de apoio]
    }
    """
    return detectar_triagem_emocional("mae_isolada_sobrecarga", mensagem, user_id)


# ============================================================================
# 3. INTEGRAÇÃO NO FLUXO DO CHATBOT (Método chat())
# ============================================================================

# INSERIR APÓS A DETECÇÃO DE ANSIEDADE (RF.EMO.009), ANTES DE "Detecta se e saudacao"

# ========================================================================
# RF.EMO.010 - TRIAGEM EMOCIONAL: ISOLAMENTO E SOBRECARGA
# ========================================================================
logger.info(f"[TRIAGEM] Verificando triagem emocional - Isolamento/Sobrecarga")
triagem_isolamento = detectar_triagem_isolamento_sobrecarga(pergunta, user_id=user_id)

if triagem_isolamento.get("detectado"):
    nivel_isolamento = triagem_isolamento.get("nivel")
    resposta_triagem = triagem_isolamento.get("resposta", "")
    recursos = triagem_isolamento.get("recursos", {})
    
    logger.info(f"[TRIAGEM] ✅ Isolamento/Sobrecarga detectado - Nível: {nivel_isolamento}")
    
    # Adiciona recursos de apoio à resposta se disponíveis
    resposta_final = resposta_triagem
    if recursos.get("telefones"):
        telefones_texto = "\n\n**Recursos de Apoio:**\n"
        for telefone in recursos["telefones"]:
            telefones_texto += f"- **{telefone.get('nome', '')}**: {telefone.get('numero', '')} - {telefone.get('descricao', '')}\n"
        resposta_final += telefones_texto
    
    # Nível moderado bloqueia resposta normal (prioridade alta)
    if nivel_isolamento == "moderada":
        return {
            "resposta": resposta_final,
            "fonte": "triagem_emocional",
            "alerta": True,
            "nivel": nivel_isolamento,
            "tipo": "isolamento_sobrecarga",
            "perfil": "mae_isolada_sobrecarga",
            "codigo_requisito": "RF.EMO.010"
        }
    elif nivel_isolamento == "leve":
        # Isolamento leve: será combinado com resposta normal
        logger.info(f"[TRIAGEM] Isolamento leve detectado - será combinado com resposta normal")


# ============================================================================
# 4. ATUALIZAÇÃO DA ROTA API
# ============================================================================

@app.route('/api/triagem-emocional', methods=['POST'])
def api_triagem_emocional():
    """
    API de Triagem Emocional - Suporta múltiplos perfis
    RF.EMO.009 (Ansiedade) e RF.EMO.010 (Isolamento/Sobrecarga)
    Integração com BMad Core
    """
    data = request.get_json()
    mensagem = data.get('mensagem', '')
    user_id = data.get('user_id', 'default')
    perfil = data.get('perfil', None)  # Novo: permite especificar perfil
    
    if not mensagem.strip():
        return jsonify({"erro": "Mensagem não pode estar vazia"}), 400
    
    logger.info(f"[TRIAGEM_API] Analisando mensagem - Perfil: {perfil or 'todos'}")
    
    # Se perfil especificado, verifica apenas esse
    if perfil:
        if perfil == "mae_ansiosa":
            resultado = detectar_triagem_ansiedade(mensagem, user_id)
            codigo = "RF.EMO.009"
        elif perfil == "mae_isolada_sobrecarga":
            resultado = detectar_triagem_isolamento_sobrecarga(mensagem, user_id)
            codigo = "RF.EMO.010"
        else:
            return jsonify({"erro": f"Perfil '{perfil}' não encontrado"}), 400
    else:
        # Verifica todos os perfis (prioridade: ansiedade > isolamento)
        resultado_ansiedade = detectar_triagem_ansiedade(mensagem, user_id)
        if resultado_ansiedade.get("detectado"):
            resultado = resultado_ansiedade
            codigo = "RF.EMO.009"
        else:
            resultado = detectar_triagem_isolamento_sobrecarga(mensagem, user_id)
            codigo = "RF.EMO.010" if resultado.get("detectado") else None
    
    return jsonify({
        "codigo_requisito": codigo,
        "integracao_bmad": True,
        **resultado
    })


# ============================================================================
# 5. EXEMPLOS DE TESTE
# ============================================================================

"""
EXEMPLOS DE MENSAGENS PARA TESTE:

ANSIEDADE LEVE:
- "Estou um pouco preocupada com o parto"
- "Tenho algumas dúvidas sobre os cuidados com o bebê"

ANSIEDADE MODERADA:
- "Estou muito ansiosa e não consigo dormir de preocupação"
- "Tenho medo de fazer algo errado com o bebê"

ANSIEDADE ALTA:
- "Estou tendo crises de ansiedade e não consigo relaxar"
- "Meu coração não para de bater forte, estou em pânico"

ISOLAMENTO/SOBRECARGA LEVE:
- "Estou muito cansada, ninguém me ajuda"
- "Me sinto sozinha às vezes"
- "Faço tudo sozinha e está difícil"

ISOLAMENTO/SOBRECARGA MODERADA:
- "Não aguento mais essa rotina, estou completamente esgotada"
- "Me sinto isolada de tudo, ninguém entende o que estou passando"
- "Estou em burnout, não tenho forças para continuar"
- "Fazer tudo sozinha está me matando"
"""

