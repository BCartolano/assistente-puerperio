# 🎨 Manual de Sobrevivência Visual - Sophia

## ⚠️ REGRAS CRÍTICAS - NUNCA VIOLAR

### 🚫 PROIBIÇÕES ABSOLUTAS

1. **Cores Cinzas em Botões - ERRO CRÍTICO**
   - ❌ NUNCA use `#555`, `#333`, `#666`, `rgba(108, 117, 125, ...)` em botões
   - ❌ NUNCA use `background: #555` ou similares
   - ✅ SEMPRE use variáveis CSS: `var(--sophia-pink-primary)`, `var(--sophia-bg-gradient)`

2. **Tamanhos de Botões - ERRO CRÍTICO**
   - ❌ NUNCA use `padding: 1.5rem 3rem` ou maiores
   - ❌ NUNCA use `min-height: 200px` ou alturas fixas em botões
   - ✅ SEMPRE use `padding: 0.75rem 1.1rem` (máximo `0.85rem 1.2rem`)
   - ✅ SEMPRE use `min-height: auto` e `height: auto`

3. **Hard-coding de Cores - ERRO CRÍTICO**
   - ❌ NUNCA escreva `background: #f4a6a6` diretamente
   - ✅ SEMPRE use `var(--sophia-pink-primary)`

---

## ✅ CHECKLIST ANTES DE QUALQUER IMPLEMENTAÇÃO

### Cores
- [ ] Verifiquei se estou usando `--sophia-pink-primary` em vez de hex
- [ ] Não há nenhum `#555`, `#333`, `#666` no código
- [ ] Todos os botões usam `var(--sophia-bg-gradient)` ou variáveis CSS
- [ ] Hover states usam `linear-gradient(135deg, var(--sophia-pink-primary) 0%, var(--sophia-pink-secondary) 100%)`

### Tamanhos
- [ ] Botões têm `padding: 0.75rem 1.1rem` (máximo `0.85rem 1.2rem`)
- [ ] Fontes são `0.9rem` (máximo `0.95rem`)
- [ ] `min-height: auto` e `height: auto` em todos os botões
- [ ] Ícones não excedem `3rem` (máximo `2.5rem` em mobile)

### Imagens
- [ ] Imagens têm `max-height: 150px` (desktop) e `120px` (mobile)
- [ ] Containers têm `border-radius: 24px` (ou `var(--sophia-border-radius-lg)`)
- [ ] Background usa `var(--sophia-bg-white)`

### Event Listeners
- [ ] Botões dinâmicos usam event delegation no container pai
- [ ] Funções estão expostas globalmente (`window.chatApp?.`)
- [ ] Não há `addEventListener` direto em elementos que serão recriados

---

## 🎨 PALETA DE CORES SOPHIA

### Cores Primárias (SEMPRE USAR)
```css
--sophia-pink-primary: #f4a6a6;      /* Rosa principal */
--sophia-pink-secondary: #f8b8c8;   /* Rosa secundário */
--sophia-pink-light: rgba(244, 166, 166, 0.3);
--sophia-pink-medium: rgba(244, 166, 166, 0.4);
--sophia-pink-dark: #e89595;
```

### Cores de Texto
```css
--sophia-text-primary: #7a4a4a;      /* Texto principal */
--sophia-text-secondary: #8b6a5a;    /* Texto secundário */
--sophia-text-light: #9a7a6a;        /* Texto claro */
```

### Cores de Fundo
```css
--sophia-bg-white: rgba(255, 255, 255, 0.9);
--sophia-bg-light: rgba(255, 252, 250, 0.85);
--sophia-bg-gradient: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 249, 247, 0.7) 100%);
```

### Cores de Alerta
```css
--sophia-emergency: #e63946;         /* Apenas emergências reais */
--sophia-warning: #ffb703;           /* Atenção */
```

---

## 📐 TAMANHOS PADRÃO

