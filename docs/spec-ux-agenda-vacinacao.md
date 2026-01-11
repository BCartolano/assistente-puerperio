# Especificação UX - Agenda de Vacinação Interativa

**UX Expert:** Sally  
**Data:** 2025-01-08  
**Contexto:** Backend implementado, necessitamos diretrizes de interface Desktop

---

## 🎯 OBJETIVO

Criar uma experiência visual acolhedora e empoderadora para a Agenda de Vacinação, transformando uma "tabela de hospital" fria em uma **jornada de proteção** visualmente rica e emocionalmente conectada.

---

## 🎨 PRINCÍPIOS DE DESIGN

### 1. Calor e Acolhimento
- Usar paleta quente existente (#ff8fa3, #ffb3c6, #ffe8f0)
- Evitar cores frias ou hospitalares
- Transmitir sensação de cuidado e proteção

### 2. Empoderamento da Mãe
- Visualizar progresso claramente
- Celebrar conquistas (vacinas aplicadas)
- Reduzir ansiedade sobre "estar atrasada"

### 3. Clareza e Simplicidade
- Informação fácil de entender
- Visualização imediata do que é próximo
- Reduzir sobrecarga cognitiva

---

## 📐 COMPONENTE TIMELINE CENTRAL

### Estrutura Visual

```
┌─────────────────────────────────────────────────────┐
│  💉 JORNADA DE PROTEÇÃO - [Nome do Bebê]            │
│  ─────────────────────────────────────────────────  │
│                                                      │
│  ✅ AO NASCER                                        │
│  ┌─────────────────────────────────────────┐        │
│  │ ✓ BCG              [Aplicada em 15/01]  │        │
│  │ ✓ Hepatite B       [Aplicada em 15/01]  │        │
│  └─────────────────────────────────────────┘        │
│                                                      │
│  📅 2 MESES (15/03/2025 - Falta 30 dias)           │
│  ┌─────────────────────────────────────────┐        │
│  │ ⏳ Pentavalente    [Pendente]            │        │
│  │ ⏳ VIP             [Pendente]            │        │
│  │ ⏳ Rotavírus       [Pendente]            │        │
│  │ ⏳ Pneumocócica    [Pendente]            │        │
│  └─────────────────────────────────────────┘        │
│                                                      │
│  🔜 PRÓXIMA VACINA                                   │
│  ⭐ Pentavalente - 1ª dose                           │
│  📅 15/03/2025 (em 30 dias)                         │
│  💡 Protege contra: Difteria, Tétano, Coqueluche... │
│  [Marcar como Aplicada]                              │
│                                                      │
│  📊 PROGRESSO GERAL                                  │
│  ████████░░░░░░░░ 40% (2 de 5 vacinas aplicadas)    │
└─────────────────────────────────────────────────────┘
```

### Estados Visuais

#### ✅ Vacina Concluída
- **Cor:** Verde suave (#c4d5a0) ou cor quente (#ff8fa3) com opacidade
- **Ícone:** ✓ (check) ou 🎉
- **Card:** Fundo claro, borda suave
- **Informação:** Data aplicada, local (se informado)

#### ⏳ Vacina Pendente
- **Cor:** Cinza suave (#e0e0e0) ou cor quente translúcida
- **Ícone:** ⏳ ou 📅
- **Card:** Fundo translúcido, borda pontilhada
- **Informação:** Data recomendada, dias até a vacina

#### 🔜 Próxima Vacina (Destaque)
- **Cor:** Destaque com cor quente (#ff8fa3) ou gradiente
- **Ícone:** ⭐ ou 🔜
- **Card:** Destaque visual (sombra, borda mais forte)
- **Botão:** "Marcar como Aplicada" (destaque)
- **Badge:** "Próxima em X dias"

#### ⚠️ Vacina Atrasada
- **Cor:** Laranja suave (#e07a5f) - não alarmante
- **Ícone:** ⚠️
- **Card:** Borda laranja, fundo amarelado suave
- **Mensagem:** "Recomendada em [data], mas ainda pode ser aplicada"

---

## 🎉 FEEDBACK DE COMEMORAÇÃO

### Quando Marcar Vacina como Aplicada

#### 1. Animação de Sucesso
```
┌─────────────────────────────────────┐
│                                     │
│        🎉  ✨  🎊                    │
│                                     │
│   Vacina Aplicada com Sucesso!      │
│                                     │
│   Parabéns! Você está cuidando      │
│   perfeitamente do [Nome do Bebê]!  │
│                                     │
│        💉 ✨ 🤱                      │
│                                     │
│   [Fechar]                          │
└─────────────────────────────────────┘
```

**Elementos:**
- Modal centralizado com glassmorphism
- Confetes animados caindo (CSS animation)
- Ícones animados (pulsação, rotação suave)
- Mensagem personalizada com nome do bebê
- Cor de fundo: Gradiente quente (#ffe8f0 → #ffb3c6)

#### 2. Atualização do Progresso
- Barra de progresso anima até novo percentual
- Contador de vacinas concluídas aumenta
- Timeline atualiza visualmente (pendente → concluída)

#### 3. Micro-interações
- Botão "Marcar como Aplicada" com feedback hover
- Ícone de check aparece com animação de escala
- Cores mudam suavemente (pendente → concluída)

---

## 📱 RESPONSIVIDADE

### Desktop (≥1024px)
- Timeline vertical completa visível
- Cards lado a lado quando possível (grid)
- Sidebar direita: Próximas vacinas resumidas
- Sidebar esquerda: Estatísticas rápidas

### Tablet (768px - 1023px)
- Timeline vertical compacta
- Cards empilhados
- Sidebars ocultas ou colapsáveis

### Mobile (<768px)
- Timeline vertical simplificada
- Cards full-width
- Apenas "Próxima Vacina" visível inicialmente
- Botão "Ver Todas" para expandir

---

## 🎨 PALETA DE CORES APLICADA

### Status de Vacina
- **Concluída:** #c4d5a0 (Verde Sálvia) - 80% opacidade
- **Pendente:** #e0e0e0 (Cinza suave) ou #ffb3c6 (Pêssego) - 30% opacidade
- **Próxima:** #ff8fa3 (Coral) - 100% opacidade
- **Atrasada:** #e07a5f (Terracota) - 100% opacidade

### Backgrounds
- **Timeline:** #ffffff (branco) ou #ffe8f0 (creme) muito claro
- **Cards concluídas:** #ffe8f0 (creme) - 50% opacidade
- **Card próxima:** Gradiente #ffe8f0 → #ffb3c6

---

## 💡 ELEMENTOS VISUAIS ADICIONAIS

### Ícones Decorativos
- 💉 Seringa (vacinas)
- 🎉 Confete (comemoração)
- ⭐ Estrela (próxima vacina)
- ✓ Check (aplicada)
- ⏳ Relógio (pendente)
- 🤱 Bebê (proteção)

### Ilustrações SVG (Futuro)
- Vacina com "escudo" de proteção
- Bebê sorrindo com super-herói
- Caminho/jornada visual

---

## 📐 ESPECIFICAÇÕES TÉCNICAS

### CSS Classes Sugeridas

```css
.vaccination-timeline {
    /* Container principal da timeline */
}

.vaccine-card {
    /* Card individual de vacina */
}

.vaccine-card.completed {
    /* Estado: Concluída */
}

.vaccine-card.pending {
    /* Estado: Pendente */
}

.vaccine-card.next {
    /* Estado: Próxima (destaque) */
}

.vaccine-card.overdue {
    /* Estado: Atrasada */
}

.celebration-modal {
    /* Modal de comemoração */
}

.progress-bar {
    /* Barra de progresso geral */
}
```

### Animações CSS

```css
@keyframes confetti-fall {
    /* Confetes caindo */
}

@keyframes pulse-check {
    /* Pulsação do ícone de check */
}

@keyframes slide-in {
    /* Slide-in do card quando marca como aplicada */
}
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Estrutura Base
- [ ] Criar componente Timeline
- [ ] Implementar cards de vacina
- [ ] Estados visuais (concluída, pendente, próxima)
- [ ] Responsividade básica

### Fase 2: Interatividade
- [ ] Botão "Marcar como Aplicada"
- [ ] Modal de comemoração
- [ ] Atualização do progresso
- [ ] Animações básicas

### Fase 3: Refinamentos
- [ ] Confetes animados
- [ ] Micro-interações
- [ ] Ícones decorativos
- [ ] Polimento visual

---

## 📊 MÉTRICAS DE SUCESSO UX

1. **Clareza:** Mãe entende imediatamente quais vacinas já foram aplicadas
2. **Motivação:** Visualização de progresso incentiva continuidade
3. **Redução de Ansiedade:** Cores quentes e mensagens positivas
4. **Celebração:** Feedback visual reforça comportamento positivo
5. **Acesso Rápido:** Próxima vacina facilmente identificável

---

**Especificação criada por:** Sally (UX Expert)  
**Data:** 2025-01-08  
**Versão:** 1.0  
**Status:** Pronto para implementação frontend
