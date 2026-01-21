# Função: Detecção Automática de Serviço Maternal

**Desenvolvedor:** James  
**Contexto:** Implementação de detecção automática de serviço maternal  
**Objetivo:** Criar função que detecta automaticamente se hospital possui serviço maternal

**Data:** {{date}}

---

## 📋 Visão Geral

### Requisitos
Criar função `detectarServicoMaternal(hospital)` que analise o objeto hospital e detecte automaticamente se possui serviço maternal, usando:
1. Análise de palavras-chave no nome/descrição
2. Verificação de tags/categorias (se disponíveis)
3. Lógica de fallback inteligente

### Lógica de Exibição (Nova Regra de Negócio)

#### Estados Possíveis
1. **Verificação Explícita (true):** Banco diz `true` → Mostra badge verde "Possui Ala Maternal"
2. **Verificação Implícita (Smart Check):** Banco é `null` → Faz detecção automática:
   - **Encontrou palavras-chave?** → Trata como COM Maternidade (badge verde)
   - **Não encontrou nada?** → Trata como Hospital Geral/PS (omite informação de maternidade, mostra apenas "Atendimento: Pronto Socorro / Geral")
3. **Certeza Absoluta (false):** Banco diz `false` → Mostra badge laranja "Não contém Ala Maternal"

---

## 💻 Implementação

### Função Principal: detectarServicoMaternal

```javascript
/**
 * Detecta automaticamente se hospital possui serviço maternal
 * Analisa nome, descrição, tags e categorias do hospital
 * 
 * @param {Object} hospital - Objeto do hospital
 * @param {string} hospital.name - Nome do hospital
 * @param {string} hospital.description - Descrição do hospital (opcional)
 * @param {Array} hospital.tags - Tags do hospital (opcional)
 * @param {Array} hospital.categories - Categorias do hospital (opcional)
 * @param {string} hospital.specialty - Especialidade do hospital (opcional)
 * @param {boolean} hospital.hasMaternityWard - Valor do banco (true/false/null)
 * 
 * @returns {Object} Resultado da detecção
 * @returns {boolean} resultado.hasMaternityWard - true/false/null (null = desconhecido)
 * @returns {string} resultado.confidence - 'explicit' | 'detected' | 'unknown'
 * @returns {Array} resultado.keywordsFound - Palavras-chave encontradas
 */
function detectarServicoMaternal(hospital) {
    // 1. VERIFICAÇÃO EXPLÍCITA: Se banco diz true, retorna true (confiança alta)
    if (hospital.hasMaternityWard === true) {
        return {
            hasMaternityWard: true,
            confidence: 'explicit',
            keywordsFound: [],
            reason: 'Confirmado no banco de dados'
        };
    }
    
    // 2. CERTEZA ABSOLUTA: Se banco diz false explicitamente, retorna false
    if (hospital.hasMaternityWard === false) {
        return {
            hasMaternityWard: false,
            confidence: 'explicit',
            keywordsFound: [],
            reason: 'Confirmado como não possui no banco de dados'
        };
    }
    
    // 3. SMART CHECK: Se banco é null/undefined, faz detecção automática
    const keywords = [
        'maternidade',
        'materno',
        'infantil',
        'obstetrícia',
        'obstetricia',
        'parto',
        'mulher',
        'women',
        'maternity',
        'obstetrics',
        'gynaecology',
        'gynecology',
        'ginecologia',
        'saúde da mulher',
        'healthcare:speciality=maternity',
        'healthcare:speciality=obstetrics'
    ];
    
    const keywordsFound = [];
    const searchTexts = [];
    
    // Coleta textos para análise
    if (hospital.name) searchTexts.push(hospital.name.toLowerCase());
    if (hospital.description) searchTexts.push(hospital.description.toLowerCase());
    if (hospital.specialty) searchTexts.push(hospital.specialty.toLowerCase());
    
    // Analisa cada texto
    searchTexts.forEach(text => {
        keywords.forEach(keyword => {
            if (text.includes(keyword.toLowerCase())) {
                if (!keywordsFound.includes(keyword)) {
                    keywordsFound.push(keyword);
                }
            }
        });
    });
    
    // Analisa tags (se disponíveis)
    if (hospital.tags && Array.isArray(hospital.tags)) {
        hospital.tags.forEach(tag => {
            const tagLower = tag.toLowerCase();
            keywords.forEach(keyword => {
                if (tagLower.includes(keyword.toLowerCase())) {
                    if (!keywordsFound.includes(keyword)) {
                        keywordsFound.push(keyword);
                    }
                }
            });
        });
    }
    
    // Analisa categorias (se disponíveis - ex: Google Places API)
    if (hospital.categories && Array.isArray(hospital.categories)) {
        hospital.categories.forEach(category => {
            const categoryLower = category.toLowerCase();
            if (categoryLower.includes('hospital especializado') || 
                categoryLower.includes('maternity') ||
                categoryLower.includes('obstetrics')) {
                keywordsFound.push('hospital especializado');
            }
        });
    }
    
    // Resultado do Smart Check
    if (keywordsFound.length > 0) {
        // Encontrou palavras-chave → Trata como COM Maternidade
        return {
            hasMaternityWard: true,
            confidence: 'detected',
            keywordsFound: keywordsFound,
            reason: `Detectado automaticamente: ${keywordsFound.join(', ')}`
        };
    } else {
        // Não encontrou nada → Trata como desconhecido (null)
        return {
            hasMaternityWard: null,
            confidence: 'unknown',
            keywordsFound: [],
            reason: 'Não foi possível detectar - tratar como Hospital Geral/PS'
        };
    }
}
```

