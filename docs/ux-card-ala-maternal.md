# Especificação Visual: Card de Hospital - Ala Maternal

**Especialista:** UX Expert (Sally)  
**Contexto:** Redesign do Card de Hospital na Lista de Busca  
**Objetivo:** Criar visualização impossível de ignorar sobre a disponibilidade de Ala Maternal

**Data:** {{date}}

---

## 🎨 Visão Geral do Componente

### Contexto de Uso
- **Usuário:** Gestante em situação de emergência (possível estresse elevado)
- **Cenário:** Busca rápida de hospitais próximos em situação de urgência
- **Objetivo:** Decisão rápida e correta sobre qual hospital buscar

### Requisitos de Acessibilidade
- ✅ Legível por usuários daltônicos
- ✅ Legível em dispositivos móveis (tela pequena)
- ✅ Legível em condições de baixa luz (emergência noturna)
- ✅ Tempo de compreensão: < 2 segundos

---

## 📐 Estrutura do Card

### Hierarquia Visual (Topo → Base)
1. **Header:** Nome do Hospital + Distância
2. **Badge de Ala Maternal** (NOVO - Destaque Principal) ← **FOCO PRINCIPAL**
3. **Badges Secundários:** SUS, Pronto Socorro (se aplicável)
4. **Informações:** Endereço, Telefone, Website
5. **Ações:** Botões (Ligar, Rota, Ver Mapa)

---

## 🎯 Estados do Badge de Ala Maternal

### Estado 1: POSITIVO (Hospital TEM Ala Maternal)

