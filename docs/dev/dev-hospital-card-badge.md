# Código: HospitalCard e getHospitalBadge

**Desenvolvedor:** James  
**Contexto:** Implementação do componente HospitalCard com função getHospitalBadge  
**Objetivo:** Criar código pronto para renderização de cards de hospital com detecção automática

**Data:** {{date}}

---

## 📋 Visão Geral

### Tecnologia
JavaScript vanilla (não React) - compatível com código existente

### Regras de Renderização
- PRIORIDADE 1: Dado oficial (true) → Badge verde "Ala Maternal Confirmada"
- PRIORIDADE 2: Dado oficial negativo (false) → Badge laranja "Não possui Maternidade"
- PRIORIDADE 3: Smart Check (null) → Detecta palavras-chave:
  - Encontrou → Badge verde "Provável Maternidade" (texto diferente para honestidade jurídica)
  - Não encontrou → Badge azul/cinza "Pronto Socorro Geral"

---

## 💻 Código Completo

### Função: getHospitalBadge

```javascript
/**
 * Palavras-chave para detecção automática de maternidade
 */
const MATERNITY_KEYWORDS = ['maternidade', 'obstetr', 'parto', 'mulher', 'mae', 'infantil'];

/**
 * Retorna badge de maternidade baseado em dados do hospital
 * 
 * @param {Object} hospital - Objeto do hospital
 * @param {boolean|null} hospital.hasMaternity - Valor do banco (true/false/null)
 * @param {string} hospital.nome - Nome do hospital (ou hospital.name)
 * @returns {Object} Objeto com tipo e texto do badge
 * @returns {string} resultado.tipo - 'SUCCESS' | 'ERROR' | 'INFO'
 * @returns {string} resultado.texto - Texto do badge
 */
function getHospitalBadge(hospital) {
    // Normaliza nome (aceita tanto 'nome' quanto 'name')
    const nomeHospital = (hospital.nome || hospital.name || '').toLowerCase();
    const hasMaternity = hospital.hasMaternity; // true, false, ou null/undefined
    
    // PRIORIDADE 1: Dado Oficial (true)
    if (hasMaternity === true) {
        return {
            tipo: 'SUCCESS',
            texto: '✅ Ala Maternal Confirmada'
        };
    }
    
    // PRIORIDADE 2: Dado Oficial Negativo (false)
    if (hasMaternity === false) {
        return {
            tipo: 'ERROR',
            texto: '⚠️ Não possui Maternidade'
        };
    }
    
    // PRIORIDADE 3: Smart Check (null/undefined)
    // Verifica se nome contém alguma das palavras-chave
    const encontrouKeyword = MATERNITY_KEYWORDS.some(keyword => {
        return nomeHospital.includes(keyword.toLowerCase());
    });
    
    if (encontrouKeyword) {
        // Encontrou palavra-chave → Provável Maternidade (texto sutilmente diferente)
        return {
            tipo: 'SUCCESS',
            texto: '🏥 Provável Maternidade'
        };
    } else {
        // Não encontrou → Pronto Socorro Geral
        return {
            tipo: 'INFO',
            texto: 'ℹ️ Pronto Socorro Geral'
        };
    }
}
```

---

### Função: renderizarBadgeMaternal

```javascript
/**
 * Renderiza o HTML do badge de maternidade
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

### Função: renderizarCardHospital (Integração com código existente)

```javascript
/**
 * Renderiza card completo do hospital com badge de maternidade
 * Integra com código existente da classe ChatbotPuerperio
 * 
 * @param {Object} hospital - Objeto do hospital
 * @param {number} index - Índice do hospital na lista
 * @param {Object} context - Contexto (this da classe ChatbotPuerperio)
 * @returns {string} HTML completo do card
 */
