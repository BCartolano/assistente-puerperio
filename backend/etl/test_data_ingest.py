#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Unitários para data_ingest.py
Purpose: Validar lógica de classificação puerperal rigorosa
"""

import unittest
import sys
import os

# Adicionar caminho do módulo
sys.path.insert(0, os.path.dirname(__file__))

from data_ingest import (
    has_obstetricia,
    is_upa,
    classify_maternity,
    clean_name,
    normalize_management,
    determine_is_sus,
    process_row
)


class TestDataIngest(unittest.TestCase):
    """Testes unitários para ingestão de dados CNES"""
    
    def test_has_obstetricia_true(self):
        """Testa detecção de Obstetrícia (Código 065)"""
        self.assertTrue(has_obstetricia('065'))
        self.assertTrue(has_obstetricia('064,065,066'))
        self.assertTrue(has_obstetricia('065;066;067'))
        self.assertTrue(has_obstetricia(' 065 '))
    
    def test_has_obstetricia_false(self):
        """Testa ausência de Obstetrícia"""
        self.assertFalse(has_obstetricia('064,066,067'))
        self.assertFalse(has_obstetricia(''))
        self.assertFalse(has_obstetricia(None))
    
    def test_is_upa_true(self):
        """Testa detecção de UPA"""
        self.assertTrue(is_upa('73'))
        self.assertTrue(is_upa('73001'))  # Pode ter mais dígitos
    
    def test_is_upa_false(self):
        """Testa não-UPA"""
        self.assertFalse(is_upa('05'))
        self.assertFalse(is_upa('07'))
        self.assertFalse(is_upa(''))
    
    def test_classify_maternity_upa_never_maternity(self):
        """TESTE CRÍTICO: UPA nunca deve ser marcada como maternidade"""
        row = {'CO_UNIDADE': '73', 'CO_SERVICO': '065,066'}  # Mesmo tendo código 065
        has_maternity, is_emergency_only = classify_maternity(row)
        
        self.assertFalse(has_maternity, "UPA não pode ter maternidade!")
        self.assertTrue(is_emergency_only, "UPA deve ser marcada como emergência apenas")
    
    def test_classify_maternity_hospital_with_obstetrics(self):
        """Testa hospital com Obstetrícia"""
        row = {'CO_UNIDADE': '05', 'CO_SERVICO': '065'}
        has_maternity, is_emergency_only = classify_maternity(row)
        
        self.assertTrue(has_maternity)
        self.assertFalse(is_emergency_only)
    
    def test_classify_maternity_hospital_without_obstetrics(self):
        """Testa hospital sem Obstetrícia"""
        row = {'CO_UNIDADE': '05', 'CO_SERVICO': '064,066'}
        has_maternity, is_emergency_only = classify_maternity(row)
        
        self.assertFalse(has_maternity)
        self.assertFalse(is_emergency_only)
    
    def test_classify_maternity_ambiguous_data(self):
        """REGRA DE OURO: Dados ambíguos = False"""
        row = {'CO_UNIDADE': '05', 'CO_SERVICO': ''}  # Serviço vazio
        has_maternity, is_emergency_only = classify_maternity(row)
        
        self.assertFalse(has_maternity, "Dados ambíguos devem resultar em False")
    
    def test_clean_name(self):
        """Testa higienização de nomes"""
        self.assertEqual(clean_name('HOSPITAL GERAL'), 'Hospital Geral')
        self.assertEqual(clean_name('hospital  geral  municipal'), 'Hospital Geral Municipal')
        self.assertEqual(clean_name(''), '')
    
    def test_normalize_management(self):
        """Testa normalização de gestão"""
        self.assertEqual(normalize_management('', 'MUNICIPAL'), 'MUNICIPAL')
        self.assertEqual(normalize_management('', 'PRIVADA'), 'PRIVADO')
        self.assertEqual(normalize_management('', 'ESTADUAL'), 'ESTADUAL')
    
    def test_determine_is_sus(self):
        """Testa determinação de SUS"""
        self.assertTrue(determine_is_sus('FILANTROPICA', 'S'))
        self.assertTrue(determine_is_sus('ADMINISTRACAO PUBLICA', ''))
        self.assertFalse(determine_is_sus('EMPRESARIAL', 'N'))
    
    def test_process_row_valid_hospital(self):
        """Testa processamento de linha válida"""
        row = {
            'CO_CNES': '1234567',
            'NO_FANTASIA': 'HOSPITAL MATERNO',
            'NO_RAZAO_SOCIAL': 'HOSPITAL MATERNO LTDA',
            'NO_MUNICIPIO': 'SAO PAULO',
            'CO_UF': 'SP',
            'CO_UNIDADE': '05',
            'CO_SERVICO': '065',
            'CO_NATUREZA_JUR': 'FILANTROPICA',
            'CO_SUS': 'S',
            'CO_GESTAO': 'MUNICIPAL'
        }
        
        result = process_row(row)
        self.assertIsNotNone(result)
        self.assertEqual(result['cnes_id'], '1234567')
        self.assertEqual(result['has_maternity'], 1)
        self.assertEqual(result['is_emergency_only'], 0)
    
    def test_process_row_missing_cnes_id(self):
        """Testa descarte quando falta CNES ID"""
        row = {
            'NO_FANTASIA': 'HOSPITAL TESTE'
        }
        
        result = process_row(row)
        self.assertIsNone(result, "Deve descartar se não tem CNES ID")


class TestCriticalRules(unittest.TestCase):
    """Testes para regras críticas de segurança"""
    
    def test_upa_cannot_be_maternity(self):
        """REGRA CRÍTICA: UPA não pode ser maternidade (mesmo com código 065)"""
        # Cenário que deve falhar se implementado incorretamente
        test_cases = [
            {'CO_UNIDADE': '73', 'CO_SERVICO': '065'},  # UPA com código 065
            {'CO_UNIDADE': '73001', 'CO_SERVICO': '065,066'},  # UPA com códigos
        ]
        
        for row in test_cases:
            has_maternity, is_emergency_only = classify_maternity(row)
            self.assertFalse(
                has_maternity,
                f"FALHA CRÍTICA: UPA marcada como maternidade! {row}"
            )
            self.assertTrue(
                is_emergency_only,
                f"UPA deve ser marcada como emergência apenas: {row}"
            )
    
    def test_ambiguous_data_always_false(self):
        """REGRA DE OURO: Dados ambíguos sempre resultam em False"""
        ambiguous_cases = [
            {'CO_UNIDADE': '05', 'CO_SERVICO': ''},  # Serviço vazio
            {'CO_UNIDADE': '05', 'CO_SERVICO': None},  # Serviço None
        ]
        
        for row in ambiguous_cases:
            has_maternity, _ = classify_maternity(row)
            self.assertFalse(
                has_maternity,
                f"Dados ambíguos devem resultar em False: {row}"
            )


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 EXECUTANDO TESTES UNITÁRIOS - Data Ingest")
    print("=" * 60)
    print()
    
    unittest.main(verbosity=2)