---

### Função Auxiliar: Normalizar Resultado para Exibição

```javascript
/**
 * Normaliza resultado da detecção para uso na renderização
 * Converte resultado da detecção em valores booleanos/nulos padronizados
 * 
 * @param {Object} resultado - Resultado da função detectarServicoMaternal
 * @returns {boolean|null} Valor normalizado para renderização
 */
function normalizarResultadoDetecao(resultado) {
    // Retorna o valor hasMaternityWard diretamente
    // true = tem maternidade
    // false = não tem maternidade
    // null = desconhecido (não mostrar informação de maternidade)
    return resultado.hasMaternityWard;
}
```

---

### Função: Renderização Condicional do Badge (Atualizada)

```javascript
/**
 * Cria o badge de Ala Maternal baseado no resultado da detecção
 * Implementa a nova lógica de exibição:
 * - true (explícito/detectado) → Badge verde
 * - false (explícito) → Badge laranja "Não contém"
 * - null (desconhecido) → Omite badge de maternidade, mostra apenas "Atendimento: PS Geral"
 * 
 * @param {Object} hospital - Objeto do hospital
 * @param {Object} resultadoDetecao - Resultado da função detectarServicoMaternal (opcional)
 * @returns {string} HTML do badge ou mensagem de atendimento
 */
function criarBadgeAlaMaternal(hospital, resultadoDetecao = null) {
    // Se não foi passado resultado, faz detecção
    if (!resultadoDetecao) {
        resultadoDetecao = detectarServicoMaternal(hospital);
    }
    
    const hasMaternityWard = resultadoDetecao.hasMaternityWard;
    const confidence = resultadoDetecao.confidence;
    
    // Estado 1: VERIFICAÇÃO EXPLÍCITA ou DETECTADA (true)
    if (hasMaternityWard === true) {
        return `
            <div class="hospital-badge-maternity-positive">
                <i class="fas fa-baby"></i>
                <span>Possui Ala Maternal</span>
            </div>
        `;
    }
    
    // Estado 2: CERTEZA ABSOLUTA (false)
    if (hasMaternityWard === false) {
        return `
            <div class="hospital-badge-maternity-negative">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Não contém Ala Maternal</span>
            </div>
        `;
    }
    
    // Estado 3: DESCONHECIDO (null) → Omite badge de maternidade
    // Mostra apenas informação de atendimento geral
    return `
        <div class="hospital-badge-service-general">
            <i class="fas fa-hospital"></i>
            <span>Atendimento: Pronto Socorro / Geral</span>
        </div>
    `;
}
```

---

### Integração com Código Existente

#### Atualização da Função searchHospitalsNearby

```javascript
async searchHospitalsNearby(lat, lon, radius = 50000) {
    // ... código existente de busca ...
    
    // Para cada hospital encontrado, aplicar detecção automática
    hospitals.forEach(hospital => {
        // Se hasMaternityWard não está definido ou é null, faz detecção automática
        if (hospital.hasMaternityWard === null || hospital.hasMaternityWard === undefined) {
            const resultadoDetecao = detectarServicoMaternal({
                name: hospital.name,
                description: hospital.description,
                tags: hospital.tags,
                categories: hospital.categories,
                specialty: hospital.specialty,
                hasMaternityWard: null
            });
            
            // Atualiza hospital com resultado da detecção
            hospital.hasMaternityWard = resultadoDetecao.hasMaternityWard;
            hospital.detectionConfidence = resultadoDetecao.confidence;
            hospital.detectionKeywords = resultadoDetecao.keywordsFound;
        }
    });
    
    // ... resto do código ...
}
```

