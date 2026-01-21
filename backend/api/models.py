#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic Models para validação de requisições e respostas
Purpose: Garantir tipos corretos e validação rigorosa
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator


class SearchRequest(BaseModel):
    """Modelo de requisição de busca de facilidades"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude da localização da mãe")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude da localização da mãe")
    radius_km: float = Field(default=10.0, ge=0.1, le=50.0, description="Raio de busca em km")
    filter_type: Literal["ALL", "SUS", "PRIVATE", "EMERGENCY_ONLY", "MATERNITY"] = Field(
        default="ALL",
        description="Tipo de filtro: ALL, SUS, PRIVATE, EMERGENCY_ONLY, MATERNITY"
    )
    is_emergency: bool = Field(
        default=False,
        description="Se True, ignora filtros de convênio e retorna unidades mais próximas"
    )
    
    @validator('latitude', 'longitude')
    def validate_coordinates(cls, v):
        """Valida coordenadas geográficas"""
        if not isinstance(v, (int, float)):
            raise ValueError('Coordenadas devem ser numéricas')
        return float(v)


class FacilityTags(BaseModel):
    """Tags da facilidade (SUS, Privado, Maternidade)"""
    sus: bool = Field(..., description="Atende pelo SUS")
    private: bool = Field(..., description="É privado")
    maternity: bool = Field(..., description="Tem maternidade")
    emergency_only: bool = Field(default=False, description="Apenas emergência (UPA)")


class FacilityResult(BaseModel):
    """Resultado individual de busca de facilidade"""
    id: str = Field(..., description="CNES ID")
    name: str = Field(..., description="Nome do hospital")
    fantasy_name: Optional[str] = Field(None, description="Nome fantasia")
    type: Literal["HOSPITAL", "UPA", "UBS"] = Field(..., description="Tipo de unidade")
    tags: FacilityTags = Field(..., description="Tags da facilidade")
    badges: List[str] = Field(..., description="Badges visuais (ex: ['ACEITA SUS', 'MATERNIDADE'])")
    address: Optional[str] = Field(None, description="Endereço completo")
    city: Optional[str] = Field(None, description="Cidade")
    state: Optional[str] = Field(None, description="Estado (UF)")
    distance_km: float = Field(..., ge=0, description="Distância em km")
    lat: Optional[float] = Field(None, description="Latitude")
    long: Optional[float] = Field(None, description="Longitude")
    google_search_term: str = Field(..., description="Termo para busca no Google Maps")
    warning_message: Optional[str] = Field(
        None,
        description="Mensagem de aviso (ex: 'Apenas estabilização, não realiza parto')"
    )
    phone: Optional[str] = Field(None, description="Telefone (se disponível)")
    cnpj: Optional[str] = Field(None, description="CNPJ (se disponível)")


class SearchMeta(BaseModel):
    """Metadados da resposta"""
    legal_disclaimer: str = Field(
        ...,
        description="Aviso legal obrigatório (Lei 11.634/2008)"
    )
    total_results: int = Field(..., description="Total de resultados encontrados")
    data_source_date: Optional[str] = Field(
        None,
        description="Data da base CNES usada (para aviso de possível desatualização)"
    )
    is_cache_fallback: bool = Field(
        default=False,
        description="Se True, dados vêm de cache local (API CNES pode estar offline)"
    )


class SearchResponse(BaseModel):
    """Resposta completa da busca"""
    meta: SearchMeta = Field(..., description="Metadados da resposta")
    results: List[FacilityResult] = Field(..., description="Lista de resultados")
    
    class Config:
        schema_extra = {
            "example": {
                "meta": {
                    "legal_disclaimer": "⚠️ Aviso: Em caso de emergência médica (sangramento, desmaio), dirija-se ao PS mais próximo independente de convênio. Lei 11.634/2008.",
                    "total_results": 3,
                    "data_source_date": "2025-01-15",
                    "is_cache_fallback": False
                },
                "results": [
                    {
                        "id": "cnes_1234567",
                        "name": "Hospital Maternidade Exemplo",
                        "type": "HOSPITAL",
                        "tags": {
                            "sus": True,
                            "private": False,
                            "maternity": True,
                            "emergency_only": False
                        },
                        "badges": ["ACEITA SUS", "MATERNIDADE"],
                        "address": "Rua Exemplo, 123",
                        "city": "São Paulo",
                        "state": "SP",
                        "distance_km": 2.5,
                        "google_search_term": "Hospital Maternidade Exemplo Emergency",
                        "warning_message": None
                    }
                ]
            }
        }
