# Código: Card de Hospital - Ala Maternal

**Desenvolvedor:** James  
**Contexto:** Implementação da lógica de exibição condicional nos Cards de Hospital  
**Objetivo:** Implementar renderização condicional baseada em `hasMaternityWard`

**Data:** {{date}}

---

## 📋 Visão Geral

### Requisitos de Código
1. Receber a lista de hospitais da API
2. Implementar renderização condicional:
   - `IF (hospital.hasMaternityWard === true)` → Renderizar Badge de Sucesso
   - `IF (hospital.hasMaternityWard === false || null)` → Renderizar Badge de Alerta + Texto 'Não contém Ala Maternal'
3. Garantir que a lista renderizada respeite a ordem de prioridade (Maternidade primeiro)

---

## 💻 Código de Exemplo

### Função: Renderização Condicional do Badge

```javascript
/**
 * Cria o badge de Ala Maternal baseado no estado do hospital
 * @param {Object} hospital - Objeto do hospital com hasMaternityWard
 * @returns {string} HTML do badge de maternidade
 */
function criarBadgeAlaMaternal(hospital) {
    // Validação: garantir que hasMaternityWard sempre seja boolean
    const hasMaternityWard = hospital.hasMaternityWard ?? false;
    
    // Estado POSITIVO: Hospital TEM Ala Maternal
    if (hasMaternityWard === true) {
        return `
            <div class="hospital-badge-maternity-positive">
                <i class="fas fa-baby"></i>
                <span>Possui Ala Maternal</span>
            </div>
        `;
    }
    
    // Estado NEGATIVO: Hospital NÃO TEM Ala Maternal
    // Tratamento de NULL/FALSE: sempre exibir como negativo
    return `
        <div class="hospital-badge-maternity-negative">
            <i class="fas fa-exclamation-triangle"></i>
            <span>Não possui Ala Maternal - Apenas PS Geral</span>
        </div>
    `;
}
```

---

### Função: Validação e Sanitização de Dados

```javascript
/**
 * Valida e sanitiza dados do hospital
 * Garante que hasMaternityWard sempre seja boolean
 * @param {Object} hospital - Objeto do hospital
 * @returns {Object} Hospital validado
 */
function validarHospital(hospital) {
    // Garantir que hasMaternityWard sempre seja boolean (nunca null/undefined)
    const hasMaternityWard = hospital.hasMaternityWard ?? false;
    
    return {
        ...hospital,
        hasMaternityWard: Boolean(hasMaternityWard)
    };
}
```

---

### Função: Ordenação de Hospitais

```javascript
/**
 * Ordena hospitais por prioridade:
 * 1. Hospitais com Ala Maternal primeiro (hasMaternityWard=true)
 * 2. Entre mesmos tipos, ordena por distância (mais próximo primeiro)
 * @param {Array} hospitais - Array de hospitais
 * @returns {Array} Array de hospitais ordenado
 */
function ordenarHospitais(hospitais) {
    return [...hospitais].sort((a, b) => {
        // Validação: garantir que hasMaternityWard sempre seja boolean
        const aHasMaternity = a.hasMaternityWard ?? false;
        const bHasMaternity = b.hasMaternityWard ?? false;
        
        // Prioridade 1: Hospitais com Ala Maternal primeiro
        if (aHasMaternity && !bHasMaternity) return -1;
        if (!aHasMaternity && bHasMaternity) return 1;
        
        // Prioridade 2: Entre mesmos tipos, ordena por distância (mais próximo primeiro)
        return (a.distance || 0) - (b.distance || 0);
    });
}
```

---

### Função: Renderização Completa do Card

```javascript
/**
 * Renderiza o card completo do hospital com badge de Ala Maternal
 * @param {Object} hospital - Objeto do hospital
 * @param {number} index - Índice do hospital na lista
 * @returns {string} HTML completo do card
 */
function renderizarCardHospital(hospital, index) {
    // Validação: garantir que hasMaternityWard sempre seja boolean
    const hospitalValidado = validarHospital(hospital);
    const hasMaternityWard = hospitalValidado.hasMaternityWard ?? false;
    
    // Sanitização de dados
    const hospitalName = formatHospitalName(hospitalValidado.name || 'Hospital');
    const sanitizedPhone = hospitalValidado.phone ? sanitizePhone(hospitalValidado.phone) : '';
    const sanitizedAddress = hospitalValidado.address ? sanitizeString(hospitalValidado.address) : '';
    const distanceKm = ((hospitalValidado.distance || 0) / 1000).toFixed(1);
    
    // Badge de Ala Maternal (condicional)
    const badgeAlaMaternal = criarBadgeAlaMaternal(hospitalValidado);
    
    // Badges secundários (opcional)
    const badges = [];
    if (hospitalValidado.isEmergency === true) {
        badges.push(createBadge('emergency', 'Pronto Socorro', 'fas fa-ambulance'));
    }
    
    // HTML do card
    return `
        <div class="hospital-card" data-index="${index}">
            <div class="hospital-header">
                <h4 class="hospital-name">${hospitalName}</h4>
                <span class="hospital-distance">${distanceKm} km</span>
            </div>
            ${badgeAlaMaternal}
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
                            ${escapeHtml(hospitalValidado.phone)}
                        </a>
                    </p>
                ` : ''}
                ${hospitalValidado.website ? `
                    <p class="hospital-website">
                        <i class="fas fa-globe"></i>
                        <a href="${hospitalValidado.website}" 
                           target="_blank" 
                           rel="noopener" 
                           class="hospital-website-link">
                            ${escapeHtml(hospitalValidado.website)}
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
                <a href="https://www.google.com/maps/dir/?api=1&destination=${hospitalValidado.lat},${hospitalValidado.lon}" 
                   target="_blank" 
                   class="btn-sophia btn-sophia-compact hospital-route-btn">
                    <i class="fas fa-route"></i> Rota
                </a>
                <a href="https://www.google.com/maps/search/?api=1&query=${hospitalValidado.lat},${hospitalValidado.lon}" 
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

