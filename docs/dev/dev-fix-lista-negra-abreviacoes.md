# Correção: Lista Negra - Adição de Variações e Abreviações

**Desenvolvedor:** James  
**Contexto:** Bug crítico - falso positivo detectado  
**Problema:** "Hospital Orto" foi incorretamente validado como maternidade

**Data:** {{date}}

---

## 🐛 Bug Identificado

### Problema
O "Hospital Orto" foi validado incorretamente como maternidade quando deveria ser bloqueado pela lista negra.

### Causa
A lista negra filtrou "Ortopedia", mas falhou em pegar a **abreviação "Orto"** presente no nome fantasia do hospital.

### Impacto
- **Falso Positivo:** Hospitais especializados que não atendem parto aparecendo na lista
- **Risco de Segurança:** Gestantes podem ser direcionadas para locais sem infraestrutura adequada

---

## ✅ Correção Implementada

### Expansão da Lista Negra

Adicionadas variações, abreviações e termos sem acento para evitar falsos positivos:

#### **Ortopedia (EXPANDIDO):**
- ✅ `'orto'` ← **CRÍTICO: Adicionado para pegar abreviação**
- ✅ `'trauma'`
- ✅ `'traumatologia'`
- ✅ `'fraturas'`
- ✅ `'acidentados'`
- ✅ `'ortopedia'` (mantido)
- ✅ `'orthopedics'` (mantido)
- ✅ `'ortopédico'` (mantido)
- ✅ `'orthopedic'` (mantido)

#### **Cirurgia Plástica/Estética (EXPANDIDO):**
- ✅ `'plastica'` (sem acento)
- ✅ `'estetica'` (sem acento)
- ✅ `'lipo'`
- ✅ `'lipoaspiração'` / `'lipoaspiracao'`
- ✅ `'plástica'` (mantido)
- ✅ `'plastic'` (mantido)

#### **Day Hospital (NOVO):**
- ✅ `'day hospital'`
- ✅ `'day-hospital'`
- ✅ `'day'` (para pegar Day Hospital - geralmente cirurgias pequenas, não atende parto)

#### **Oftalmologia (EXPANDIDO):**
- ✅ `'oftalmo'` ← **Adicionado para pegar abreviação**
- ✅ `'oftalmologia'` (mantido)
- ✅ `'olhos'` (mantido)
- ✅ `'eyes'` (mantido)
- ✅ `'ocular'` (mantido)

#### **Cardiologia (EXPANDIDO):**
- ✅ `'cardio'` ← **Adicionado para pegar abreviação**
- ✅ `'coracao'` (sem cedilha) ← **Adicionado**
- ✅ `'coração'` (com cedilha) ← **Adicionado**
- ✅ `'cardiologia'` (mantido)
- ✅ `'cardíaco'` (mantido)
- ✅ `'cardiac'` (mantido)

#### **Urologia / Rim / Renal (EXPANDIDO):**
- ✅ `'rim'` ← **Adicionado**
- ✅ `'renal'` ← **Adicionado**
- ✅ `'nefrologia'` ← **Adicionado**
- ✅ `'urologia'` (mantido)
- ✅ `'urology'` (mantido)

---

## 🔍 Lógica de Verificação

### Case-Insensitive (Já Implementado)
A verificação já é case-insensitive (ignorar maiúsculas/minúsculas) através de:
```javascript
const nameLower = (hospitalName || '').toLowerCase();
const specialtyLower = (specialty || '').toLowerCase();
const healthcareLower = (healthcare || '').toLowerCase();
const healthcareSpeciality = (tags?.['healthcare:speciality'] || '').toLowerCase();
```

### Verificação de Substring
A verificação usa `includes()` que detecta substrings:
```javascript
blacklistSpecialties.some(term => nameLower.includes(term))
```

**Exemplos:**
- ✅ "Hospital Orto" → `nameLower = "hospital orto"` → `includes('orto')` → **TRUE** → **BLOQUEADO**
- ✅ "Hospital de Ortopedia" → `nameLower = "hospital de ortopedia"` → `includes('ortopedia')` → **TRUE** → **BLOQUEADO**
- ✅ "Hospital de Traumatologia" → `nameLower = "hospital de traumatologia"` → `includes('trauma')` → **TRUE** → **BLOQUEADO**

---

## ✅ Casos de Teste

### ❌ Deve BLOQUEAR (Lista Negra):

1. **"Hospital Orto"** → ✅ Bloqueado (contém "orto")
2. **"Hospital Ortopédico"** → ✅ Bloqueado (contém "ortopédico")
3. **"Hospital de Trauma"** → ✅ Bloqueado (contém "trauma")
4. **"Hospital de Fraturas"** → ✅ Bloqueado (contém "fraturas")
5. **"Hospital de Acidentados"** → ✅ Bloqueado (contém "acidentados")
6. **"Hospital de Plastica"** → ✅ Bloqueado (contém "plastica")
7. **"Hospital de Estetica"** → ✅ Bloqueado (contém "estetica")
8. **"Day Hospital"** → ✅ Bloqueado (contém "day")
9. **"Hospital Oftalmo"** → ✅ Bloqueado (contém "oftalmo")
10. **"Hospital de Rim"** → ✅ Bloqueado (contém "rim")
11. **"Hospital Renal"** → ✅ Bloqueado (contém "renal")
12. **"Hospital de Coracao"** → ✅ Bloqueado (contém "coracao")
13. **"Hospital Cardio"** → ✅ Bloqueado (contém "cardio")

### ✅ Deve ACEITAR (Passa na Lista Negra):

1. **"Hospital Geral"** → ✅ Aceito (não contém termos da lista negra)
2. **"Hospital Municipal"** → ✅ Aceito (não contém termos da lista negra)
3. **"Maternidade Municipal"** → ✅ Aceito (prioridade alta - tem indicador explícito)
4. **"Hospital da Mulher"** → ✅ Aceito (prioridade alta - tem indicador explícito)
5. **"Hospital São Paulo"** → ✅ Aceito (não contém termos da lista negra)

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Adição de variações e abreviações na lista negra | Dev (James) |
| {{date}} | 1.1 | Adição de termos: Orto, Trauma, Plastica, Estetica, Day, Oftalmo, Rim, Renal, Coracao, Cardio | Dev (James) |

---

## 📝 Notas Importantes

### Termos Adicionados
- **Variações:** `'orto'`, `'trauma'`, `'fraturas'`, `'acidentados'`
- **Sem acento:** `'plastica'`, `'estetica'`, `'coracao'`
- **Abreviações:** `'orto'`, `'oftalmo'`, `'cardio'`, `'lipo'`
- **Novos termos:** `'day'`, `'rim'`, `'renal'`

### Verificação
- ✅ Case-insensitive (já implementado)
- ✅ Detecta substrings (já implementado)
- ✅ Verifica nome, especialidade, tipo e tags OSM

### Segurança
- **CRÍTICO:** Esta correção previne que hospitais especializados que não atendem parto apareçam na lista
- **Prioridade:** Alta - relacionado à segurança do paciente
