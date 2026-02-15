# -*- coding: utf-8 -*-
"""
Blueprint: Chat (IA, Histórico, Categorias, BASE_CONHECIMENTO, Triagem, Limpar memória).
Rotas: /api/chat, /api/historico/<user_id>, /api/categorias, /api/alertas, /api/telefones,
/api/guias, /api/guias/<guia_id>, /api/cuidados/gestacao, /api/cuidados/gestacao/<trimestre>,
/api/cuidados/puerperio, /api/cuidados/puerperio/<periodo>, /api/triagem-emocional,
/api/limpar-memoria-ia.
Usa current_app.chatbot, current_app.conversas, current_app.base_conhecimento, etc.
"""
import json
import sqlite3

from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_required, current_user

chat_bp = Blueprint("chat", __name__, url_prefix="")


def _db_path():
    return current_app.config.get("DB_PATH", "")


def _get_chatbot():
    return getattr(current_app, "chatbot", None)


def _get_conversas():
    return getattr(current_app, "conversas", {})


# ---------- /api/chat ----------
@chat_bp.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json()
    pergunta = (data.get("pergunta") or "").strip()

    if not current_user.is_authenticated:
        return jsonify({"erro": "Usuário não autenticado"}), 401

    user_id = str(current_user.id)
    user_id_from_request = data.get("user_id", "default")
    if user_id_from_request != "default" and str(user_id_from_request) != user_id:
        current_app.logger.warning(
            "[API_CHAT] Frontend tentou usar user_id diferente: %s, usando %s",
            user_id_from_request, user_id
        )

    if not pergunta:
        return jsonify({"erro": "Pergunta não pode estar vazia"}), 400

    get_user_context = getattr(current_app, "get_user_context", None)
    contexto_usuario = get_user_context(current_user.id) if get_user_context else None

    current_app.logger.info("[API_CHAT] Recebida pergunta: %s...", pergunta[:50])
    chatbot = _get_chatbot()
    if not chatbot:
        return jsonify({"erro": "Chatbot não disponível"}), 503
    current_app.logger.info("[API_CHAT] chatbot.openai_client disponível: %s", chatbot.openai_client is not None)
    if contexto_usuario:
        current_app.logger.info(
            "[API_CHAT] Contexto: Bebê=%s, Próxima vacina=%s",
            contexto_usuario.get("baby_name"), contexto_usuario.get("next_vaccine_name")
        )

    resposta = chatbot.chat(pergunta, user_id, contexto_usuario=contexto_usuario)
    current_app.logger.info("[API_CHAT] Resposta gerada - fonte: %s", resposta.get("fonte", "desconhecida"))
    return jsonify(resposta)


# ---------- /api/historico/<user_id> ----------
@chat_bp.route("/api/historico/<user_id>", methods=["GET", "DELETE"])
@login_required
def api_historico(user_id):
    if not current_user.is_authenticated or str(current_user.id) != str(user_id):
        current_app.logger.warning(
            "[HISTORICO] Tentativa de acesso não autorizado: user_id=%s, current_user.id=%s",
            user_id, getattr(current_user, "id", "N/A")
        )
        return jsonify({"erro": "Acesso negado. Você só pode acessar seu próprio histórico."}), 403

    conversas = _get_conversas()
    carregar_historico_db = getattr(current_app, "carregar_historico_db", None)
    if not carregar_historico_db:
        return jsonify({"erro": "Serviço indisponível"}), 503

    if request.method == "DELETE":
        try:
            if user_id in conversas:
                conversas[user_id] = []
            try:
                conn = sqlite3.connect(_db_path())
                conn.cursor().execute("DELETE FROM conversas WHERE user_id = ?", (str(user_id),))
                conn.commit()
                conn.close()
                current_app.logger.info("[DB] Histórico limpo do banco para user_id: %s", user_id)
            except Exception as db_err:
                current_app.logger.warning("[DB] Erro ao limpar histórico do banco: %s", db_err)
            return jsonify({"success": True, "message": "Histórico limpo com sucesso"})
        except Exception as e:
            current_app.logger.exception("[HISTORICO] Erro ao limpar")
            return jsonify({"success": False, "error": str(e)}), 500

    historico_memoria = conversas.get(user_id, [])
    historico_db = carregar_historico_db(str(user_id), limit=50)
    historico_completo = historico_db.copy()
    for msg_mem in historico_memoria:
        if not any(
            msg_db.get("pergunta") == msg_mem.get("pergunta") and msg_db.get("timestamp") == msg_mem.get("timestamp")
            for msg_db in historico_completo
        ):
            historico_completo.append(msg_mem)
    historico_completo.sort(key=lambda x: x.get("timestamp", ""))
    return jsonify(historico_completo)


# ---------- /api/categorias ----------
@chat_bp.route("/api/categorias")
def api_categorias():
    base = getattr(current_app, "base_conhecimento", None)
    if base is None:
        return jsonify([])
    return jsonify(list(base.keys()))


# ---------- /api/alertas ----------
@chat_bp.route("/api/alertas")
def api_alertas():
    alertas = getattr(current_app, "alertas", [])
    return jsonify(alertas)


