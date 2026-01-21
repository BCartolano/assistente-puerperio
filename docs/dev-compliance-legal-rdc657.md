# Código: Atualização por Compliance Legal - RDC 657/2022

**Desenvolvedor:** James  
**Contexto:** Correção de Segurança Jurídica - Remoção de Inferência Automática  
**Objetivo:** Implementar código que atende RDC 657/2022 e Ato Médico

**Data:** {{date}}

---

## 🚨 CORREÇÃO CRÍTICA DE SEGURANÇA JURÍDICA

### Problema Identificado
A implementação atual da 'Prioridade 3 (Smart Check)' gera **risco de exercício ilegal da medicina** por inferência incorreta.

### Alteração Obrigatória
- ❌ **REMOVER:** Lista de palavras-chave
- ❌ **REMOVER:** Lógica de tentar adivinhar pelo nome
- ✅ **IMPLEMENTAR:** Estado neutro para `hasMaternity === null`

---

## 💻 Código Atualizado

### Função: getHospitalBadge (VERSÃO COMPLIANCE)

```javascript
/**
 * Retorna badge de maternidade baseado em dados oficiais do hospital
 * NÃO realiza inferência automática - apenas dados oficiais
 * 
 * @param {Object} hospital - Objeto do hospital
 * @param {boolean|null} hospital.hasMaternity - Valor do banco (true/false/null)
 * @returns {Object} Objeto com tipo e texto do badge
 * @returns {string} resultado.tipo - 'SUCCESS' | 'ERROR' | 'INFO'
 * @returns {string} resultado.texto - Texto do badge
 */
function getHospitalBadge(hospital) {
    const hasMaternity = hospital.hasMaternity; // true, false, ou null/undefined
    
    // PRIORIDADE 1: Dado Oficial (true) - CNES ou Validação Manual
    if (hasMaternity === true) {
        return {
            tipo: 'SUCCESS',
            texto: '✅ Ala Maternal Habilitada'
        };
    }
    
    // PRIORIDADE 2: Dado Oficial Negativo (false) - CNES ou Validação Manual
    if (hasMaternity === false) {
        return {
            tipo: 'ERROR',
            texto: '⚠️ Não possui Ala Maternal'
        };
    }
    
    // PRIORIDADE 3: Sem Informação (null) - Estado Neutro
    // NÃO tenta adivinhar - apenas informa que informação não está disponível
    return {
        tipo: 'INFO',
        texto: '📞 Atendimento Geral / Ligue 192'
    };
}
```

---

### Função: renderizarBadgeMaternal (VERSÃO COMPLIANCE)

```javascript
/**
 * Renderiza o HTML do badge de maternidade (versão compliance)
 * 
 * @param {Object} hospital - Objeto do hospital
 * @returns {string} HTML do badge
 */
function renderizarBadgeMaternal(hospital) {
    const badge = getHospitalBadge(hospital);
    
    // Define classe CSS baseada no tipo
    let classeBadge = '';
    switch (badge.tipo) {
        case 'SUCCESS':
            classeBadge = 'hospital-badge-maternity-success';
            break;
        case 'ERROR':
            classeBadge = 'hospital-badge-maternity-error';
            break;
        case 'INFO':
            classeBadge = 'hospital-badge-maternity-info';
            break;
        default:
            classeBadge = 'hospital-badge-maternity-info';
    }
    
    return `
        <div class="${classeBadge}">
            <span>${badge.texto}</span>
        </div>
    `;
}
```

---

### Função: renderizarDisclaimer (NOVA - Obrigatória)

```javascript
/**
 * Renderiza disclaimer obrigatório (compliance legal)
 * 
 * @returns {string} HTML do disclaimer
 */
function renderizarDisclaimer() {
    return `
        <div class="hospital-disclaimer" style="
            background: rgba(255, 183, 3, 0.1);
            border-left: 3px solid var(--sophia-warning);
            padding: 0.75rem;
            margin-bottom: 1rem;
            border-radius: 6px;
            font-size: 0.85rem;
            color: var(--sophia-text-secondary);
        ">
            <p style="margin: 0; line-height: 1.5;">
                <strong>⚠️ Importante:</strong> As informações exibidas são baseadas no cadastro oficial de estabelecimentos de saúde (CNES/DATASUS). 
                Em caso de emergência, ligue <strong>192 (SAMU)</strong>. 
                Para confirmação de serviços disponíveis, consulte diretamente o estabelecimento por telefone.
            </p>
        </div>
    `;
}
```

---

### Função: displayHospitals (VERSÃO COMPLIANCE)

