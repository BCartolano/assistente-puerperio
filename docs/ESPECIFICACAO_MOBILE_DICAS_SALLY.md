# Especificação Mobile: Aba Dicas/Recursos

**Criado por:** Sally (UX Expert)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Aprovado

---

## 🎯 LAYOUT DA ABA 'DICAS/RECURSOS'

### **Estrutura: Lista Vertical de Cards**

✅ **Recomendação:** Usar lista vertical de cards para facilitar scroll e leitura em mobile.

### **Cards Incluídos:**

1. **💡 Dica do Dia**
   - Ícone: 💡
   - Título: "Dica do Dia"
   - Conteúdo: Texto da dica (dinâmico, carregado de `sidebar-content.js`)

2. **✨ Afirmação Positiva**
   - Ícone: ✨
   - Título: "Afirmação Positiva"
   - Conteúdo: Texto da afirmação (dinâmico, carregado de `sidebar-content.js`)

3. **📅 Próxima Vacina**
   - Ícone: 📅
   - Título: "Próxima Vacina"
   - Conteúdo: Widget de próxima vacina (se disponível)

4. **📺 Vídeos Educativos** (Opcional - Futuro)
   - Ícone: 📺
   - Título: "Vídeos Educativos"
   - Conteúdo: Lista de miniaturas de vídeos do YouTube

### **Design dos Cards:**

```css
.mobile-dica-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(255, 143, 163, 0.1);
    border: 1px solid rgba(255, 143, 163, 0.15);
    transition: all 0.3s ease;
}

.mobile-dica-card:active {
    transform: scale(0.98);
    box-shadow: 0 1px 6px rgba(255, 143, 163, 0.15);
}
```

### **Especificações:**

- **Espaçamento:** 1rem entre cards
- **Padding:** 1.25rem interno
- **Borda:** 16px radius (arredondado e acolhedor)
- **Feedback:** Escala 0.98 ao tocar (feedback visual)
- **Cor:** Paleta quente (branco com borda coral)

---

## 🎬 MODAL DE VÍDEO NO MOBILE

### **Comportamento Recomendado:**

✅ **Tela Cheia Automática** para facilitar visualização.

### **Implementação:**

1. **Ao Abrir Modal:**
   - Vídeo abre em tela cheia (fullscreen)
   - Botão de fechar (X) visível no canto superior direito
   - Controles de vídeo do YouTube visíveis

2. **Ao Fechar Modal:**
   - Fecha automaticamente o vídeo
   - Remove `src` do iframe para parar áudio imediatamente
   - Retorna à aba de Dicas

### **CSS para Mobile:**

```css
@media (max-width: 1023px) {
    .video-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100vw;
        height: 100vh;
        z-index: 10000;
        background: rgba(0, 0, 0, 0.95);
    }
    
    .video-modal-content {
        width: 100%;
        height: 100%;
        max-width: 100%;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .video-modal-player iframe {
        width: 100%;
        height: calc(100vh - 100px); /* Altura total menos controles */
        max-height: 100%;
    }
    
    .video-modal-close {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 10001;
        width: 44px;
        height: 44px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
    }
}
```

### **Funcionalidades:**

- ✅ Tela cheia automática ao abrir
- ✅ Botão de fechar grande (44px × 44px) para toque fácil
- ✅ ESC key fecha o modal e para o vídeo
- ✅ Remove `src` ao fechar para parar áudio imediatamente
- ✅ Fundo escuro (rgba(0, 0, 0, 0.95)) para destacar vídeo

---

## 🎨 ESTILO VISUAL DA BOTTOM NAVIGATION

### **Paleta Quente:**

- **Background:** `rgba(255, 255, 255, 0.98)` com `backdrop-filter: blur(20px)`
- **Borda Superior:** `1px solid rgba(255, 143, 163, 0.2)` (coral suave)
- **Sombra:** `0 -2px 12px rgba(0, 0, 0, 0.08)` (sombra superior)

### **Estado Inativo:**

- **Cor do Ícone:** `var(--text-warm-medium, #999)` (cinza médio)
- **Cor do Texto:** `var(--text-warm-medium, #999)` (cinza médio)
- **Tamanho do Ícone:** 1.5rem
- **Tamanho do Texto:** 0.7rem

### **Estado Ativo:**

- **Cor do Ícone:** `var(--color-primary-warm, #ff8fa3)` (coral)
- **Cor do Texto:** `var(--color-primary-warm, #ff8fa3)` (coral)
- **Tamanho do Ícone:** 1.5rem com `transform: scale(1.1)` (ligeiro aumento)
- **Tamanho do Texto:** 0.7rem com `font-weight: 600` (negrito)

### **Feedback Visual:**

1. **Ao Clicar:**
   - Efeito ripple (círculo expandindo de rgba(255, 143, 163, 0.2))
   - `transform: scale(0.95)` no item ativo

2. **Transição:**
   - `transition: all 0.3s ease` (suave)
   - Animação de scale no ícone ativo

### **Acessibilidade:**

- **Tamanho Mínimo:** 44px × 44px (padrão iOS/Android)
- **Zona de Alcance:** Inferior da tela (perfeito para polegar)
- **Altura Total:** 64px (padrão iOS/Android)
- **Padding:** 0.5rem interno
- **Gap:** 0.25rem entre ícone e texto

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [x] Layout de lista vertical de cards definido
- [x] Design dos cards especificado
- [x] Modal de vídeo tela cheia especificado
- [x] Estilo visual da bottom navigation definido
- [x] Feedback visual e transições especificados
- [ ] Implementação no código (Dev)
- [ ] Testes em dispositivos reais
- [ ] Validação de acessibilidade

---

## 📝 PRÓXIMOS PASSOS

1. **Dev:** Implementar layout de cards conforme especificação
2. **Dev:** Implementar modal de vídeo tela cheia
3. **Dev:** Aplicar estilos da bottom navigation
4. **UX (Sally):** Validar protótipos
5. **Testes:** Usabilidade em dispositivos reais

---

**Versão:** 1.0  
**Status:** ✅ Aprovado  
**Próxima Revisão:** Após implementação
