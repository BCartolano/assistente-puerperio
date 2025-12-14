# 📊 RF.EMO.010 - Resumo Executivo

## 🎯 Objetivo
Expandir sistema de triagem emocional para detectar **Isolamento e Sobrecarga (Burnout Materno)**.

---

## 📋 Arquivos Criados

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `RF_EMO_010_PLANO_IMPLEMENTACAO.md` | Plano detalhado completo | ✅ Criado |
| `RF_EMO_010_CODIGO_PLACEHOLDER.py` | Código pronto para implementação | ✅ Criado |
| `RF_EMO_010_JSON_EXPANDIDO.json` | Estrutura JSON do novo perfil | ✅ Criado |
| `RF_EMO_010_RESUMO_EXECUTIVO.md` | Este resumo | ✅ Criado |

---

## 🔄 Mudanças Necessárias

### 1. **Arquivo JSON** (`dados/triagem_emocional.json`)
- ✅ Adicionar perfil `mae_isolada_sobrecarga`
- ✅ 40+ palavras-chave definidas
- ✅ 17 frases completas definidas
- ✅ 2 níveis (leve/moderada)
- ✅ Respostas personalizadas criadas

### 2. **Backend** (`backend/app.py`)

#### A. Refatorar Função (linhas ~1467-1604)
```python
# ANTES:
def detectar_triagem_ansiedade(mensagem, user_id=None):
    # Código específico para ansiedade
    ...

# DEPOIS:
def detectar_triagem_emocional(perfil_id, mensagem, user_id=None):
    # Código genérico para qualquer perfil
    ...

def detectar_triagem_ansiedade(mensagem, user_id=None):
    return detectar_triagem_emocional("mae_ansiosa", mensagem, user_id)

def detectar_triagem_isolamento_sobrecarga(mensagem, user_id=None):
    return detectar_triagem_emocional("mae_isolada_sobrecarga", mensagem, user_id)
```

#### B. Integrar no Fluxo (após linha ~2696)
```python
# Adicionar após detecção de ansiedade:
triagem_isolamento = detectar_triagem_isolamento_sobrecarga(pergunta, user_id)
if triagem_isolamento.get("detectado") and nivel == "moderada":
    return resposta_triagem  # Bloqueia resposta normal
```

#### C. Atualizar API (linha ~2992)
```python
# Adicionar suporte a parâmetro 'perfil' e verificar ambos os perfis
```

---

## 📊 Estrutura de Níveis

### RF.EMO.009 (Ansiedade) - 3 níveis
- **Leve** → Combina com resposta normal
- **Moderada** → Bloqueia resposta normal
- **Alta** → Bloqueia resposta normal

### RF.EMO.010 (Isolamento/Sobrecarga) - 2 níveis
- **Leve** → Combina com resposta normal
- **Moderada** → Bloqueia resposta normal

---

## 🔄 Ordem de Prioridade

```
1. RISCO SUICÍDIO (prioridade máxima)
   ↓
2. RF.EMO.009 - ANSIEDADE
   ├─ Alta/Moderada → Bloqueia
   └─ Leve → Combina
   ↓
3. RF.EMO.010 - ISOLAMENTO/SOBRECARGA
   ├─ Moderada → Bloqueia
   └─ Leve → Combina
   ↓
4. RESPOSTA NORMAL
```

---

## ✅ Checklist Rápido

- [ ] Expandir `triagem_emocional.json` com novo perfil
- [ ] Refatorar função para genérica
- [ ] Criar função wrapper `detectar_triagem_isolamento_sobrecarga()`
- [ ] Integrar no método `chat()` após ansiedade
- [ ] Atualizar rota API `/api/triagem-emocional`
- [ ] Testar detecção leve
- [ ] Testar detecção moderada
- [ ] Validar integração no fluxo

---

## 📝 Exemplos de Teste

**Isolamento Leve:**
- "Estou muito cansada, ninguém me ajuda"
- "Me sinto sozinha às vezes"

**Isolamento Moderada:**
- "Não aguento mais essa rotina, estou completamente esgotada"
- "Estou em burnout, não tenho forças para continuar"

---

## 🎯 Próximos Passos

1. **Revisar** `RF_EMO_010_PLANO_IMPLEMENTACAO.md` (plano completo)
2. **Copiar** código de `RF_EMO_010_CODIGO_PLACEHOLDER.py`
3. **Expandir** JSON usando `RF_EMO_010_JSON_EXPANDIDO.json` como referência
4. **Implementar** seguindo checklist
5. **Testar** com exemplos fornecidos

---

**Status:** 📝 Planejamento Completo - Pronto para Implementação  
**Data:** 2025-01-27

