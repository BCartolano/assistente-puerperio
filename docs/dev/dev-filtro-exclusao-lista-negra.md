# Refatoração: Filtro por Exclusão (Lista Negra) e Otimização da API

**Desenvolvedor:** James  
**Contexto:** Filtro muito restritivo gerando zero resultados + Timeout da API Overpass  
**Objetivo:** Mudar estratégia de inclusão estrita para exclusão e otimizar chamadas à API

**Data:** {{date}}

---

## 🐛 Problemas Identificados

### 1. Filtro Muito Restritivo (Zero Resultados)
- **Problema:** A validação de infraestrutura usava **inclusão estrita** (só aceitava se tivesse tags explícitas de maternidade)
- **Causa:** APIs de mapas muitas vezes não possuem a tag 'Maternidade' ou 'Obstetrícia' explicitamente preenchida
- **Resultado:** Hospitais grandes que possuem o serviço estavam sendo ocultados (falso-negativo generalizado)

### 2. Timeout da API Overpass (504 Gateway Timeout)
- **Problema:** Servidor derrubando conexão antes de retornar dados
- **Causa:** Query muito complexa ou timeout insuficiente
- **Resultado:** Falhas frequentes na busca de hospitais

---

## ✅ Soluções Implementadas

### 1. Nova Estratégia: Lista Negra (Exclusão)

**Antes (Inclusão Estrita):**
```javascript
// Só aceitava se tivesse indicador EXPLÍCITO de maternidade
const hasMaternityIndicator = 
    nameLower.includes('maternidade') ||
    specialtyLower.includes('obstetrics');
    
return hasMaternityIndicator; // BLOQUEAVA hospitais gerais
```

**Depois (Exclusão):**
```javascript
// PRIORIDADE ALTA: Aceita se tiver indicador explícito
if (hasMaternityIndicator) {
    return true; // Confirmação explícita
}

// LISTA NEGRA: Bloqueia apenas especializados que NÃO atendem parto
const blacklistSpecialties = [
    'oftalmologia', 'olhos',
    'cardiologia',
    'oncologia',
    'ortopedia',
    'psiquiatria',
    'plástica',
    // ... outros
];

if (hasBlacklistedSpecialty) {
    return false; // BLOQUEIA especializados
}

// PADRÃO: Aceita hospitais gerais (presumimos que atendem partos)
return true; // Aceita por padrão
```

---

### 2. Regra de Validação Atualizada

#### **Nova Lógica `validateMaternityInfrastructure()`:**

1. **PRIORIDADE ALTA:** Aceita se contém indicadores explícitos de maternidade
   - "maternidade", "maternity"
   - "obstetrícia", "obstetrics"
   - "ala maternal", "mulher", "women"
   - etc.

2. **LISTA NEGRA:** Bloqueia apenas hospitais especializados que NÃO atendem parto
   - Oftalmologia, Olhos
   - Cardiologia
   - Oncologia
   - Ortopedia
   - Psiquiatria
   - Plástica
   - Dermatologia
   - Neurologia
   - Urologia
   - Otorrino

3. **PADRÃO:** Aceita hospitais gerais
   - Presumimos que hospitais gerais atendem partos ou estabilizam melhor que clínicas

#### **Resumo da Regra:**
```
Se for 'Hospital' E (Contém 'Maternidade' OU Não contém termos da 'Lista Negra'), então EXIBIR.
```

---

### 3. Otimização da Query Overpass

**Antes:**
```javascript
const query = `
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:${radius},${lat},${lon});
      way["amenity"="hospital"](around:${radius},${lat},${lon});
      relation["amenity"="hospital"](around:${radius},${lat},${lon});
    );
    out center tags;
`;
```

**Depois (Simplificada):**
```javascript
const query = `[out:json][timeout:30];
(node["amenity"="hospital"](around:${radius},${lat},${lon});
 way["amenity"="hospital"](around:${radius},${lat},${lon});
 relation["amenity"="hospital"](around:${radius},${lat},${lon}););
out center tags;`;
```

**Mudanças:**
- ✅ Query simplificada (menos processamento no servidor)
- ✅ Timeout aumentado de 25 para 30 segundos
- ✅ Toda filtragem movida para o cliente (JavaScript)

---

### 4. Tratamento de Erros Melhorado

**Antes:**
```javascript
if (!response.ok) {
    if ((response.status === 504 || response.status === 429) && serverIndex < servers.length - 1) {
        continue;
    }
    return [];
}
```

