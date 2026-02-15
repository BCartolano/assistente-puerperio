# Modo Automático - Validação de Hospitais

## Status: ✅ ATIVO

O sistema está rodando em **modo automático** analisando e corrigindo hospitais de maternidade continuamente.

---

## Script Principal

**`auto_validate_hospitals.py`** - Roda em segundo plano validando hospitais automaticamente.

### Características:

1. **Funciona sem internet** - Análise local por padrões de nome
2. **Tratamento de erros** - Continua mesmo se houver problemas
3. **Processamento em lotes** - Processa 50 hospitais por vez
4. **Estado persistente** - Salva progresso e retoma de onde parou
5. **Logs detalhados** - Registra todas as ações

---

## Como Usar

### Iniciar modo automático:
```bash
python backend/scripts/auto_validate_hospitals.py
```

### Parar:
- Pressione `Ctrl+C` no terminal

### Ver logs:
```bash
# Ver último estado
cat backend/scripts/auto_validation_state.json

# Ver histórico de ações
cat backend/scripts/auto_validation_log.json
```

---

## O que o Script Faz

1. **Analisa hospitais** marcados como `has_maternity=1`
2. **Identifica padrões** que indicam não-maternidade:
   - Saúde mental (PSIQUIATRIA, CVV, DEPENDENCIA)
   - Especialidades (ORTOPEDIA, OFTALMOLOGIA, etc.)
   - Clínicas específicas
   - COVID-19
3. **Remove automaticamente** hospitais com padrões claros de não-maternidade
4. **Registra pendentes** que requerem validação manual
5. **Salva progresso** continuamente

---

## Arquivos Gerados

- `auto_validation_state.json` - Estado atual (último CNES processado, contadores)
- `auto_validation_log.json` - Histórico de ações (últimos 1000 registros)

---

## Segurança

- ✅ **Não remove hospitais sem padrão claro** - Apenas registra como "pendente"
- ✅ **Preserva "Hospital das Clínicas"** - Hospitais gerais são mantidos
- ✅ **Logs completos** - Todas as ações são registradas
- ✅ **Estado persistente** - Pode parar e retomar sem perder progresso

---

## Status Atual

O script está rodando em **segundo plano** e continuará processando hospitais automaticamente.

**Última atualização:** Verificar `auto_validation_state.json`