# ---------- /api/telefones ----------
@chat_bp.route("/api/telefones")
def api_telefones():
    telefones = getattr(current_app, "telefones_uteis", [])
    return jsonify(telefones)


# ---------- /api/guias ----------
@chat_bp.route("/api/guias")
def api_guias():
    guias = getattr(current_app, "guias_praticos", [])
    return jsonify(guias)


@chat_bp.route("/api/guias/<guia_id>")
def api_guia_especifico(guia_id):
    guias = getattr(current_app, "guias_praticos", {})
    guia = guias.get(guia_id)
    if guia:
        return jsonify(guia)
    return jsonify({"erro": "Guia não encontrado"}), 404


# ---------- /api/cuidados/* ----------
@chat_bp.route("/api/cuidados/gestacao")
def api_cuidados_gestacao():
    dados = getattr(current_app, "cuidados_gestacao", {})
    return jsonify(dados)


@chat_bp.route("/api/cuidados/gestacao/<trimestre>")
def api_trimestre_especifico(trimestre):
    dados = getattr(current_app, "cuidados_gestacao", {})
    trimestre_data = dados.get(trimestre)
    if trimestre_data:
        return jsonify(trimestre_data)
    return jsonify({"erro": "Trimestre não encontrado"}), 404


@chat_bp.route("/api/cuidados/puerperio")
def api_cuidados_puerperio():
    dados = getattr(current_app, "cuidados_pos_parto", {})
    return jsonify(dados)


@chat_bp.route("/api/cuidados/puerperio/<periodo>")
def api_periodo_especifico(periodo):
    dados = getattr(current_app, "cuidados_pos_parto", {})
    periodo_data = dados.get(periodo)
    if periodo_data:
        return jsonify(periodo_data)
    return jsonify({"erro": "Período não encontrado"}), 404


# ---------- /api/triagem-emocional ----------
@chat_bp.route("/api/triagem-emocional", methods=["POST"])
def api_triagem_emocional():
    data = request.get_json()
    mensagem = (data.get("mensagem") or "").strip()
    user_id = data.get("user_id", "default")

    if not mensagem:
        return jsonify({"erro": "Mensagem não pode estar vazia"}), 400

    current_app.logger.info("[TRIAGEM_API] Analisando mensagem para triagem emocional")
    detectar = getattr(current_app, "detectar_triagem_ansiedade", None)
    if not detectar:
        return jsonify({"codigo_requisito": "RF.EMO.009", "integracao_bmad": True, "detectado": False}), 200

    resultado = detectar(mensagem, user_id=user_id)
    return jsonify({
        "codigo_requisito": "RF.EMO.009",
        "integracao_bmad": True,
        **resultado
    })


# ---------- /api/limpar-memoria-ia ----------
@chat_bp.route("/api/limpar-memoria-ia", methods=["POST"])
@login_required
def limpar_memoria_ia():
    try:
        user_id = session.get("user_id") or (current_user.id if current_user.is_authenticated else "default")

        conversas = _get_conversas()
        conversas_count = sum(len(conv) for conv in conversas.values())
        conversas.clear()

        info_apagadas = 0
        memoria_sophia_apagadas = 0
        try:
            conn = sqlite3.connect(_db_path())
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_info WHERE user_id = ?", (str(user_id),))
            info_apagadas = cursor.rowcount
            cursor.execute("DELETE FROM memoria_sophia WHERE user_id = ?", (str(user_id),))
            memoria_sophia_apagadas = cursor.rowcount
            conn.commit()
            conn.close()
        except Exception as e:
            current_app.logger.warning("[LIMPAR_MEMORIA] Erro ao limpar dados do banco: %s", e)

        chatbot = _get_chatbot()
        if chatbot and getattr(chatbot, "user_threads", None) and user_id in chatbot.user_threads:
            del chatbot.user_threads[user_id]
            current_app.logger.info("[LIMPAR_MEMORIA] Thread OpenAI removida para user_id %s", user_id)
        if chatbot and getattr(chatbot, "ultimas_respostas", None) and user_id in chatbot.ultimas_respostas:
            del chatbot.ultimas_respostas[user_id]

        total_apagado = conversas_count + info_apagadas + memoria_sophia_apagadas
        current_app.logger.info(
            "[LIMPAR_MEMORIA] Memória limpa para user_id %s: %s conversas, %s info, %s memoria_sophia",
            user_id, conversas_count, info_apagadas, memoria_sophia_apagadas
        )
        return jsonify({
            "sucesso": True,
            "mensagem": f"Memória da Sophia limpa com sucesso! {total_apagado} item(ns) removido(s): {conversas_count} conversas da memória, {info_apagadas} informações pessoais e {memoria_sophia_apagadas} dados memorizados (nomes, lugares, comidas).",
            "conversas_apagadas": conversas_count,
            "info_apagadas": info_apagadas,
            "memoria_sophia_apagadas": memoria_sophia_apagadas,
            "total_apagado": total_apagado
        }), 200
    except Exception as e:
        current_app.logger.exception("[LIMPAR_MEMORIA] Erro")
        return jsonify({"sucesso": False, "erro": str(e)}), 500