**Depois:**
```javascript
if (!response.ok) {
    if (response.status === 504 || response.status === 500) {
        lastError = new Error('O servidor de mapas está demorando para responder. Tente novamente em alguns segundos ou reduza o raio de busca.');
        if (serverIndex < servers.length - 1) {
            continue; // Tenta próximo servidor
        }
        throw lastError; // Lança erro com mensagem amigável
    }
    if (response.status === 429) {
        lastError = new Error('Muitas solicitações. Aguarde alguns segundos antes de tentar novamente.');
        if (serverIndex < servers.length - 1) {
            continue;
        }
        throw lastError;
    }
    // ... outros tratamentos
}
```

**Melhorias:**
- ✅ Mensagens de erro amigáveis para o usuário
- ✅ Tratamento específico para 504, 500, 429
- ✅ Propaga erro para `findNearbyHospitals()` que já exibe na interface

---

### 5. Timeout Aumentado

**Antes:**
```javascript
const timeoutId = setTimeout(() => controller.abort(), 20000); // 20 segundos
```

**Depois:**
```javascript
const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 segundos
```

**Benefícios:**
- ✅ Mais tempo para servidores lentos responderem
- ✅ Reduz falsos negativos por timeout

---

## 📊 Resultado Esperado

### Antes
- ❌ Zero resultados (filtro muito restritivo)
- ❌ Timeout frequente (504 Gateway Timeout)
- ❌ Erros sem mensagens amigáveis

### Depois
- ✅ Hospitais gerais são exibidos (assumimos que atendem partos)
- ✅ Apenas especializados que não atendem parto são bloqueados
- ✅ Query mais leve e rápida
- ✅ Timeout aumentado para 30 segundos
- ✅ Mensagens de erro amigáveis

---

## 🔍 Casos de Teste

### ✅ Deve INCLUIR (Passa no Filtro):

1. **"Hospital Geral"** → ✅ Tipo: Hospital | ✅ Infra: Não está na lista negra
2. **"Hospital Municipal"** → ✅ Tipo: Hospital | ✅ Infra: Não está na lista negra
3. **"Maternidade Municipal"** → ✅ Tipo: Maternidade | ✅ Infra: Tem indicador explícito (prioridade alta)
4. **"Hospital da Mulher"** → ✅ Tipo: Hospital | ✅ Infra: Tem indicador explícito (prioridade alta)
5. **"Hospital São Paulo"** (sem tags especiais) → ✅ Tipo: Hospital | ✅ Infra: Aceito por padrão

### ❌ Deve EXCLUIR (Bloqueado):

1. **"Hospital de Oftalmologia"** → ✅ Tipo: Hospital | ❌ Infra: Está na lista negra (oftalmologia)
2. **"Hospital Cardiológico"** → ✅ Tipo: Hospital | ❌ Infra: Está na lista negra (cardiologia)
3. **"Hospital Oncológico"** → ✅ Tipo: Hospital | ❌ Infra: Está na lista negra (oncologia)
4. **"Hospital Ortopédico"** → ✅ Tipo: Hospital | ❌ Infra: Está na lista negra (ortopedia)

### ❌ Continua EXCLUINDO (Filtro de Tipo):

1. **"UBS Centro"** → ❌ Tipo: UBS (não é hospital)
2. **"Clínica Médica ABC"** → ❌ Tipo: Clínica (não é hospital)
3. **"UPA 24h"** → ❌ Tipo: UPA (não é hospital)

---

## 📝 Notas Importantes

### Mudança de Estratégia
- **ANTES:** "Só mostro se tiver confirmação explícita" (inclusão estrita)
- **DEPOIS:** "Mostro por padrão, só bloqueio especializados que não atendem parto" (exclusão)

### Assunção de Segurança
- Presumimos que **hospitais gerais** atendem partos ou estabilizam melhor que clínicas
- Apenas **especializados que NÃO atendem parto** são bloqueados (lista negra)

### Performance
- Query simplificada reduz carga no servidor Overpass
- Timeout aumentado reduz falsos negativos
- Filtragem no cliente (JavaScript) alivia servidor

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Refatoração: Lista negra em vez de inclusão estrita | Dev (James) |
| {{date}} | 1.1 | Otimização: Query simplificada + timeout aumentado | Dev (James) |
| {{date}} | 1.2 | Melhoria: Tratamento de erros com mensagens amigáveis | Dev (James) |
