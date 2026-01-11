# Especificação Mobile-2: Chat e Interações

**Criado por:** Sally (UX Expert)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Aprovado

---

## 📱 ÁREA DE ENTRADA DE TEXTO (INPUT) NO MOBILE

### **Problema:**
Teclado virtual no mobile pode cobrir o input, impedindo que a mãe veja o que está digitando.

### **Solução Recomendada:**

#### **1. Input Fixo Acima da Bottom Navigation**
- ✅ **Posição:** `position: fixed`, `bottom: 64px` (acima da bottom nav)
- ✅ **Z-index:** 998 (acima do conteúdo, abaixo do header)
- ✅ **Altura mínima:** 70px (confortável para toque)

#### **2. Ajuste Quando Teclado Virtual Abre**
- ✅ **Detecção:** JavaScript detecta quando teclado abre
- ✅ **Ajuste:** `transform: translateY(-40vh)` quando teclado está visível
- ✅ **Transição:** `transition: transform 0.3s ease` (suave)

#### **3. CSS Implementado:**
```css
@media (max-width: 1023px) {
    .input-area {
        position: fixed !important;
        bottom: 64px !important; /* Acima da bottom navigation */
        left: 0;
        right: 0;
        width: 100vw;
        z-index: 998;
        min-height: 70px;
        transition: bottom 0.3s ease, transform 0.3s ease;
    }
    
    .input-area.keyboard-open {
        transform: translateY(-40vh); /* Move para cima quando teclado abre */
    }
}
```

### **JavaScript para Detecção de Teclado:**
```javascript
// Detecta quando teclado virtual abre/fecha
function detectKeyboard() {
    const inputArea = document.querySelector('.input-area');
    const viewportHeight = window.innerHeight;
    
    window.addEventListener('resize', () => {
        const currentHeight = window.innerHeight;
        const heightDiff = viewportHeight - currentHeight;
        
        // Se altura diminuiu significativamente (teclado abriu)
        if (heightDiff > 150) {
            inputArea.classList.add('keyboard-open');
        } else {
            inputArea.classList.remove('keyboard-open');
        }
    });
}
```

---

## ⚡ STREAMING DE RESPOSTAS NO MOBILE

### **Análise:**

**Desktop (25ms por caractere):**
- ✅ Funciona bem em conexões rápidas
- ✅ Efeito visual agradável

**Mobile 4G Normal (~10-20 Mbps):**
- ✅ 25ms ainda funciona, mas pode parecer lento
- ⚠️ Usuário pode pensar que está travado

**Mobile 4G Lento (~1-3 Mbps):**
- ❌ 25ms é muito lento
- ❌ Resposta parece "engasgar"
- ❌ Usuário pode perder interesse

### **Recomendação:**

✅ **Velocidade Adaptativa Baseada em Tamanho de Tela:**

- **Desktop (≥1024px):** 25ms por caractere (atual)
- **Mobile (<1024px):** 15ms por caractere (40% mais rápido)

**Justificativa:**
- Mobile geralmente tem conexões mais lentas
- Usuário espera respostas mais rápidas em mobile
- 15ms ainda mantém efeito visual, mas não parece travado
- Reduz sensação de "espera" em conexões lentas

### **Implementação:**
```javascript
// Velocidade adaptativa baseada em tamanho de tela
const isMobile = window.innerWidth <= 1023;
const streamingSpeed = isMobile ? 15 : 25; // 15ms no mobile, 25ms no desktop
await this.typewriterEffect(messageTextElement, content, streamingSpeed);
```

### **Alternativa (Futuro):**
Para conexões muito lentas (< 3G), considerar mostrar resposta completa sem streaming:
```javascript
const connectionSpeed = navigator.connection?.effectiveType || '4g';
if (connectionSpeed === '2g' || connectionSpeed === 'slow-2g') {
    // Mostra resposta completa (sem streaming)
    messageTextElement.innerHTML = this.formatMessage(content);
} else {
    // Usa streaming adaptativo
    const speed = isMobile ? 15 : 25;
    await this.typewriterEffect(messageTextElement, content, speed);
}
```

---

## 💬 INDICADOR DE DIGITAÇÃO DA SOPHIA (MOBILE)

### **Requisitos:**

1. **Visível:** Mãe precisa saber que Sophia está "digitando"
2. **Discreto:** Não deve distrair ou ocupar muito espaço
3. **Localização:** Topo da aba de chat (abaixo do header, se existir)
4. **Visual:** Animação suave de 3 pontos pulsantes
5. **Cor:** Paleta quente (coral suave)

### **Design Proposto:**

#### **Posicionamento:**
- **Desktop:** Mantém posição atual (dentro do chat)
- **Mobile:** Fixo no topo da aba de chat, abaixo do header (se existir)

#### **Estilo Visual:**
```css
/* Indicador de Digitação Mobile */
@media (max-width: 1023px) {
    .typing-indicator {
        position: sticky;
        top: 0;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 143, 163, 0.2);
        z-index: 100;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .typing-dots {
        display: flex;
        gap: 0.4rem;
        align-items: center;
        justify-content: center;
    }
    
    .typing-dots span {
        width: 8px;
        height: 8px;
        background: var(--color-primary-warm, #ff8fa3);
        border-radius: 50%;
        animation: typingDot 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) {
        animation-delay: 0s;
    }
    
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typingDot {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.4;
        }
        30% {
            transform: translateY(-8px);
            opacity: 1;
        }
    }
    
    .typing-indicator span:not(.typing-dots) {
        font-size: 0.85rem;
        color: var(--text-warm-medium, #666);
        margin-left: 0.5rem;
    }
}
```

#### **Tamanho e Espaçamento:**
- **Altura:** ~40px (discreto, não ocupa muito espaço)
- **Padding:** 0.75rem vertical, 1rem horizontal
- **Fonte:** 0.85rem (legível mas não intrusivo)
- **Ícones:** 8px × 8px (pequenos e discretos)

#### **Comportamento:**
- Aparece quando Sophia está "digitando" (resposta sendo gerada)
- Desaparece quando resposta completa
- Transição suave: `opacity: 0 → 1` com `transition: opacity 0.3s ease`

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### **Input Mobile:**
- [x] Input fixo acima da bottom navigation
- [ ] Detecção de teclado virtual (JavaScript)
- [ ] Ajuste de posição quando teclado abre
- [ ] Teste em dispositivos reais

### **Streaming de Respostas:**
- [x] Velocidade adaptativa (15ms mobile, 25ms desktop)
- [ ] Indicador de progresso durante streaming
- [ ] Fallback para conexões muito lentas (futuro)

### **Indicador de Digitação:**
- [ ] CSS para mobile implementado
- [ ] Posicionamento sticky no topo
- [ ] Animação de 3 pontos pulsantes
- [ ] Transições suaves

---

## 📝 PRÓXIMOS PASSOS

1. **Dev:** Implementar detecção de teclado virtual
2. **Dev:** Ajustar posição do input quando teclado abre
3. **Dev:** Implementar indicador de digitação mobile
4. **UX (Sally):** Validar protótipos
5. **Testes:** Usabilidade em dispositivos reais com teclado virtual

---

**Versão:** 1.0  
**Status:** ✅ Aprovado  
**Próxima Revisão:** Após implementação