---

### CSS para Badge de Atendimento Geral (Novo)

```css
/* Badge de Atendimento Geral (quando não se sabe sobre maternidade) */
.hospital-badge-service-general {
    background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
    color: #FFFFFF;
    padding: 0.5rem 0.75rem;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 700;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(108, 117, 125, 0.3);
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.75rem;
}

.hospital-badge-service-general i {
    font-size: 1rem;
    color: #FFFFFF;
}
```

---

## 🧪 Testes

### Teste 1: Verificação Explícita (true)
```javascript
const hospital = {
    name: "Hospital Teste",
    hasMaternityWard: true
};

const resultado = detectarServicoMaternal(hospital);
// Esperado: { hasMaternityWard: true, confidence: 'explicit' }
```

### Teste 2: Verificação Explícita (false)
```javascript
const hospital = {
    name: "Hospital Teste",
    hasMaternityWard: false
};

const resultado = detectarServicoMaternal(hospital);
// Esperado: { hasMaternityWard: false, confidence: 'explicit' }
```

### Teste 3: Smart Check - Detectado (palavras-chave encontradas)
```javascript
const hospital = {
    name: "Hospital Maternidade São Paulo",
    hasMaternityWard: null
};

const resultado = detectarServicoMaternal(hospital);
// Esperado: { hasMaternityWard: true, confidence: 'detected', keywordsFound: ['maternidade'] }
```

### Teste 4: Smart Check - Não Detectado (null)
```javascript
const hospital = {
    name: "Hospital Geral",
    hasMaternityWard: null
};

const resultado = detectarServicoMaternal(hospital);
// Esperado: { hasMaternityWard: null, confidence: 'unknown', keywordsFound: [] }
```

### Teste 5: Análise de Tags
```javascript
const hospital = {
    name: "Hospital Central",
    tags: ['obstetrics', 'emergency'],
    hasMaternityWard: null
};

const resultado = detectarServicoMaternal(hospital);
// Esperado: { hasMaternityWard: true, confidence: 'detected', keywordsFound: ['obstetrics'] }
```

---

## 📝 Documentação de Uso

### Como Usar

```javascript
// Exemplo 1: Hospital com valor explícito no banco
const hospital1 = {
    name: "Hospital Exemplo",
    hasMaternityWard: true
};
const resultado1 = detectarServicoMaternal(hospital1);
// resultado1.hasMaternityWard = true (explícito)

// Exemplo 2: Hospital sem valor no banco (faz detecção automática)
const hospital2 = {
    name: "Hospital Maternidade da Mulher",
    hasMaternityWard: null
};
const resultado2 = detectarServicoMaternal(hospital2);
// resultado2.hasMaternityWard = true (detectado)
// resultado2.keywordsFound = ['maternidade', 'mulher']

// Exemplo 3: Hospital sem valor e sem palavras-chave
const hospital3 = {
    name: "Pronto Socorro Central",
    hasMaternityWard: null
};
const resultado3 = detectarServicoMaternal(hospital3);
// resultado3.hasMaternityWard = null (desconhecido)
```

---

## ✅ Checklist de Implementação

### Função de Detecção
- [x] Função `detectarServicoMaternal()` implementada
- [x] Verificação explícita (true/false) implementada
- [x] Smart Check (detecção automática) implementada
- [x] Análise de palavras-chave implementada
- [x] Análise de tags/categorias implementada
- [x] Retorno de confiança e keywords implementado

### Renderização
- [x] Função `criarBadgeAlaMaternal()` atualizada com nova lógica
- [x] Badge verde para true (explícito/detectado)
- [x] Badge laranja para false (explícito)
- [x] Badge cinza "Atendimento Geral" para null (desconhecido)
- [x] CSS do badge de atendimento geral criado

### Integração
- [ ] Função integrada em `searchHospitalsNearby()`
- [ ] Testes unitários criados
- [ ] Testes de integração executados

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial da função de detecção automática | Dev (James) |
