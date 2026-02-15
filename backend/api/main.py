#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor FastAPI - API de Busca de Facilidades de Saúde Puerperal
Purpose: Expor dados CNES via API RESTful com validação rigorosa
Author: Dev Agent (baseado em health_data_audit rules)
"""

import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar router DEPOIS de configurar logging
try:
    from .routes import router
    logger.info("✅ Router de facilities importado com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro ao importar router: {e}")
    router = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento de ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando API de Busca de Facilidades Puerperais...")
    logger.info("📊 Base de dados: CNES (Cache Híbrido)")
    logger.info("✅ API pronta para receber requisições")
    yield
    # Shutdown
    logger.info("🛑 Encerrando API...")


# Criar aplicação FastAPI
app = FastAPI(
    title="API de Busca de Facilidades Puerperais",
    description=(
        "API RESTful para busca de hospitais, UPAs e UBS "
        "com validação rigorosa baseada em dados oficiais do CNES/DataSUS. "
        "Implementa Cache Híbrido para resiliência e validação dupla "
        "(Google Maps + CNES) conforme arquitetura definida."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS usando ALLOW_ORIGINS do env
try:
    from backend.utils.env import ALLOW_ORIGINS
    _origins = [o.strip() for o in (ALLOW_ORIGINS or "*").split(",") if o.strip()] or ["*"]
except ImportError:
    _origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Métodos explícitos
    allow_headers=["*"],  # Permite todos os headers
    expose_headers=["*"],  # Expõe todos os headers na resposta
)

# Registrar rotas do facilities (DEVE vir ANTES dos endpoints dummy)
if router:
    app.include_router(router)
    logger.info("✅ Router de facilities registrado com sucesso")
else:
    logger.warning("⚠️ Router de facilities não foi importado - endpoints /api/v1/facilities não estarão disponíveis")

# Registrar rotas do chatbot (opcional)
try:
    from backend.chat.router_fastapi import router as chat_router
    app.include_router(chat_router)
    logger.info("✅ Router de chat registrado com sucesso")
except Exception as e:
    logger.warning("⚠️ Router de chat indisponível: %s", e)

# Endpoints dummy para compatibilidade com sistema legado (sem prefixo /api/v1)
# Estes endpoints são MOCK PURO - NÃO ACESSAM BANCO DE DADOS
@app.get("/api/vaccination/status")
async def dummy_vaccination_status():
    """
    Endpoint dummy para /api/vaccination/status - Evita erro 500
    MOCK PURO - NÃO ACESSA BANCO DE DADOS
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "Endpoint temporário - serviço de vacinação não disponível",
            "vaccines": [
                {"name": "BCG", "status": "taken", "date": "2023-01-01"},
                {"name": "Hepatite B", "status": "pending", "date": "2023-02-01"}
            ],
            "data": []
        }
    )


@app.get("/api/baby_profile")
@app.post("/api/baby_profile")
async def dummy_baby_profile():
    """
    Endpoint dummy para /api/baby_profile - Evita erro 500
    MOCK PURO - NÃO ACESSA BANCO DE DADOS
    """
    return JSONResponse(
        status_code=200,
        content={
            "exists": False,
            "id": 1,
            "name": "Bebê Puerpério",
            "birth_date": "2023-01-01",
            "age_months": 2,
            "message": "Endpoint temporário - serviço de perfil de bebê não disponível"
        }
    )


# Endpoint raiz REMOVIDO - O Flask serve o HTML na rota /
# Se precisar de um endpoint raiz para a API, use /api ou /api/v1
# @app.get("/")
# async def root():
#     """Endpoint raiz"""
#     return {
#         "service": "API de Busca de Facilidades Puerperais",
#         "version": "1.0.0",
#         "status": "operational",
#         "documentation": "/docs",
#         "health_check": "/api/v1/facilities/health"
#     }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global de exceções - evita crash do app"""
    logger.error(f"❌ Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "message": (
                "Ocorreu um erro inesperado. "
                "Por favor, tente novamente. "
                "Se o problema persistir, contate o suporte."
            ),
            "detail": str(exc) if os.getenv("DEBUG", "False").lower() == "true" else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "5000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Iniciando servidor FastAPI em http://{host}:{port}")
    logger.info(f"📚 Documentação disponível em http://{host}:{port}/docs")
    
    uvicorn.run(
        "backend.api.main:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload em desenvolvimento
        log_level="info"
    )