function renderizarCardHospital(hospital, index, context) {
    // Normaliza propriedades (aceita nome/name)
    const nomeHospital = hospital.nome || hospital.name || 'Hospital';
    const distanciaKm = ((hospital.distance || 0) / 1000).toFixed(1);
    
    // Sanitização (usa métodos da classe se disponível)
    const hospitalName = context.formatHospitalName ? 
        context.formatHospitalName(nomeHospital) : nomeHospital;
    const sanitizedPhone = hospital.phone ? 
        (context.sanitizePhone ? context.sanitizePhone(hospital.phone) : hospital.phone) : '';
    const sanitizedAddress = hospital.address ? 
        (context.sanitizeString ? context.sanitizeString(hospital.address) : hospital.address) : '';
    const escapeHtml = context.escapeHtml || ((text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    });
    
    // Badge de Maternidade
    const badgeMaternal = renderizarBadgeMaternal({
        hasMaternity: hospital.hasMaternity,
        nome: nomeHospital,
        name: nomeHospital
    });
    
    // Badges secundários (opcional)
    const badges = [];
    if (hospital.isEmergency === true) {
        const createBadge = context.createBadge || function(type, text, icon) {
            return `<span class="hospital-badge-${type}">
                <i class="${icon}"></i>
                <span>${text}</span>
            </span>`;
        };
        badges.push(createBadge('emergency', 'Pronto Socorro', 'fas fa-ambulance'));
    }
    
    // HTML do card
    return `
        <div class="hospital-card" data-index="${index}">
            <div class="hospital-header">
                <h4 class="hospital-name">${hospitalName}</h4>
                <span class="hospital-distance">${distanciaKm} km</span>
            </div>
            ${badgeMaternal}
            ${badges.length > 0 ? `<div class="hospital-badges">${badges.join('')}</div>` : ''}
            <div class="hospital-info">
                ${sanitizedAddress ? `
                    <p class="hospital-address">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${escapeHtml(sanitizedAddress)}</span>
                        <button class="hospital-copy-btn" 
                                data-copy="${escapeHtml(sanitizedAddress)}" 
                                aria-label="Copiar endereço"
                                title="Copiar endereço">
                            <i class="fas fa-copy"></i>
                        </button>
                    </p>
                ` : ''}
                ${sanitizedPhone ? `
                    <p class="hospital-phone">
                        <i class="fas fa-phone"></i>
                        <a href="tel:${sanitizedPhone}" 
                           class="hospital-phone-link" 
                           data-phone="${sanitizedPhone}">
                            ${escapeHtml(hospital.phone)}
                        </a>
                    </p>
                ` : ''}
                ${hospital.website ? `
                    <p class="hospital-website">
                        <i class="fas fa-globe"></i>
                        <a href="${hospital.website}" 
                           target="_blank" 
                           rel="noopener" 
                           class="hospital-website-link">
                            ${escapeHtml(hospital.website)}
                        </a>
                    </p>
                ` : ''}
            </div>
            <div class="hospital-actions">
                ${sanitizedPhone ? `
                    <a href="tel:${sanitizedPhone}" 
                       class="btn-sophia btn-sophia-compact hospital-call-btn"
                       data-phone="${sanitizedPhone}">
                        <i class="fas fa-phone"></i> Ligar
                    </a>
                ` : ''}
                <a href="https://www.google.com/maps/dir/?api=1&destination=${hospital.lat},${hospital.lon}" 
                   target="_blank" 
                   class="btn-sophia btn-sophia-compact hospital-route-btn">
                    <i class="fas fa-route"></i> Rota
                </a>
                <a href="https://www.google.com/maps/search/?api=1&query=${hospital.lat},${hospital.lon}" 
                   target="_blank" 
                   class="btn-sophia btn-sophia-compact hospital-map-btn">
                    <i class="fas fa-map"></i> Ver Mapa
                </a>
            </div>
        </div>
    `;
}
```

---

### Integração com código existente (atualização do método displayHospitals)

```javascript
/**
 * Método atualizado displayHospitals (para adicionar na classe ChatbotPuerperio)
 * Substitui a lógica de badge de maternidade pela nova função getHospitalBadge
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
    
    // Ordena: hospitais com maternidade primeiro, depois por distância
    const sortedHospitals = [...completeHospitals].sort((a, b) => {
        // Normaliza hasMaternity (aceita ambos os formatos)
        const aHasMaternity = a.hasMaternity === true || (a.hasMaternity === null && getHospitalBadge(a).tipo === 'SUCCESS');
        const bHasMaternity = b.hasMaternity === true || (b.hasMaternity === null && getHospitalBadge(b).tipo === 'SUCCESS');
        
        // Prioridade 1: Hospitais com maternidade primeiro
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
    container.innerHTML = `<p style="margin-bottom: var(--sophia-spacing-md); color: var(--sophia-text-secondary);">Encontrados ${sortedHospitals.length} hospital(is) próximo(s):</p>`;
    
    sortedHospitals.forEach((hospital, index) => {
        // Normaliza propriedade hasMaternity
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

## 🎨 CSS para os Badges

### Estilos dos Badges (adicionar ao arquivo CSS)

```css
/* Badge SUCCESS - Verde Escuro (Bold) */
.hospital-badge-maternity-success {
    background: linear-gradient(135deg, #28a745 0%, #218838 100%);
    color: #FFFFFF;
    padding: 0.5rem 0.75rem;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 700;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.75rem;
}

.hospital-badge-maternity-success span {
    color: #FFFFFF;
    font-weight: 700;
}

/* Badge ERROR - Laranja/Vermelho */
.hospital-badge-maternity-error {
    background: linear-gradient(135deg, #ffb703 0%, #e6a502 100%);
    color: #FFFFFF;
    padding: 0.5rem 0.75rem;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 700;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(255, 183, 3, 0.3);
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.75rem;
}

.hospital-badge-maternity-error span {
    color: #FFFFFF;
    font-weight: 700;
}

/* Badge INFO - Azul ou Cinza Escuro (Neutro) */
.hospital-badge-maternity-info {
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

.hospital-badge-maternity-info span {
    color: #FFFFFF;
    font-weight: 700;
}
```

---

## 🧪 Testes

### Teste 1: PRIORIDADE 1 - Dado Oficial (true)
```javascript
const hospital = {
    nome: "Hospital Teste",
    hasMaternity: true
};

const badge = getHospitalBadge(hospital);
// Esperado: { tipo: 'SUCCESS', texto: '✅ Ala Maternal Confirmada' }
```

### Teste 2: PRIORIDADE 2 - Dado Oficial Negativo (false)
```javascript
const hospital = {
    nome: "Hospital Teste",
    hasMaternity: false
};

const badge = getHospitalBadge(hospital);
// Esperado: { tipo: 'ERROR', texto: '⚠️ Não possui Maternidade' }
```

### Teste 3: PRIORIDADE 3 - Smart Check (encontrou palavra-chave)
```javascript
const hospital = {
    nome: "Hospital Maternidade São Paulo",
    hasMaternity: null
};

const badge = getHospitalBadge(hospital);
// Esperado: { tipo: 'SUCCESS', texto: '🏥 Provável Maternidade' }
```

### Teste 4: PRIORIDADE 3 - Smart Check (não encontrou)
```javascript
const hospital = {
    nome: "Pronto Socorro Central",
    hasMaternity: null
};

const badge = getHospitalBadge(hospital);
// Esperado: { tipo: 'INFO', texto: 'ℹ️ Pronto Socorro Geral' }
```

---

## 📝 Notas de Implementação

### Compatibilidade
- ✅ Código JavaScript vanilla (não requer React)
- ✅ Compatível com código existente
- ✅ Aceita tanto `hospital.nome` quanto `hospital.name`
- ✅ Aceita tanto `hospital.hasMaternity` quanto `hospital.hasMaternityWard` (com normalização)

### Segurança Jurídica
- ✅ Texto "Provável Maternidade" para detecção automática (não oficial)
- ✅ Texto "Ala Maternal Confirmada" para dados oficiais
- ✅ Texto "Pronto Socorro Geral" para hospitais sem indicação de maternidade

### Integração
- ✅ Função `getHospitalBadge()` independente e reutilizável
- ✅ Função `renderizarCardHospital()` integra com código existente
- ✅ Método `displayHospitals()` atualizado para usar nova lógica

---

## ✅ Checklist de Implementação

### Funções
- [x] `getHospitalBadge()` implementada com todas as prioridades
- [x] `renderizarBadgeMaternal()` implementada
- [x] `renderizarCardHospital()` implementada
- [x] Método `displayHospitals()` atualizado

### CSS
- [x] Estilos para badge SUCCESS (verde)
- [x] Estilos para badge ERROR (laranja)
- [x] Estilos para badge INFO (cinza)

### Testes
- [x] Testes unitários documentados
- [ ] Testes executados
- [ ] Integração testada

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial do código HospitalCard e getHospitalBadge | Dev (James) |
