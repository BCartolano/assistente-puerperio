# Especificação: Correção de Layout do Header

**UX Expert:** Sally  
**Contexto:** Violação de heurística visual - botão sobrepondo logo  
**Objetivo:** Definir especificação de design para corrigir sobreposição

**Data:** {{date}}

---

## 🎯 Problema Identificado

### Violação de Heurística Visual
O botão de menu (`#menu-toggle-header`) está sobrepondo o elemento de branding (`.header-logo-text` - texto "Sophia"), prejudicando:
- **Legibilidade:** Texto do logo fica parcialmente ou completamente oculto
- **Estética:** Visual desorganizado e não profissional
- **Usabilidade:** Área de toque do botão interfere na leitura do logo

---

## 📐 Análise do Layout Atual

### Estrutura HTML (Referência)
```html
<div class="header-left">
    <button id="menu-toggle-header">...</button>
    <div class="header-logo">
        <h1 class="header-logo-text">Sophia</h1>
    </div>
</div>
```

### Problema Visual
- Botão (`#menu-toggle-header`): Largura 40px
- Logo (`.header-logo-text`): Texto "Sophia"
- **Sobreposição:** Botão pode estar sobre o texto

---

## 🎨 Especificação de Design

### Layout Correto (Flexbox)

#### Container Pai (`.header-left`)
- **Display:** `flex`
- **Align-items:** `center` (alinhamento vertical)
- **Gap:** `12px` a `16px` (espaçamento entre botão e logo)
- **Justify-content:** `flex-start` (alinhamento horizontal à esquerda)

### Espaçamento Ideal

#### Gap Recomendado: `12px` a `16px`

**Justificativa:**
- **12px (mínimo):** Espaçamento confortável sem desperdiçar espaço
- **16px (ideal):** Espaço visual agradável e respiração adequada
- **Gap em vez de margin:** Mais limpo e semântico com Flexbox

### Área de Toque

#### Botão (`#menu-toggle-header`)
- **Largura:** `40px` (mantém)
- **Altura:** `40px` (mantém)
- **Área de toque:** Mínimo 44x44px (acessibilidade mobile)
- **Espaçamento:** Gap de 12-16px garante que área de toque não invada logo

---

## 📊 Especificações Detalhadas

### Container: `.header-left`

```css
.header-left {
    display: flex;
    align-items: center;
    gap: 15px; /* Espaçamento entre botão e logo */
    flex: 0 0 auto;
}
```

### Botão: `#menu-toggle-header`

```css
#menu-toggle-header {
    flex-shrink: 0; /* Não encolhe */
    width: 40px;
    height: 40px;
    min-width: 40px;
    min-height: 40px;
}
```

### Logo: `.header-logo-text`

```css
.header-logo-text {
    flex: 0 0 auto; /* Não encolhe nem estica */
    margin: 0;
    padding: 0;
    white-space: nowrap; /* Evita quebra de linha */
}
```

---

## 🎯 Validação Visual

### Checklist de Heurísticas
- ✅ **Separação Visual:** Botão e logo têm espaço claro entre eles
- ✅ **Legibilidade:** Texto "Sophia" completamente visível
- ✅ **Área de Toque:** Botão tem área clicável adequada (44x44px mínimo)
- ✅ **Alinhamento:** Botão e logo alinhados verticalmente (center)
- ✅ **Consistência:** Espaçamento consistente em todas as resoluções

### Métricas de Sucesso
- **Gap mínimo:** 12px entre botão e logo
- **Sem sobreposição:** 0 pixels de interseção entre elementos
- **Área de toque:** Mínimo 44x44px para acessibilidade
- **Alinhamento vertical:** Centralizado (align-items: center)

---

## 📱 Responsividade

### Mobile (≤768px)
- **Gap:** `12px` (economia de espaço)
- **Layout:** Flexbox row (botão + logo lado a lado)

### Desktop (≥769px)
- **Gap:** `15px` a `16px` (mais espaço visual)
- **Layout:** Flexbox row (botão + logo lado a lado)

---

## ✅ Checklist de Implementação

### Layout
- [x] Container `.header-left` usa Flexbox
- [x] Gap de 12-16px entre botão e logo
- [x] Alinhamento vertical (center)
- [x] Sem sobreposição de elementos
- [x] Área de toque adequada (44x44px)

### Visual
- [x] Logo completamente visível
- [x] Espaçamento visual agradável
- [x] Layout limpo e profissional
- [x] Consistência entre breakpoints

---

## 📝 Notas para Implementação

### Para @dev
- **Prioridade:** Usar Flexbox com gap (não margin)
- **Gap recomendado:** 15px (equilíbrio entre espaço e economia)
- **Garantir:** Sem position: absolute que cause sobreposição
- **Validar:** Sem interseção de pixels entre elementos

### Para @qa
- **Testar:** Botão e logo não se sobrepõem
- **Validar:** Gap visível e adequado
- **Verificar:** Área de toque do botão funcional
- **Confirmar:** Alinhamento vertical correto

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial: Especificação de layout do header | UX Expert (Sally) |
