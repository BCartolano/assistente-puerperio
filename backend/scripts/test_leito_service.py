#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Serviço de Leitos
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.etl.leito_service import load_leito_reference, has_obstetr_leito, has_obstetr_service

print("="*70)
print("TESTE DO SERVIÇO DE LEITOS")
print("="*70)
print()

codes, descs = load_leito_reference()
print(f"[1] Códigos de leitos de obstetrícia: {codes}")
print(f"[2] Descrições de leitos de obstetrícia: {descs}")

print("\n[3] TESTES DE VALIDAÇÃO:")
print(f"   TP_LEITO='02' -> {has_obstetr_leito(tp_leito='02')}")
print(f"   DS_LEITO='OBSTETRICIA' -> {has_obstetr_leito(ds_leito='OBSTETRICIA')}")
print(f"   DS_LEITO='OBSTETRICIA CIRURGICA' -> {has_obstetr_leito(ds_leito='OBSTETRICIA CIRURGICA')}")
print(f"   CO_LEITO='02' -> {has_obstetr_leito(co_leito='02')}")

print("\n[4] TESTES DE SERVIÇOS:")
print(f"   CO_SERVICO='141' -> {has_obstetr_service('141')}")
print(f"   CO_SERVICO='065,141,066' -> {has_obstetr_service('065,141,066')}")
print(f"   CO_SERVICO='065,066' -> {has_obstetr_service('065,066')}")

print("\n[OK] Teste concluido!")
