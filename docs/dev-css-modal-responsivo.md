# CSS: Modal de Hospitais Responsivo

**Desenvolvedor:** James  
**Contexto:** Implementação de CSS responsivo para modal de hospitais  
**Objetivo:** Ajustar largura do modal para Desktop (60-70% ou max 1000px)

**Data:** {{date}}

---

## 📋 Visão Geral

### Problema
Modal de Hospitais está com largura fixa de Mobile (~400px) mesmo em Desktop, ficando muito estreito.

### Solução
Implementar media queries para ajustar largura do modal em diferentes breakpoints:
- **Mobile (≤767px):** Manter atual (90%, max 400px)
- **Tablet (768-1023px):** 85%, max 600px
- **Desktop (≥1024px):** 70%, max 1000px

---

## 💻 Código CSS

### CSS Completo (Substituir estilos existentes)

```css
/* ========================================
   MODAL DE HOSPITAIS - RESPONSIVO
   ======================================== */

/* Base do Modal (comporta todos os modais) */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    align-items: center;
    justify-content: center;
}

.modal.show {
    display: flex;
}

/* Modal Content - Base (Mobile First) */
.modal-content {
    background: white;
    border-radius: 15px;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

/* Modal de Hospitais - Específico (Mobile First) */
.modal-content.modal-hospitals,
.modal-hospitals .modal-content {
    max-width: 400px;  /* Mobile: max 400px */
    width: 90%;
}

/* ========================================
   TABLET (768px - 1023px)
   ======================================== */
@media (min-width: 768px) and (max-width: 1023px) {
    .modal-content.modal-hospitals,
    .modal-hospitals .modal-content {
        width: 85%;
        max-width: 600px;  /* Tablet: max 600px */
    }
}

/* ========================================
   DESKTOP (1024px+)
   ======================================== */
@media (min-width: 1024px) {
    .modal-content.modal-hospitals,
    .modal-hospitals .modal-content {
        width: 70%;  /* Desktop: 70% da largura */
        max-width: 1000px;  /* Desktop: max 1000px */
    }
    
    /* Cards de Hospital - Ajustes para Desktop */
    .hospital-card {
        width: 100% !important;
        padding: 1.5rem !important;  /* Mais espaço com largura maior */
    }
    
    /* Botões de Ação - Horizontal em Desktop */
    .hospital-actions {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 0.75rem !important;
    }
    
    .hospital-actions .btn-sophia-compact,
    .hospital-actions .hospital-call-btn,
    .hospital-actions .hospital-route-btn,
    .hospital-actions .hospital-map-btn {
        flex: 1 !important;
        min-width: 120px !important;  /* Garante tamanho mínimo adequado */
        max-width: none !important;
    }
}

/* ========================================
   DESKTOP LARGE (1400px+)
   ======================================== */
@media (min-width: 1400px) {
    .modal-content.modal-hospitals,
    .modal-hospitals .modal-content {
        width: 65%;  /* Desktop grande: 65% */
        max-width: 1000px;  /* Mantém max 1000px */
    }
}
```

---

## 🎯 Versão Alternativa (Seletor Mais Específico)

Se o modal de hospitais usar uma classe específica diferente, use esta versão:

```css
/* Modal de Hospitais - Base (Mobile) */
#hospitals-modal .modal-content,
.modal-content.modal-hospitals {
    max-width: 400px;
    width: 90%;
}

/* Tablet (768px - 1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
    #hospitals-modal .modal-content,
    .modal-content.modal-hospitals {
        width: 85%;
        max-width: 600px;
    }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
    #hospitals-modal .modal-content,
    .modal-content.modal-hospitals {
        width: 70%;
        max-width: 1000px;
    }
    
    /* Cards de Hospital */
    #hospitals-modal .hospital-card {
        width: 100% !important;
        padding: 1.5rem !important;
    }
    
    /* Botões - Horizontal */
    #hospitals-modal .hospital-actions {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 0.75rem !important;
    }
    
    #hospitals-modal .hospital-actions .btn-sophia-compact,
    #hospitals-modal .hospital-actions .hospital-call-btn,
    #hospitals-modal .hospital-actions .hospital-route-btn,
    #hospitals-modal .hospital-actions .hospital-map-btn {
        flex: 1 !important;
        min-width: 120px !important;
    }
}
```

---

## 🔍 Identificação da Classe

### Verificar no HTML
Para identificar a classe exata do modal de hospitais, verifique no HTML:

```html
<!-- Exemplo 1: Classe no modal-content -->
<div class="modal-content modal-hospitals">
    ...
</div>

<!-- Exemplo 2: ID no modal -->
<div class="modal" id="hospitals-modal">
    <div class="modal-content">
        ...
    </div>
</div>

<!-- Exemplo 3: Classe no container -->
<div class="modal hospitals-modal">
    <div class="modal-content">
        ...
    </div>
</div>
```

---

## 📊 Breakpoints Resumidos

| Breakpoint | Largura | Max-Width | Botões |
|------------|---------|-----------|--------|
| Mobile (≤767px) | 90% | 400px | Wrap (empilhado) |
| Tablet (768-1023px) | 85% | 600px | Wrap (tenta row) |
| Desktop (≥1024px) | 70% | 1000px | Row (horizontal) |

---

## ✅ Checklist de Implementação

### CSS
- [x] Media query para Tablet (768-1023px)
- [x] Media query para Desktop (≥1024px)
- [x] Ajuste de largura do modal
- [x] Ajuste de cards (width: 100%)
- [x] Ajuste de botões (row em Desktop)
- [ ] Testar em diferentes resoluções

### Validação
- [ ] Modal funciona em Mobile (mantém atual)
- [ ] Modal funciona em Tablet (largura intermediária)
- [ ] Modal funciona em Desktop (largura expandida)
- [ ] Botões ficam lado a lado em Desktop
- [ ] Botões não ficam excessivamente largos
- [ ] Cards aproveitam largura adequadamente

---

## 🔧 Ajustes Opcionais

### Se Botões Ficarem Muito Largos em Desktop

```css
@media (min-width: 1024px) {
    .hospital-actions .btn-sophia-compact {
        flex: 1;
        min-width: 120px;
        max-width: 200px;  /* Limita largura máxima */
    }
}
```

### Se Quiser Padding Adaptativo

```css
/* Mobile */
.hospital-card {
    padding: 1.25rem !important;
}

/* Desktop */
@media (min-width: 1024px) {
    .hospital-card {
        padding: 1.5rem !important;  /* Mais espaço */
    }
}
```

---

## 📝 Notas para Implementação

### Para @dev
- **Prioridade:** Identificar classe exata do modal de hospitais
- **Testar:** Em diferentes resoluções (Mobile, Tablet, Desktop)
- **Validar:** Botões não ficam muito largos
- **Garantir:** Transições suaves entre breakpoints

### Para @qa
- **Testar:** Modal em Mobile (≤767px)
- **Testar:** Modal em Tablet (768-1023px)
- **Testar:** Modal em Desktop (≥1024px)
- **Validar:** Botões se comportam corretamente
- **Verificar:** Cards aproveitam largura

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial: CSS responsivo para modal de hospitais | Dev (James) |
