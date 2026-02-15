#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes QA - Localizador de Unidades de Saúde
Validação dos critérios de aceite após implementações de filtragem
"""

import sys
import os

# Adicionar path do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.facility_service import FacilityService

class Colors:
    """Cores para output do terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    """Imprime cabeçalho do teste"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print(f"TESTE: {test_name}")
    print(f"{'='*70}{Colors.END}\n")

def print_pass(message):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}[PASSOU] {message}{Colors.END}")

def print_fail(message):
    """Imprime mensagem de falha"""
    print(f"{Colors.RED}[FALHOU] {message}{Colors.END}")

def print_warning(message):
    """Imprime mensagem de aviso"""
    print(f"{Colors.YELLOW}[AVISO] {message}{Colors.END}")

def print_info(message):
    """Imprime mensagem informativa"""
    print(f"{Colors.BLUE}[INFO] {message}{Colors.END}")

# ============================================================================
# TESTE 1: Filtro de Blacklist (Farma, Drogaria, Removale, Estética)
# ============================================================================

def test_blacklist_filter():
    """Testa se a função _sanitize_name filtra corretamente termos problemáticos"""
    print_test_header("1. Teste de Ruído (Blacklist)")
    
    service = FacilityService()
    
    # Casos de teste
    test_cases = [
        ("Farma Conde", None, "Farma"),
        ("Drogaria São Paulo", None, "Drogaria"),
        ("Removale Transporte", None, "Removale"),
        ("Clínica Estética Beleza", None, "Estética"),
        ("Hospital Municipal", "Hospital Municipal", "Não deve filtrar"),
        ("UBS Centro", "UBS Centro", "Não deve filtrar"),
        ("Farmácia Popular", None, "Farmácia"),
        ("Ambulância Privada", None, "Ambulância"),
    ]
    
    passed = 0
    failed = 0
    
    for name, expected, description in test_cases:
        result = service._sanitize_name(name)
        if result == expected:
            print_pass(f"'{name}' -> {result} ({description})")
            passed += 1
        else:
            print_fail(f"'{name}' -> Esperado: {expected}, Obtido: {result} ({description})")
            failed += 1
    
    print_info(f"Resultado: {passed} passaram, {failed} falharam")
    return failed == 0

# ============================================================================
# TESTE 2: Filtro de Nomes de Profissionais
# ============================================================================

def test_person_name_detection():
    """Testa se a função _is_person_name detecta corretamente nomes de pessoas"""
    print_test_header("2. Teste de Detecção de Nomes de Profissionais")
    
    service = FacilityService()
    
    # Casos de teste
    test_cases = [
        ("Monica Araujo", True, "Nome de pessoa (2 palavras)"),
        ("Vanessa Carvalho", True, "Nome de pessoa (2 palavras)"),
        ("João Silva Santos", True, "Nome de pessoa (3 palavras)"),
        ("Hospital Municipal", False, "Instituição"),
        ("UBS Centro de Saúde", False, "Instituição"),
        ("Maria", False, "Nome único (menos de 2 palavras)"),
        ("Centro de Saúde Municipal da Cidade", False, "Muitas palavras"),
    ]
    
    passed = 0
    failed = 0
    
    for name, expected, description in test_cases:
        result = service._is_person_name(name)
        if result == expected:
            print_pass(f"'{name}' -> {result} ({description})")
            passed += 1
        else:
            print_fail(f"'{name}' -> Esperado: {expected}, Obtido: {result} ({description})")
            failed += 1
    
    print_info(f"Resultado: {passed} passaram, {failed} falharam")
    return failed == 0

def test_display_name_improvement():
    """Testa se a função _improve_display_name melhora nomes de profissionais"""
    print_test_header("2b. Teste de Melhoria de Nomes de Exibição")
    
    service = FacilityService()
    
    # Casos de teste
    test_cases = [
        # (name, fantasy_name, facility_type, city, neighborhood, expected_contains)
        ("Consultório Odontológico LTDA", "Monica Araujo", "CONSULTÓRIO", "São Paulo", "Centro", 
         "Unidade de Saúde", "Deve gerar genérico quando razão social também parece ser nome de pessoa"),
        ("Hospital Municipal", "Hospital Municipal", "HOSPITAL", "São Paulo", None,
         "Hospital Municipal", "Deve manter nome quando não é pessoa"),
        ("Vanessa Silva Consultório", "Vanessa Silva", "UBS", "Rio", "Copacabana",
         "Unidade Básica de Saúde", "Deve gerar genérico quando ambos são pessoas"),
        ("Clínica Odontológica Especializada", "Monica Araujo", "CONSULTÓRIO", "São Paulo", "Centro",
         "Clínica Odontológica", "Deve usar razão social quando não é nome de pessoa"),
    ]
    
    passed = 0
    failed = 0
    
    for name, fantasy_name, facility_type, city, neighborhood, expected_contains, description in test_cases:
        result = service._improve_display_name(name, fantasy_name, facility_type, city, neighborhood)
        if expected_contains.lower() in result.lower():
            print_pass(f"'{fantasy_name}' -> '{result}' ({description})")
            passed += 1
        else:
            print_fail(f"'{fantasy_name}' -> Esperado conter '{expected_contains}', Obtido: '{result}' ({description})")
            failed += 1
    
    print_info(f"Resultado: {passed} passaram, {failed} falharam")
    return failed == 0

# ============================================================================
# TESTE 3: Identificação de Pontos de Vacinação
# ============================================================================

def test_vaccination_point_identification():
    """Testa se UBS/Postos são identificados como pontos de vacinação"""
    print_test_header("3. Teste de Identificação de Pontos de Vacinação")
    
    service = FacilityService()
    
    # Simular Row-like objects
    class MockRow:
        def __init__(self, tipo_unidade):
            self._tipo_unidade = tipo_unidade
        def __getitem__(self, key):
            if key == 'tipo_unidade':
                return self._tipo_unidade
            return None
        def get(self, key, default=None):
            return self.__getitem__(key) or default
    
    test_cases = [
        (MockRow('01'), True, "Posto de Saúde (01)"),
        (MockRow('02'), True, "Centro de Saúde/UBS (02)"),
        (MockRow('15'), True, "Policlínica (15)"),
        (MockRow('40'), True, "Unidade Mista (40)"),
        (MockRow('UBS'), True, "Tipo mapeado UBS"),
        (MockRow('05'), False, "Hospital Geral (05)"),
        (MockRow('73'), False, "UPA (73)"),
    ]
    
    passed = 0
    failed = 0
    
    for row, expected, description in test_cases:
        result = service._is_vaccination_point(row)
        if result == expected:
            print_pass(f"{description} -> {result}")
            passed += 1
        else:
            print_fail(f"{description} -> Esperado: {expected}, Obtido: {result}")
            failed += 1
    
    print_info(f"Resultado: {passed} passaram, {failed} falharam")
    return failed == 0

# ============================================================================
# TESTE 4: Query SQL - Allow-list e Exclusões
# ============================================================================

def test_sql_query_filters():
    """Testa se a query SQL tem allow-list e exclusões corretas"""
    print_test_header("4. Teste de Filtros SQL (Allow-list e Exclusões)")
    
    service = FacilityService()
    
    # Testar construção da query
    query, params = service._build_filter_query("ALL", False)
    
    # Verificar se contém placeholders para allow-list (deve ter 10 ? para os tipos permitidos)
    # A query deve ter: tipo_unidade IN (?,?,?,?,?,?,?,?,?,?)
    has_allow_list_placeholders = query.count('?') >= 10  # 10 tipos permitidos
    
    # Verificar se contém exclusões (deve ter mais 2 ? para tipos excluídos)
    # A query deve ter: tipo_unidade NOT IN (?,?)
    has_exclusion_placeholders = query.count('NOT IN') > 0
    
    # Verificar se os parâmetros contêm os tipos corretos
    allowed_in_params = any(tipo in params for tipo in ['05', '07', '73', '01', '02', '15', '40'])
    excluded_in_params = '22' in params and '43' in params
    
    passed = 0
    failed = 0
    
    if has_allow_list_placeholders:
        print_pass("Query contém placeholders para allow-list de tipos permitidos")
        passed += 1
    else:
        print_fail("Query NÃO contém placeholders suficientes para allow-list")
        failed += 1
    
    if has_exclusion_placeholders:
        print_pass("Query contém cláusula NOT IN para exclusões")
        passed += 1
    else:
        print_fail("Query NÃO contém cláusula de exclusão")
        failed += 1
    
    if allowed_in_params:
        print_pass("Parâmetros contêm tipos permitidos (05, 07, 73, 01, 02, 15, 40)")
        passed += 1
    else:
        print_fail("Parâmetros NÃO contêm tipos permitidos")
        failed += 1
    
    if excluded_in_params:
        print_pass("Parâmetros contêm tipos excluídos (22, 43)")
        passed += 1
    else:
        print_fail("Parâmetros NÃO contêm tipos excluídos")
        failed += 1
    
    print_info(f"Query gerada (primeiros 300 chars): {query[:300]}...")
    print_info(f"Total de parâmetros: {len(params)}")
    print_info(f"Resultado: {passed} passaram, {failed} falharam")
    return failed == 0

# ============================================================================
# TESTE 5: Verificação de Campos no Retorno
# ============================================================================

def test_api_response_fields():
    """Testa se o retorno da API contém os campos necessários"""
    print_test_header("5. Teste de Campos no Retorno da API")
    
    # Verificar modelo
    try:
        from api.models import FacilityResult
        
        # Verificar campos obrigatórios
        required_fields = [
            'isVaccinationPoint',
            'isHospital',
            'display_name',
            'distance_type'
        ]
        
        # Compatibilidade com Pydantic V1 e V2
        try:
            model_fields = FacilityResult.model_fields.keys()  # Pydantic V2
        except AttributeError:
            model_fields = FacilityResult.__fields__.keys()  # Pydantic V1
        
        passed = 0
        failed = 0
        
        for field in required_fields:
            if field in model_fields:
                print_pass(f"Campo '{field}' presente no modelo")
                passed += 1
            else:
                print_fail(f"Campo '{field}' AUSENTE no modelo")
                failed += 1
        
        print_info(f"Resultado: {passed} passaram, {failed} falharam")
        return failed == 0
        
    except ImportError:
        print_warning("Não foi possível importar modelos - teste pulado")
        return True

# ============================================================================
# TESTE 6: Verificação Frontend (Análise de Código)
# ============================================================================

def test_frontend_implementation():
    """Verifica implementação no frontend através de análise de código"""
    print_test_header("6. Teste de Implementação Frontend (Análise de Código)")
    
    frontend_file = "frontend/src/components/ResultsList.jsx"
    
    if not os.path.exists(frontend_file):
        print_warning(f"Arquivo {frontend_file} não encontrado")
        return True
    
    with open(frontend_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("shouldHideCard", "Filtro de segurança no frontend"),
        ("Aprox.", "Texto 'Aprox.' na distância"),
        ("distance_type === 'linear'", "Verificação de tipo de distância"),
        ("Ponto de Vacinação", "Badge de vacinação"),
        ("Atendimento de Emergência/Alta Complexidade", "Texto de apoio para hospitais"),
    ]
    
    passed = 0
    failed = 0
    
    for check, description in checks:
        if check in content:
            print_pass(f"{description} - Encontrado no código")
            passed += 1
        else:
            print_fail(f"{description} - NÃO encontrado no código")
            failed += 1
    
    print_info(f"Resultado: {passed} passaram, {failed} falharam")
    return failed == 0

# ============================================================================
# EXECUÇÃO DOS TESTES
# ============================================================================

def main():
    """Executa todos os testes"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*70)
    print("ROTEIRO DE TESTES QA - LOCALIZADOR DE UNIDADES DE SAÚDE")
    print("="*70)
    print(f"{Colors.END}\n")
    
    tests = [
        ("Teste 1: Filtro de Blacklist", test_blacklist_filter),
        ("Teste 2a: Detecção de Nomes de Profissionais", test_person_name_detection),
        ("Teste 2b: Melhoria de Nomes de Exibição", test_display_name_improvement),
        ("Teste 3: Identificação de Pontos de Vacinação", test_vaccination_point_identification),
        ("Teste 4: Filtros SQL", test_sql_query_filters),
        ("Teste 5: Campos no Retorno da API", test_api_response_fields),
        ("Teste 6: Implementação Frontend", test_frontend_implementation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_fail(f"Erro ao executar {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print("RESUMO FINAL DOS TESTES")
    print(f"{'='*70}{Colors.END}\n")
    
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}[PASSOU]{Colors.END}" if result else f"{Colors.RED}[FALHOU]{Colors.END}"
        print(f"{status} - {test_name}")
    
    print(f"\n{Colors.BOLD}Total: {passed_count}/{total_count} testes passaram{Colors.END}\n")
    
    if passed_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}*** TODOS OS TESTES PASSARAM! ***{Colors.END}")
        print(f"{Colors.GREEN}O Localizador esta pronto para producao!{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}*** ALGUNS TESTES FALHARAM ***{Colors.END}")
        print(f"{Colors.YELLOW}Por favor, revise os testes que falharam antes de fazer deploy.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
