#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas da API de Busca de Facilidades
Purpose: Endpoints FastAPI para busca de hospitais/UPAs/UBS
"""

import logging
from typing import Dict
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from .models import SearchRequest, SearchResponse, SearchMeta, FacilityResult
from ..services.facility_service import FacilityService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["facilities"])

# Instância do serviço (pode ser injetada via dependency injection)
facility_service = FacilityService()

# Aviso legal obrigatório (UX Expert + PM)
LEGAL_DISCLAIMER = (
    "⚠️ Aviso de Emergência: Em caso de risco imediato à vida da mãe ou do bebê "
    "(sangramento intenso, perda de consciência, convulsão), dirija-se ao Pronto Socorro "
    "mais próximo, seja ele público ou privado. A Lei Federal obriga o atendimento de "
    "emergência para estabilização, independente de convênio ou capacidade de pagamento. "
    "Não aguarde validação do aplicativo em situações críticas."
)


@router.post("/facilities/search", response_model=SearchResponse)
async def search_facilities(request: SearchRequest):
    """
    Busca facilidades de saúde puerperal
    
    **Regras de Negócio:**
    - Se `is_emergency=true`: Ignora filtros de convênio, retorna unidades mais próximas
    - Se `filter_type=MATERNITY`: Apenas hospitais com maternidade
    - Se `filter_type=SUS`: Apenas unidades que atendem SUS
    - Se `filter_type=PRIVATE`: Apenas unidades privadas
    - Se `filter_type=EMERGENCY_ONLY`: Apenas UPAs
    
    **Aviso Legal:** 
    Sempre incluído na resposta (Lei 11.634/2008)
    """
    try:
        # Buscar facilidades
        results, data_source_date, is_cache_fallback = facility_service.search_facilities(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_km=request.radius_km,
            filter_type=request.filter_type,
            is_emergency=request.is_emergency
        )
        
        # Formatar aviso de cache (se aplicável)
        if is_cache_fallback and data_source_date:
            additional_warning = (
                f"\n\n⚠️ Dados baseados no registro oficial de {data_source_date}. "
                "API CNES está offline. Confirme informações por telefone."
            )
            legal_disclaimer = LEGAL_DISCLAIMER + additional_warning
        else:
            legal_disclaimer = LEGAL_DISCLAIMER
        
        # Construir resposta
        response = SearchResponse(
            meta=SearchMeta(
                legal_disclaimer=legal_disclaimer,
                total_results=len(results),
                data_source_date=data_source_date,
                is_cache_fallback=is_cache_fallback
            ),
            results=[FacilityResult(**result) for result in results]
        )
        
        return response
        
    except FileNotFoundError as e:
        logger.error(f"❌ Banco de dados não encontrado: {e}")
        raise HTTPException(
            status_code=503,
            detail=(
                "Serviço temporariamente indisponível. "
                "Banco de dados CNES não foi inicializado. "
                "Contate o administrador do sistema."
            )
        )
    except Exception as e:
        logger.error(f"❌ Erro ao buscar facilidades: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=(
                "Erro interno do servidor ao processar busca. "
                "Por favor, tente novamente. Se o problema persistir, contate o suporte."
            )
        )


@router.get("/facilities/health")
async def health_check():
    """Health check do serviço de facilidades"""
    try:
        # Tentar conectar ao banco
        conn = facility_service._get_connection()
        conn.close()
        
        return {
            "status": "healthy",
            "service": "facilities_search",
            "database": "connected"
        }
    except Exception as e:
        logger.warning(f"⚠️ Health check falhou: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "facilities_search",
                "database": "disconnected",
                "error": str(e)
            }
        )