```javascript
/**
 * Método displayHospitals atualizado (versão compliance)
 * Remove lógica de inferência automática
 */
displayHospitals(hospitals) {
    if (!this.hospitalsList) return;
    
    if (!hospitals || hospitals.length === 0) {
        this.showEmptyState();
        return;
    }
    
    // Filtra hospitais com informações completas
    const completeHospitals = hospitals.filter(h => {
        const hasName = (h.name || h.nome) && (h.name || h.nome).trim() !== '' && (h.name || h.nome) !== 'Hospital';
        const hasAddress = h.address && h.address.trim() !== '';
        const hasPhone = h.phone && h.phone.trim() !== '';
        return hasName && hasAddress && hasPhone;
    });
    
    // Ordena: hospitais com maternidade confirmada primeiro, depois por distância
    const sortedHospitals = [...completeHospitals].sort((a, b) => {
        // Apenas hasMaternity === true é considerado "com maternidade"
        const aHasMaternity = a.hasMaternity === true;
        const bHasMaternity = b.hasMaternity === true;
        
        // Prioridade 1: Hospitais com maternidade confirmada primeiro
        if (aHasMaternity && !bHasMaternity) return -1;
        if (!aHasMaternity && bHasMaternity) return 1;
        
        // Prioridade 2: Por distância (mais próximo primeiro)
        return (a.distance || 0) - (b.distance || 0);
    });
    
    if (sortedHospitals.length === 0) {
        this.showEmptyState();
        return;
    }
    
    // Renderização
    const fragment = document.createDocumentFragment();
    const container = document.createElement('div');
    
    // Disclaimer obrigatório (compliance)
    container.innerHTML = renderizarDisclaimer();
    
    // Contador de hospitais
    const contador = document.createElement('p');
    contador.style.cssText = 'margin-bottom: var(--sophia-spacing-md); color: var(--sophia-text-secondary);';
    contador.textContent = `Encontrados ${sortedHospitals.length} hospital(is) próximo(s):`;
    container.appendChild(contador);
    
    // Cards de hospitais
    sortedHospitals.forEach((hospital, index) => {
        // Garantir que hasMaternity seja null se não estiver definido (não tentar inferir)
        hospital.hasMaternity = hospital.hasMaternity ?? null;
        
        const cardHtml = renderizarCardHospital(hospital, index, this);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = cardHtml;
        container.appendChild(tempDiv.firstElementChild);
    });
    
    fragment.appendChild(container);
    this.hospitalsList.innerHTML = '';
    this.hospitalsList.appendChild(fragment);
    
    // Adiciona event listeners
    this.attachHospitalEventListeners();
}
```

---

## 🔒 Comparação: Antes vs Depois

### ❌ ANTES (NÃO COMPLIANCE)

```javascript
// LÓGICA REMOVIDA - NÃO USAR
const MATERNITY_KEYWORDS = ['maternidade', 'obstetr', 'parto', 'mulher', 'mae', 'infantil'];

function getHospitalBadge(hospital) {
    if (hasMaternity === null) {
        // ❌ TENTAVA ADIVINHAR - REMOVIDO
        const encontrouKeyword = MATERNITY_KEYWORDS.some(keyword => {
            return nomeHospital.includes(keyword.toLowerCase());
        });
        
        if (encontrouKeyword) {
            return { tipo: 'SUCCESS', texto: '🏥 Provável Maternidade' }; // ❌ INFERÊNCIA
        }
    }
}
```

### ✅ DEPOIS (COMPLIANCE)

```javascript
function getHospitalBadge(hospital) {
    if (hasMaternity === true) {
        return { tipo: 'SUCCESS', texto: '✅ Ala Maternal Habilitada' }; // ✅ DADO OFICIAL
    }
    
    if (hasMaternity === false) {
        return { tipo: 'ERROR', texto: '⚠️ Não possui Ala Maternal' }; // ✅ DADO OFICIAL
    }
    
    // ✅ ESTADO NEUTRO - NÃO TENTA ADIVINHAR
    return { tipo: 'INFO', texto: '📞 Atendimento Geral / Ligue 192' };
}
```

---

## 📋 Resumo da Nova Lógica

### getHospitalBadge - 3 Estados Apenas

| Valor | Tipo | Texto | Cor | Observação |
|-------|------|-------|-----|------------|
| `true` | SUCCESS | "✅ Ala Maternal Habilitada" | Verde | Dado oficial (CNES/manual) |
| `false` | ERROR | "⚠️ Não possui Ala Maternal" | Laranja | Dado oficial (CNES/manual) |
| `null` | INFO | "📞 Atendimento Geral / Ligue 192" | Cinza | Estado neutro (sem informação) |

### Regras Críticas
- ❌ **NUNCA** inferir baseado em nome
- ❌ **NUNCA** usar palavras-chave
- ❌ **NUNCA** tentar adivinhar
- ✅ **SEMPRE** usar dados oficiais (true/false)
- ✅ **SEMPRE** estado neutro quando null

---

## ✅ Checklist de Implementação

### Código
- [x] Remover lista de palavras-chave (`MATERNITY_KEYWORDS`)
- [x] Remover lógica de Smart Check (inferência)
- [x] Atualizar `getHospitalBadge()` para 3 estados apenas
- [x] Implementar estado neutro para `null`
- [x] Criar função `renderizarDisclaimer()`
- [x] Atualizar `displayHospitals()` para remover inferência
- [x] Adicionar disclaimer obrigatório

### CSS
- [x] Estilos para badge SUCCESS (verde)
- [x] Estilos para badge ERROR (laranja)
- [x] Estilos para badge INFO (cinza)
- [ ] Estilos para disclaimer (opcional - inline já implementado)

### Testes
- [ ] Testar: Estado true → Badge verde
- [ ] Testar: Estado false → Badge laranja
- [ ] Testar: Estado null → Badge cinza (neutro)
- [ ] Testar: Nenhuma inferência automática funciona
- [ ] Testar: Disclaimer exibido corretamente

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Correção crítica: Remoção de inferência automática (Compliance) | Dev (James) |