### Botões
```css
/* Botão Padrão */
padding: 0.75rem 1.1rem;
font-size: 0.9rem;
font-weight: 600;
min-height: auto;
height: auto;
border-radius: var(--sophia-border-radius-sm); /* 12px */

/* Botão Compacto */
padding: 0.65rem 0.9rem;
font-size: 0.85rem;

/* Botão Grande (apenas emergências) */
padding: 0.85rem 1.2rem;
font-size: 0.95rem;
```

### Ícones
```css
/* Ícones em Botões */
font-size: 1rem; /* Desktop */
font-size: 0.95rem; /* Mobile */

/* Ícones em Cards */
font-size: 2.5rem; /* Desktop */
font-size: 2rem; /* Mobile */

/* Ícones de Resultado */
font-size: 3rem; /* Desktop */
font-size: 2.5rem; /* Mobile */
```

### Imagens
```css
/* Imagens em Cards */
max-height: 150px; /* Desktop */
max-height: 120px; /* Mobile */
border-radius: var(--sophia-border-radius-lg); /* 24px */
```

---

## 🔧 COMPONENTES PADRÃO

### Botão Sophia (Base)
```css
.btn-sophia {
    background: var(--sophia-bg-gradient) !important;
    border: 2px solid var(--sophia-pink-medium) !important;
    border-radius: var(--sophia-border-radius-sm) !important;
    color: var(--sophia-text-primary) !important;
    padding: 0.75rem 1.1rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    min-height: auto !important;
    height: auto !important;
}

.btn-sophia:hover {
    background: linear-gradient(135deg, var(--sophia-pink-primary) 0%, var(--sophia-pink-secondary) 100%) !important;
    border-color: var(--sophia-pink-primary) !important;
    color: white !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--sophia-shadow-md) !important;
}
```

### Card de Sintoma
```css
.sintoma-card {
    background: var(--sophia-bg-gradient) !important;
    border: 2px solid var(--sophia-pink-light) !important;
    border-radius: var(--sophia-border-radius-md) !important;
    padding: var(--sophia-spacing-md) !important;
    box-shadow: var(--sophia-shadow-sm) !important;
}
```

---

## 🎯 EVENT DELEGATION - PADRÃO OBRIGATÓRIO

### ❌ ERRADO (Botão Morre se DOM for Atualizado)
```javascript
// NÃO FAÇA ISSO
document.querySelector('.sintoma-btn-yes').addEventListener('click', ...);
```

### ✅ CORRETO (Event Delegation)
```javascript
// SEMPRE FAÇA ISSO
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.sintoma-btn-yes');
    if (btn) {
        // Processa clique
    }
});
```

---

## 📱 RESPONSIVIDADE

### Mobile (max-width: 768px)
```css
/* Botões */
padding: 0.7rem 0.9rem !important;
font-size: 0.85rem !important;

/* Cards */
padding: var(--sophia-spacing-sm) !important;

/* Imagens */
max-height: 120px !important;
```

---

## 🧪 TESTES OBRIGATÓRIOS

### Antes de Commitar
1. [ ] Inspecione todos os botões - nenhum está cinza
2. [ ] Verifique tamanhos - nenhum botão está gigante
3. [ ] Teste triagem completa - 5 vezes seguidas
4. [ ] Verifique localStorage - histórico está salvando
5. [ ] Teste mobile - botões têm padding confortável
6. [ ] Console limpo - nenhum erro JavaScript

---

## 🚨 ALERTAS DE REGRESSÃO

Se você ver qualquer um destes, **REVERTA IMEDIATAMENTE**:

- Botão com `background: #555` ou similar
- Botão com `padding: 2rem` ou maior
- Botão com `min-height: 200px` ou altura fixa
- Cor hexadecimal hard-coded em vez de variável CSS
- Event listener direto em elemento dinâmico
- Ícone maior que `3rem`

---

## 📚 REFERÊNCIAS

- Arquivo de Variáveis CSS: `backend/static/css/style.css` (linhas 7502-7551)
- Componente Base: `.btn-sophia` (linhas 9836-9875)
- Função de Triagem: `showSintomasTriagem()` em `backend/static/js/chat.js`

---

**Última Atualização**: Restauração de Identidade Visual - 2024
**Mantenedor**: Equipe Sophia UX/Dev
