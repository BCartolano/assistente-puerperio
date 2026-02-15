#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic Models para validação de requisições e respostas
Purpose: Garantir tipos corretos e validação rigorosa
"""

from typing import Optional, List, Literal, Dict
from pydantic import BaseModel, Field, model_validator


class SearchRequest(BaseModel):
    """Modelo de requisição de busca de facilidades"""
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude (opcional se state/city informados)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude (opcional se state/city informados)")
    radius_km: float = Field(default=10.0, ge=0.1, le=25.0, description="Raio de busca em km (máx. 25km)")
    filter_type: Literal["ALL", "SUS", "PRIVATE", "EMERGENCY_ONLY", "MATERNITY"] = Field(
        default="ALL",
        description="Tipo de filtro: ALL, SUS, PRIVATE, EMERGENCY_ONLY, MATERNITY"
    )
    is_emergency: bool = Field(
        default=False,
        description="Se True, ignora filtros de convênio e retorna unidades mais próximas"
    )
    search_mode: Literal["emergency", "basic", "all"] = Field(
        default="all",
        description="Modo de busca: 'emergency' (apenas Hospitais/UPAs), 'basic' (apenas UBS/Postos), 'all' (todos)"
    )
    state: Optional[str] = Field(
        default=None,
        description="Filtro por UF (ex: SP, RJ). Brasil todo: 27 estados + DF. Ignora raio quando informado."
    )
    city: Optional[str] = Field(
        default=None,
        description="Filtro por município (ex: São José dos Campos). 5570 municípios. Ignora raio quando informado."
    )
    
    @model_validator(mode='after')
    def require_coords_or_region(self):
        """Exige lat/lon OU (state e/ou city). Busca por estado/município dispensa geolocalização."""
        has_region = bool((self.state or '').strip() or (self.city or '').strip())
        if has_region:
            return self
        if self.latitude is None or self.longitude is None:
            raise ValueError('Informe latitude e longitude ou filtro por estado/município (state/city).')
        return self


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
    display_name: Optional[str] = Field(None, description="Nome formatado para exibição (título principal: Tipo + Bairro)")
    display_subtitle: Optional[str] = Field(None, description="Subtítulo (nome de pessoa/homenagem, ex: 'Dr. José da Cruz')")
    type: Literal["HOSPITAL", "UPA", "UBS", "CONSULTÓRIO", "SAMU", "OUTROS"] = Field(..., description="Tipo de unidade")
    tags: FacilityTags = Field(..., description="Tags da facilidade")
    badges: List[str] = Field(..., description="Badges visuais (ex: ['ACEITA SUS', 'MATERNIDADE'])")
    isVaccinationPoint: bool = Field(default=False, description="Flag indicando se é ponto de vacinação (UBS/Posto)")
    isHospital: bool = Field(default=False, description="Flag indicando se é hospital (Geral ou Especializado)")
    isSamuBase: bool = Field(default=False, description="Flag indicando se é base do SAMU (apenas administrativo)")
    address: Optional[str] = Field(None, description="Endereço completo")
    city: Optional[str] = Field(None, description="Cidade")
    state: Optional[str] = Field(None, description="Estado (UF)")
    distance_km: float = Field(..., ge=0, description="Distância em km")
    distance_type: Literal["linear", "route"] = Field(
        default="linear",
        description="Tipo de distância: 'linear' (linha reta/Haversine) ou 'route' (malha viária)"
    )
    lat: Optional[float] = Field(None, description="Latitude")
    long: Optional[float] = Field(None, description="Longitude")
    google_search_term: str = Field(..., description="Termo para busca no Google Maps")
    warning_message: Optional[str] = Field(
        None,
        description="Mensagem de aviso (ex: 'Apenas estabilização, não realiza parto')"
    )
    phone: Optional[str] = Field(None, description="Telefone oficial do CNES (NU_TELEFONE do CSV)")
    cnpj: Optional[str] = Field(None, description="CNPJ oficial do estabelecimento")
    management: Optional[str] = Field(None, description="Gestão: MUNICIPAL, ESTADUAL, FEDERAL, PRIVADO, DUPLA")
    natureza_juridica: Optional[str] = Field(None, description="Natureza jurídica (CO_NATUREZA_JUR do CSV)")
    priority_score: Optional[int] = Field(None, description="Score de prioridade para ordenação (debug)")
    data_validation: Optional[Dict] = Field(None, description="FASE 3: Validação de completude dos dados críticos")


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
