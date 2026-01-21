# Especificação: Modal de Hospitais Responsivo

**UX Expert:** Sally  
**Contexto:** Problema de largura fixa do modal em Desktop  
**Objetivo:** Definir regras de redimensionamento responsivo para o modal de hospitais

**Data:** {{date}}

---

## 🎯 Problema Identificado

### Situação Atual
- Modal de Hospitais está com largura fixa de Mobile (~400px) mesmo em telas Desktop
- Modal fica muito estreito em Desktop
- Muito espaço sobrando nas laterais (overlay vazio)
- UX comprometida em telas grandes

### Objetivo
Criar sistema responsivo que adapte o modal para diferentes tamanhos de tela, aproveitando melhor o espaço disponível em Desktop.

---

## 📐 Breakpoints e Especificações

### Mobile (Padrão - até 767px)
**Comportamento:** Manter como está (atual)

- **Largura:** `width: 90%`
- **Max-width:** `max-width: 400px`
- **Layout:** Cards em coluna única
- **Botões:** Empilhados (flex-direction: column) ou wrap

---

### Tablet (768px - 1023px)
**Comportamento:** Intermediário

- **Largura:** `width: 85%`
- **Max-width:** `max-width: 600px`
- **Layout:** Cards em coluna única (largura maior)
- **Botões:** Opcional - pode começar a usar row com gap menor

---

### Desktop (1024px+)
**Comportamento:** Largura expandida (NOVO)

- **Largura:** `width: 70%` (ou 65-75% do viewport)
- **Max-width:** `max-width: 1000px`
- **Layout:** Cards esticam para aproveitar largura
- **Botões:** Horizontalmente (flex-direction: row) com gap adequado

---

## 🎨 Especificações Detalhadas

### Modal Container (.modal-content ou .modal-hospitals)

#### Mobile (até 767px)
```css
width: 90%;
max-width: 400px;
```

#### Tablet (768px - 1023px)
```css
width: 85%;
max-width: 600px;
```

#### Desktop (1024px+)
```css
width: 70%;
max-width: 1000px;
```

---

### Cards de Hospital (.hospital-card)

#### Mobile (até 767px)
- **Width:** `100%` do container (mantém atual)
- **Padding:** `1.25rem` (mantém atual)

#### Tablet (768px - 1023px)
- **Width:** `100%` do container
- **Padding:** `1.25rem` (mantém atual)

#### Desktop (1024px+)
- **Width:** `100%` do container (estica automaticamente)
- **Padding:** `1.5rem` (opcional - mais espaço com largura maior)
- **Layout:** Aproveita melhor a largura disponível

---

### Botões de Ação (.hospital-actions)

#### Mobile (até 767px)
- **Layout:** Flex wrap (permite empilhamento)
- **Direction:** `flex-wrap: wrap` (mantém atual)
- **Gap:** `0.5rem`
- **Botões:** Podem empilhar se necessário

#### Tablet (768px - 1023px)
- **Layout:** Flex wrap (ainda permite empilhamento)
- **Direction:** `flex-wrap: wrap`
- **Gap:** `0.75rem` (aumenta um pouco)
- **Botões:** Tentam ficar lado a lado se couber

#### Desktop (1024px+)
- **Layout:** Flex row (horizontal)
- **Direction:** `flex-direction: row` (ou manter wrap com gap maior)
- **Gap:** `0.75rem` a `1rem`
- **Botões:** Ficam lado a lado (não empilham)
- **Width dos botões:** `flex: 1` (distribuem espaço igualmente) OU `min-width: 120px` + `flex: 1`

---

## 📊 Matriz de Decisão

| Breakpoint | Modal Width | Modal Max-Width | Card Width | Botões Layout |
|------------|-------------|-----------------|------------|---------------|
| Mobile (≤767px) | 90% | 400px | 100% | Wrap (empilhado) |
| Tablet (768-1023px) | 85% | 600px | 100% | Wrap (tenta row) |
| Desktop (≥1024px) | 70% | 1000px | 100% | Row (horizontal) |

---

## 🎯 Recomendações de UX

### Desktop (1024px+)

#### Botões em Row
- **Vantagem:** Melhor aproveitamento do espaço horizontal
- **Vantagem:** Visual mais limpo e profissional
- **Consideração:** Garantir que botões não fiquem muito largos (usar max-width se necessário)

#### Layout Sugerido
```
┌─────────────────────────────────────────┐
│  Modal Header                           │
├─────────────────────────────────────────┤
│  [Alerta]                               │
│  [Card Hospital]                        │
│  ┌───────────────────────────────────┐ │
│  │ [Ligar] [Rota] [Ver Mapa]        │ │ ← Botões lado a lado
│  └───────────────────────────────────┘ │
│  [Card Hospital]                        │
│  ┌───────────────────────────────────┐ │
│  │ [Ligar] [Rota] [Ver Mapa]        │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Mobile (até 767px)

#### Botões em Wrap (Atual)
- **Vantagem:** Botões ficam com tamanho adequado
- **Vantagem:** Não ficam muito pequenos ou muito largos
- **Mantém:** Comportamento atual (já funciona bem)

---

## ✅ Checklist de Validação

### Desktop
- [ ] Modal ocupa 60-70% da largura (ou max 1000px)
- [ ] Cards esticam para aproveitar largura
- [ ] Botões ficam lado a lado (row)
- [ ] Botões não ficam excessivamente largos
- [ ] Espaçamento adequado entre elementos

### Tablet
- [ ] Modal ocupa 85% da largura (ou max 600px)
- [ ] Cards se adaptam à largura
- [ ] Botões funcionam bem (wrap ou row)

### Mobile
- [ ] Modal mantém comportamento atual (90%, max 400px)
- [ ] Cards e botões funcionam como antes

---

## 📝 Notas para Implementação

### Para @dev
- **Prioridade:** Implementar media queries para Desktop (≥1024px)
- **Testar:** Modal em diferentes tamanhos de tela
- **Validar:** Botões não ficam muito largos em Desktop
- **Garantir:** Transições suaves entre breakpoints

### Para @qa
- **Testar:** Modal em Mobile, Tablet e Desktop
- **Validar:** Botões se comportam corretamente em cada breakpoint
- **Verificar:** Cards aproveitam largura adequadamente

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial: Especificação de responsividade do modal | UX Expert (Sally) |