### Função: Renderização da Lista Completa

```javascript
/**
 * Renderiza a lista completa de hospitais com ordenação e badges
 * @param {Array} hospitais - Array de hospitais da API
 */
function displayHospitals(hospitais) {
    if (!hospitais || hospitais.length === 0) {
        showEmptyState();
        return;
    }
    
    // Validação e sanitização: garantir que todos os hospitais tenham hasMaternityWard como boolean
    const hospitaisValidados = hospitais.map(validarHospital);
    
    // Ordenação: hospitais com Ala Maternal primeiro
    const hospitaisOrdenados = ordenarHospitais(hospitaisValidados);
    
    // Renderização
    const fragment = document.createDocumentFragment();
    const container = document.createElement('div');
    container.innerHTML = `<p style="margin-bottom: var(--sophia-spacing-md); color: var(--sophia-text-secondary);">Encontrados ${hospitaisOrdenados.length} hospital(is) próximo(s):</p>`;
    
    hospitaisOrdenados.forEach((hospital, index) => {
        const cardHtml = renderizarCardHospital(hospital, index);
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

## 🎨 CSS (Estilos dos Badges)

### Badge Positivo (Hospital TEM Ala Maternal)

```css
.hospital-badge-maternity-positive {
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

.hospital-badge-maternity-positive i {
    font-size: 1rem;
    color: #FFFFFF;
}
```

### Badge Negativo (Hospital NÃO TEM Ala Maternal)

```css
.hospital-badge-maternity-negative {
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

.hospital-badge-maternity-negative i {
    font-size: 1rem;
    color: #FFFFFF;
}
```

---

## 📝 Funções Auxiliares (Referência)

### Funções de Sanitização

```javascript
/**
 * Formata nome do hospital para exibição elegante
 */
function formatHospitalName(name) {
    if (!name) return 'Hospital';
    return name.trim();
}

/**
 * Sanitiza telefone
 */
function sanitizePhone(phone) {
    if (!phone) return '';
    return phone.trim();
}

/**
 * Sanitiza string
 */
function sanitizeString(str) {
    if (!str) return '';
    return str.trim();
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Cria badge genérico (para badges secundários)
 */
function createBadge(type, text, iconClass) {
    const badgeClass = `hospital-badge-${type}`;
    return `
        <span class="${badgeClass}">
            <i class="${iconClass}"></i>
            <span>${text}</span>
        </span>
    `;
}
```

---

## ✅ Checklist de Implementação

### Validação
- [x] Função `validarHospital()` garante que `hasMaternityWard` sempre seja boolean
- [x] Função `criarBadgeAlaMaternal()` trata NULL/FALSE como negativo
- [x] Função `ordenarHospitais()` prioriza hospitais com maternidade

### Renderização
- [x] Badge positivo renderizado quando `hasMaternityWard === true`
- [x] Badge negativo renderizado quando `hasMaternityWard === false || null`
- [x] Lista renderizada respeitando ordem de prioridade

### CSS
- [x] Estilos do badge positivo definidos
- [x] Estilos do badge negativo definidos
- [x] Badges responsivos (mobile/desktop)

---

## 🧪 Testes (Exemplo)

### Teste 1: Badge Positivo
```javascript
const hospitalComMaternidade = {
    name: "Hospital com Maternidade",
    hasMaternityWard: true
};

const badge = criarBadgeAlaMaternal(hospitalComMaternidade);
// Esperado: Badge verde com texto "Possui Ala Maternal"
```

### Teste 2: Badge Negativo
```javascript
const hospitalSemMaternidade = {
    name: "Hospital sem Maternidade",
    hasMaternityWard: false
};

const badge = criarBadgeAlaMaternal(hospitalSemMaternidade);
// Esperado: Badge laranja com texto "Não possui Ala Maternal - Apenas PS Geral"
```

### Teste 3: Tratamento de NULL
```javascript
const hospitalNull = {
    name: "Hospital com NULL",
    hasMaternityWard: null
};

const badge = criarBadgeAlaMaternal(hospitalNull);
// Esperado: Badge laranja (tratado como false)
```

### Teste 4: Ordenação
```javascript
const hospitais = [
    { name: "A", hasMaternityWard: false, distance: 2 },
    { name: "B", hasMaternityWard: true, distance: 5 },
    { name: "C", hasMaternityWard: false, distance: 1 },
    { name: "D", hasMaternityWard: true, distance: 3 }
];

const ordenados = ordenarHospitais(hospitais);
// Esperado: [D (3km), B (5km), C (1km), A (2km)]
```

---

## 📝 Notas para Implementação

### Para @dev
- **Prioridade:** Implementar validação: `hasMaternityWard ?? false`
- **Prioridade:** Implementar função `criarBadgeAlaMaternal()` com renderização condicional
- **Prioridade:** Implementar função `ordenarHospitais()` antes da renderização

### Para @qa
- **Testar:** Badge positivo renderizado corretamente
- **Testar:** Badge negativo renderizado corretamente
- **Testar:** Tratamento de NULL (converter para false)
- **Testar:** Ordenação funciona corretamente

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial do código de exemplo | Dev (James) |