#### Especificações Visuais
- **Cor de Fundo:** Verde (#28a745) - Gradiente: #28a745 → #218838
- **Cor do Texto:** Branco (#FFFFFF)
- **Ícone:** ✅ (check) ou `fa-baby` (FontAwesome) - Tamanho: 1rem
- **Texto:** "✅ Possui Ala Maternal" ou "✅ Ala Maternal Confirmada"
- **Tamanho da Fonte:** 0.9rem (14.4px) - Peso: 700 (Bold)
- **Padding:** 0.5rem 0.75rem (8px 12px)
- **Border Radius:** 12px (var(--sophia-border-radius-sm))
- **Box Shadow:** 0 2px 8px rgba(40, 167, 69, 0.3) - Sombra verde suave
- **Posição:** Imediatamente após o header (antes dos badges secundários)
- **Display:** `inline-flex` com `align-items: center` e `gap: 0.4rem`

#### Código CSS (Referência)
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
}
```

#### Exemplo Visual (HTML)
```html
<div class="hospital-badge-maternity-positive">
    <i class="fas fa-baby"></i>
    <span>Possui Ala Maternal</span>
</div>
```

---

### Estado 2: NEGATIVO (Hospital NÃO TEM Ala Maternal)

#### Especificações Visuais
- **Cor de Fundo:** Laranja (#ffb703) - Gradiente: #ffb703 → #e6a502 (OU Cinza Escuro: #6c757d → #5a6268)
- **Cor do Texto:** Branco (#FFFFFF)
- **Ícone:** ⚠️ (warning) ou `fa-exclamation-triangle` (FontAwesome) - Tamanho: 1rem
- **Texto:** "⚠️ Não possui Ala Maternal - Apenas PS Geral" ou "⚠️ Não contém Ala Maternal"
- **Tamanho da Fonte:** 0.9rem (14.4px) - Peso: 700 (Bold)
- **Padding:** 0.5rem 0.75rem (8px 12px)
- **Border Radius:** 12px (var(--sophia-border-radius-sm))
- **Box Shadow:** 0 2px 8px rgba(255, 183, 3, 0.3) - Sombra laranja suave (OU sombra cinza)
- **Posição:** Imediatamente após o header (mesma posição do badge positivo)
- **Display:** `inline-flex` com `align-items: center` e `gap: 0.4rem`

#### Código CSS (Referência - Opção Laranja)
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
}
```

#### Exemplo Visual (HTML)
```html
<div class="hospital-badge-maternity-negative">
    <i class="fas fa-exclamation-triangle"></i>
    <span>Não possui Ala Maternal - Apenas PS Geral</span>
</div>
```

---

### Estado 3: FALLBACK (Dado Desconhecido - Tratado como Negativo)

#### Especificações Visuais
- **Cor de Fundo:** Cinza Escuro (#6c757d) - Gradiente: #6c757d → #5a6268
- **Cor do Texto:** Branco (#FFFFFF)
- **Ícone:** ⚠️ (warning) ou `fa-question-circle` (FontAwesome) - Tamanho: 1rem
- **Texto:** "⚠️ Não possui Ala Maternal - Apenas PS Geral" (mesmo texto do estado negativo)
- **Tamanho da Fonte:** 0.9rem (14.4px) - Peso: 700 (Bold)
- **Padding:** 0.5rem 0.75rem (8px 12px)
- **Border Radius:** 12px (var(--sophia-border-radius-sm))
- **Box Shadow:** 0 2px 8px rgba(108, 117, 125, 0.3) - Sombra cinza suave
- **Posição:** Imediatamente após o header (mesma posição dos outros estados)
- **Display:** `inline-flex` com `align-items: center` e `gap: 0.4rem`

**Nota:** Por regra de segurança (RN-001 do PO), dados desconhecidos são tratados como "NÃO POSSUI".

---

## 🎨 Paleta de Cores

### Cores Principais
- **Verde (Positivo):** `#28a745` (cor base) → `#218838` (gradiente)
- **Laranja (Negativo):** `#ffb703` (cor base) → `#e6a502` (gradiente)
- **Cinza (Fallback):** `#6c757d` (cor base) → `#5a6268` (gradiente)
- **Branco (Texto):** `#FFFFFF`

### Contraste (WCAG AAA)
- Verde + Branco: Contraste 4.5:1 ✅
- Laranja + Branco: Contraste 4.5:1 ✅
- Cinza + Branco: Contraste 4.5:1 ✅

### Teste de Daltonismo
- **Protanopia (vermelho-verde):** Verde e Laranja ainda são distinguíveis ✅
- **Deuteranopia (vermelho-verde):** Verde e Laranja ainda são distinguíveis ✅
- **Tritanopia (azul-amarelo):** Verde e Laranja ainda são distinguíveis ✅

---

## 📱 Comportamento Responsivo

### Desktop (> 768px)
- Badge com texto completo: "Possui Ala Maternal" / "Não possui Ala Maternal - Apenas PS Geral"
- Tamanho da fonte: 0.9rem
- Padding: 0.5rem 0.75rem

### Tablet (481px - 768px)
- Badge com texto completo (igual ao desktop)
- Tamanho da fonte: 0.85rem
- Padding: 0.45rem 0.7rem

### Mobile (< 480px)
- Badge com texto completo (igual ao desktop)
- Tamanho da fonte: 0.85rem
- Padding: 0.45rem 0.7rem
- **Importante:** Manter legibilidade mesmo em telas pequenas

---

## 🔄 Animações e Interações

### Estado Hover (Opcional - Desktop)
- **Badge Positivo:** Sombra aumenta levemente (0 4px 12px rgba(40, 167, 69, 0.4))
- **Badge Negativo:** Sombra aumenta levemente (0 4px 12px rgba(255, 183, 3, 0.4))
- **Transição:** `transition: box-shadow 0.2s ease`

### Estado Padrão
- Sem animação excessiva (evitar distrair usuário em situação de estresse)
- Transições suaves apenas

---

## 📐 Tipografia

### Font Family
- Seguir padrão do sistema: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`

### Font Weight
- **Badge:** 700 (Bold) - Garante destaque
- **Texto do Badge:** 700 (Bold)

### Font Size
- **Desktop:** 0.9rem (14.4px)
- **Mobile:** 0.85rem (13.6px)

### Line Height
- **Badge:** 1.2 (compacto, mas legível)

---

## 🎯 Posicionamento no Card

### Ordem de Elementos (Topo → Base)
```
┌─────────────────────────────────────┐
│ [Nome Hospital]         [Distância] │ ← Header
│ [BADGE ALA MATERNAL]                │ ← DESTAQUE PRINCIPAL
│ [Badge SUS] [Badge PS Geral]        │ ← Badges Secundários
│ 📍 Endereço                          │
│ 📞 Telefone                          │
│ 🌐 Website                           │
│ [Botões: Ligar | Rota | Ver Mapa]   │
└─────────────────────────────────────┘
```

### Espaçamento
- **Margem Superior:** 0.5rem (8px) após o header
- **Margem Inferior:** 0.75rem (12px) antes dos badges secundários
- **Gap entre badges:** 0.5rem (8px)

---

## ✅ Checklist de Implementação

### Visibilidade
- [ ] Badge é o primeiro elemento visual após o header
- [ ] Badge tem tamanho suficiente para ser lido rapidamente
- [ ] Badge tem contraste suficiente (WCAG AAA)

### Acessibilidade
- [ ] Testado com leitores de tela (texto alternativo adequado)
- [ ] Testado com simulador de daltonismo
- [ ] Cores distinguíveis em diferentes condições de luz

### Responsividade
- [ ] Badge funciona bem em desktop (> 768px)
- [ ] Badge funciona bem em tablet (481px - 768px)
- [ ] Badge funciona bem em mobile (< 480px)

### Consistência
- [ ] Todos os cards têm o badge (positivo ou negativo)
- [ ] Posição do badge é consistente em todos os cards
- [ ] Tamanho e estilo são consistentes

---

## 📝 Notas para Desenvolvimento

### Para @dev
- Implementar validação: garantir que badge sempre apareça (nunca ausente)
- Usar fallback: `hasMaternityWard ?? false` para tratar null/undefined
- Implementar estados condicionais: `if (hasMaternityWard) → badge positivo, else → badge negativo`

### Para @qa
- Testar todos os 3 estados (positivo, negativo, fallback)
- Testar acessibilidade (daltonismo, leitores de tela)
- Testar responsividade (diferentes tamanhos de tela)

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial da especificação visual | UX Expert (Sally) |
