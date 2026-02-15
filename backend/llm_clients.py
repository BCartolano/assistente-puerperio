# -*- coding: utf-8 -*-
"""
Clientes de IA (Groq/Gemini/OpenAI). Só inicializa se houver chave no env.
Assume que load_dotenv() já foi chamado no entrypoint (ex.: app.py).
"""
import os
import logging

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

groq_client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("[llm] Groq inicializado")
    except Exception as e:
        logger.warning("[llm] Groq indisponível: %s", e)
else:
    logger.info("[llm] Groq ausente (ok)")

gemini_client = None
gemini_model = None
genai = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_client = genai
        gemini_model = genai.GenerativeModel("gemini-pro")
        logger.info("[llm] Gemini inicializado")
    except Exception as e:
        logger.info("[llm] Gemini ausente (ok): %s", e)
        genai = None
else:
    logger.info("[llm] Gemini ausente (ok)")

openai_client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("[llm] OpenAI inicializado")
    except Exception as e:
        logger.info("[llm] OpenAI ausente (ok): %s", e)
else:
    logger.info("[llm] OpenAI ausente (ok)")

# Flags de disponibilidade (client criado com sucesso)
GROQ_AVAILABLE = groq_client is not None
GEMINI_AVAILABLE = gemini_model is not None and gemini_client is not None
OPENAI_AVAILABLE = openai_client is not None
