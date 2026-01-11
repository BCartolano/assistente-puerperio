# Sprint UX-1: Visual & Calor - Plano de Tarefas Detalhado

**Product Owner:** Sarah (PO)  
**Sprint:** UX-1 (Visual & Calor)  
**Duração:** 2 semanas (10 dias úteis)  
**Objetivo:** Implementar nova paleta de cores quentes e melhorar sensação visual de acolhimento  
**Baseado em:** `ANALISE_UX_VISUAL_SOPHIA.md` - Fase 1

---

## 📋 RESUMO DA SPRINT

**Requisitos Relacionados:**
- FR16: Paleta de cores quentes e acolhedoras
- NFR8.2: Paleta de cores que transmita sensação de calor e acolhimento

**Entregáveis:**
- ✅ Nova paleta de cores implementada
- ✅ Gradientes quentes aplicados
- ✅ Ícones decorativos animados funcionando
- ✅ Visual mais acolhedor e caloroso

**Definição de Pronto (DoD):**
- [ ] Código revisado
- [ ] Testes visuais em diferentes navegadores (Chrome, Firefox, Safari, Edge)
- [ ] Responsividade mantida (mobile, tablet, desktop)
- [ ] Performance de renderização validada
- [ ] Documentação de cores atualizada
- [ ] Validação visual com equipe/PO

---

## 🎯 TAREFAS DETALHADAS

### Tarefa 1: Configurar Variáveis CSS para Nova Paleta

**Responsável:** Dev  
**Prioridade:** 🔴 CRÍTICA  
**Estimativa:** 2 horas  
**Tipo:** Frontend - CSS

**Descrição:**
Criar arquivo de variáveis CSS (ou atualizar existente) com todas as cores quentes propostas pela análise de UX.

**Entrada:**
- `ANALISE_UX_VISUAL_SOPHIA.md` - Seção "Recomendações: Paleta de Cores Mais Acolhedora"

**Ações:**
1. Localizar arquivo CSS principal (`backend/static/css/style.css`)
2. Criar ou atualizar seção `:root` com variáveis CSS para cores:
   - `--color-primary-warm: #ff8fa3;`
   - `--color-primary-soft: #ffb3c6;`
   - `--color-accent-peach: #ffccd5;`
   - `--color-accent-cream: #ffe8f0;`
   - `--bg-warm-1: #fff5f9;`
   - `--bg-warm-2: #ffeef5;`
   - `--bg-warm-3: #ffe8f0;`
   - `--color-golden: #ffd89b;`
   - `--color-sage: #c4d5a0;`
   - `--color-terracotta: #e07a5f;`
   - `--text-warm-dark: #6b4a3f;`
   - `--text-warm-medium: #8b6a5a;`
   - `--text-accent: #a84a5f;`
3. Documentar cada variável com comentário explicando uso

**Saída:**
- Arquivo CSS com variáveis definidas
- Cores organizadas por categoria (primárias, fundo, destaque, texto)

**Critérios de Aceite:**
- [ ] Todas as variáveis de cor definidas em `:root`
- [ ] Variáveis documentadas com comentários
- [ ] Código validado sem erros de sintaxe CSS

**Arquivos Afetados:**
- `backend/static/css/style.css`

---

### Tarefa 2: Atualizar Gradiente de Fundo Principal

**Responsável:** Dev  
**Prioridade:** 🔴 CRÍTICA  
**Estimativa:** 1.5 horas  
**Tipo:** Frontend - CSS

**Descrição:**
Substituir gradiente de fundo atual por gradiente quente proposto, aplicando em elementos de background da página.

**Entrada:**
- Análise UX - Gradiente proposto:
```css
background: linear-gradient(
    135deg,
    #fff5f9 0%,      /* Branco rosado */
    #ffeef5 25%,     /* Rosa creme */
    #ffe8f0 50%,     /* Pêssego claro */
    #ffd6e6 75%,     /* Rosa pêssego */
    #ffccd5 100%     /* Coral claro */
);
```

**Ações:**
1. Localizar seletor do elemento de fundo principal (provavelmente `body` ou `.welcome-message`)
2. Substituir gradiente atual pelo novo gradiente quente
3. Usar variáveis CSS quando possível (`--bg-warm-1`, `--bg-warm-2`, etc.)
4. Testar visualmente em diferentes resoluções
5. Verificar contraste com texto para legibilidade

**Saída:**
- Gradiente de fundo atualizado
- Visual mais quente e acolhedor

**Critérios de Aceite:**
- [ ] Gradiente quente aplicado corretamente
- [ ] Transição suave entre cores
- [ ] Contraste adequado para legibilidade do texto
- [ ] Visual consistente em diferentes resoluções

**Arquivos Afetados:**
- `backend/static/css/style.css`

**Testes:**
- Verificar em Chrome, Firefox, Safari, Edge
- Validar em mobile (320px), tablet (768px), desktop (1920px)

---

### Tarefa 3: Atualizar Cores Primárias (Header, Botões, Links)

**Responsável:** Dev  
**Prioridade:** 🔴 CRÍTICA  
**Estimativa:** 2 horas  
**Tipo:** Frontend - CSS

**Descrição:**
Atualizar cores primárias de elementos interativos (header, botões, links) para usar a nova paleta quente.

**Entrada:**
- Análise UX - Cores primárias propostas

**Ações:**
1. Identificar elementos que usam cor primária atual (`#f4a6a6`):
   - Header/logo
   - Botões principais
   - Links de ação
   - Botões de envio
2. Substituir por `--color-primary-warm: #ff8fa3` (rosa coral vibrante)
3. Atualizar estados hover/active com `--color-primary-soft: #ffb3c6`
4. Aplicar gradiente em botões quando apropriado:
```css
background: linear-gradient(135deg, #ff8fa3 0%, #ffb3c6 100%);
```
5. Testar estados de interação (hover, active, focus)

**Saída:**
- Header atualizado com nova cor
- Botões com gradiente quente
- Links com cores vibrantes

**Critérios de Aceite:**
- [ ] Header usa `--color-primary-warm`
- [ ] Botões principais usam gradiente quente
- [ ] Estados hover/active funcionam corretamente
- [ ] Contraste adequado para acessibilidade (WCAG AA mínimo)
- [ ] Visual consistente em todos os elementos

**Arquivos Afetados:**
- `backend/static/css/style.css`

**Testes:**
- Verificar todos os estados de botões (normal, hover, active, focus)
- Validar contraste com ferramenta de acessibilidade (WebAIM)

---

### Tarefa 4: Atualizar Cores de Texto para Tons Quentes

**Responsável:** Dev  
**Prioridade:** 🟡 ALTA  
**Estimativa:** 1 hora  
**Tipo:** Frontend - CSS

**Descrição:**
Atualizar cores de texto para usar tons quentes de marrom, mantendo legibilidade.

**Entrada:**
- Análise UX - Cores de texto propostas

**Ações:**
1. Identificar elementos de texto:
   - Texto principal: `--text-warm-dark: #6b4a3f`
   - Texto secundário: `--text-warm-medium: #8b6a5a`
   - Links/destaque: `--text-accent: #a84a5f`
2. Substituir cores de texto atuais (`#5a4a42`, `#8b5a5a`)
3. Verificar contraste com fundo atualizado
4. Ajustar se necessário para manter legibilidade

**Saída:**
- Cores de texto atualizadas
- Melhor harmonia com fundo quente

**Critérios de Aceite:**
- [ ] Texto principal usa `--text-warm-dark`
- [ ] Texto secundário usa `--text-warm-medium`
- [ ] Links usam `--text-accent`
- [ ] Contraste WCAG AA garantido
- [ ] Legibilidade mantida em todos os contextos

**Arquivos Afetados:**
- `backend/static/css/style.css`

**Testes:**
- Validar contraste com WebAIM Contrast Checker
- Testar em diferentes fundos (cards, gradiente, branco)

---

### Tarefa 5: Criar Estrutura HTML para Ícones Decorativos

**Responsável:** Dev  
**Prioridade:** 🟡 ALTA  
**Estimativa:** 1.5 horas  
**Tipo:** Frontend - HTML

**Descrição:**
Criar estrutura HTML para ícones decorativos flutuantes nas laterais da página.

**Entrada:**
- Análise UX - Elementos visuais propostos
- Ícones sugeridos: 💕, 🌸, ✨, 🌙, 🤱, 💫

**Ações:**
1. Localizar template principal (`backend/templates/index.html`)
2. Encontrar seção `.welcome-message` ou elemento principal
3. Criar container `.desktop-side-decorations` dentro da seção
4. Adicionar estrutura para coluna esquerda e direita:
```html
<div class="desktop-side-decorations">
    <!-- Coluna Esquerda -->
    <div class="side-decoration side-left">
        <div class="floating-icon icon-1" aria-hidden="true">💕</div>
        <div class="floating-icon icon-2" aria-hidden="true">🌸</div>
        <div class="floating-icon icon-3" aria-hidden="true">🤱</div>
        <div class="decoration-shape shape-1"></div>
        <div class="decoration-shape shape-2"></div>
    </div>
    
    <!-- Coluna Direita -->
    <div class="side-decoration side-right">
        <div class="floating-icon icon-4" aria-hidden="true">✨</div>
        <div class="floating-icon icon-5" aria-hidden="true">🌙</div>
        <div class="floating-icon icon-6" aria-hidden="true">💫</div>
        <div class="decoration-shape shape-3"></div>
        <div class="decoration-shape shape-4"></div>
    </div>
</div>
```
5. Adicionar `aria-hidden="true"` para acessibilidade (elementos decorativos)

**Saída:**
- Estrutura HTML criada
- Ícones e formas posicionados

**Critérios de Aceite:**
- [ ] Estrutura HTML criada corretamente
- [ ] Ícones organizados por coluna
- [ ] Atributos de acessibilidade aplicados
- [ ] Código semanticamente correto

**Arquivos Afetados:**
- `backend/templates/index.html`

**Nota:** Ícones podem ser emojis ou Font Awesome icons. Para melhor performance e controle visual, considerar usar Font Awesome.

---

### Tarefa 6: Implementar Estilos CSS para Ícones Flutuantes

**Responsável:** Dev  
**Prioridade:** 🟡 ALTA  
**Estimativa:** 2 horas  
**Tipo:** Frontend - CSS

**Descrição:**
Criar estilos CSS para ícones decorativos flutuantes com animações suaves.

**Entrada:**
- Estrutura HTML criada na Tarefa 5
- Análise UX - Especificações de animação

**Ações:**
1. Criar estilos base para `.floating-icon`:
   - Posicionamento absoluto
   - Tamanho (30-50px para ícones, 60-100px para ícones grandes)
   - Opacidade (0.3-0.5)
   - Cor: `--color-primary-soft` ou `--color-accent-peach`
   - `pointer-events: none` (não interfere com interação)
2. Posicionar cada ícone individualmente:
   - `.icon-1`: `top: 10%; left: 5%;`
   - `.icon-2`: `top: 30%; left: 10%;`
   - `.icon-3`: `top: 50%; left: 8%;`
   - `.icon-4`: `top: 15%; right: 8%;`
   - `.icon-5`: `top: 40%; right: 5%;`
   - `.icon-6`: `top: 65%; right: 10%;`
3. Criar animação `@keyframes float`:
   - Movimento vertical suave (translateY)
   - Rotação leve (rotate)
   - Mudança de opacidade
   - Duração: 6s, ease-in-out, infinite
4. Aplicar animação com delays diferentes para cada ícone
5. Ocultar ícones em mobile/tablet (media query < 1200px)

**Saída:**
- Ícones flutuantes com animação
- Visual dinâmico e acolhedor

**Critérios de Aceite:**
- [ ] Ícones posicionados corretamente
- [ ] Animação suave e natural
- [ ] Não interfere com conteúdo principal
- [ ] Ocultos em telas < 1200px
- [ ] Performance de animação adequada (60fps)

**Arquivos Afetados:**
- `backend/static/css/style.css`

**Código de Referência (Análise UX):**
```css
.floating-icon {
    position: absolute;
    font-size: 3rem;
    opacity: 0.3;
    color: #ffb3c6;
    animation: float 6s ease-in-out infinite;
    pointer-events: none;
}

@keyframes float {
    0%, 100% {
        transform: translateY(0) rotate(0deg);
        opacity: 0.3;
    }
    50% {
        transform: translateY(-20px) rotate(5deg);
        opacity: 0.5;
    }
}
```

**Testes:**
- Verificar animação em Chrome DevTools Performance
- Validar que não causa lag ou jank
- Testar em diferentes resoluções

---

### Tarefa 7: Implementar Formas Decorativas (Círculos, Ondas)

**Responsável:** Dev  
**Prioridade:** 🟢 MÉDIA  
**Estimativa:** 2 horas  
**Tipo:** Frontend - CSS

**Descrição:**
Criar formas decorativas (círculos) para adicionar profundidade visual às laterais.

**Entrada:**
- Estrutura HTML criada na Tarefa 5
- Análise UX - Especificações de formas

**Ações:**
1. Criar estilos base para `.decoration-shape`:
   - Posicionamento absoluto
   - Forma circular (border-radius: 50%)
   - Background com gradiente suave
   - Opacidade baixa (0.2-0.4)
   - `pointer-events: none`
2. Posicionar cada forma:
   - `.shape-1`: `width: 200px; height: 200px; top: 5%; left: -50px;`
   - `.shape-2`: `width: 150px; height: 150px; bottom: 10%; left: -30px;`
   - `.shape-3`: `width: 180px; height: 180px; top: 20%; right: -40px;`
   - `.shape-4`: `width: 120px; height: 120px; bottom: 15%; right: -20px;`
3. Aplicar gradiente de fundo:
```css
background: linear-gradient(
    135deg,
    rgba(255, 179, 198, 0.2) 0%,
    rgba(255, 204, 213, 0.1) 100%
);
```
4. Criar animação `@keyframes pulse`:
   - Escala suave (scale)
   - Mudança de opacidade
   - Duração: 8-11s, ease-in-out, infinite
5. Aplicar animação com delays diferentes
6. Ocultar formas em mobile/tablet

**Saída:**
- Formas decorativas animadas
- Profundidade visual nas laterais

**Critérios de Aceite:**
- [ ] Formas posicionadas corretamente
- [ ] Animação suave e sutil
- [ ] Não interfere com conteúdo
- [ ] Ocultas em telas < 1200px
- [ ] Performance adequada

**Arquivos Afetados:**
- `backend/static/css/style.css`

**Código de Referência (Análise UX):**
```css
.decoration-shape {
    position: absolute;
    border-radius: 50%;
    background: linear-gradient(
        135deg,
        rgba(255, 179, 198, 0.2) 0%,
        rgba(255, 204, 213, 0.1) 100%
    );
    pointer-events: none;
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
        opacity: 0.2;
    }
    50% {
        transform: scale(1.1);
        opacity: 0.4;
    }
}
```

---

### Tarefa 8: Atualizar Gradientes em Cards e Elementos

**Responsável:** Dev  
**Prioridade:** 🟡 ALTA  
**Estimativa:** 1.5 horas  
**Tipo:** Frontend - CSS

**Descrição:**
Aplicar gradientes quentes em cards, botões secundários e outros elementos da interface.

**Entrada:**
- Nova paleta de cores
- Análise UX - Gradientes propostos

**Ações:**
1. Identificar elementos que podem usar gradiente:
   - Cards de recursos
   - Botões secundários
   - Caixas de destaque
   - Elementos de navegação
2. Aplicar gradiente suave em cards:
```css
background: linear-gradient(
    145deg,
    rgba(255, 143, 163, 0.1) 0%,
    rgba(255, 179, 198, 0.05) 100%
);
```
3. Atualizar bordas e sombras para tons quentes
4. Aplicar efeitos hover com gradientes mais vibrantes
5. Manter consistência visual

**Saída:**
- Cards com gradientes quentes
- Visual mais harmonioso

**Critérios de Aceite:**
- [ ] Gradientes aplicados em elementos apropriados
- [ ] Efeitos hover funcionam corretamente
- [ ] Visual consistente
- [ ] Não sobrecarrega visualmente

**Arquivos Afetados:**
- `backend/static/css/style.css`

---

### Tarefa 9: Validação e Testes Visuais

**Responsável:** Dev + PO  
**Prioridade:** 🔴 CRÍTICA  
**Estimativa:** 2 horas  
**Tipo:** QA - Validação Visual

**Descrição:**
Realizar testes visuais em diferentes navegadores e resoluções para validar implementação.

**Entrada:**
- Todas as tarefas anteriores completadas
- Checklist de validação

**Ações:**
1. **Testes de Navegadores:**
   - Chrome (última versão)
   - Firefox (última versão)
   - Safari (se disponível)
   - Edge (última versão)
   - Verificar renderização de cores e gradientes
   - Validar animações funcionam

2. **Testes de Responsividade:**
   - Mobile (320px, 375px, 414px)
   - Tablet (768px, 1024px)
   - Desktop (1280px, 1920px, 2560px)
   - Verificar que ícones/formas estão ocultos em < 1200px
   - Validar que cores se adaptam bem

3. **Testes de Acessibilidade:**
   - Validar contraste de cores (WebAIM)
   - Verificar legibilidade do texto
   - Testar navegação por teclado
   - Validar que elementos decorativos não interferem

4. **Testes de Performance:**
   - Verificar FPS das animações (60fps ideal)
   - Validar que não há jank ou lag
   - Testar tempo de carregamento

5. **Validação Visual com PO:**
   - Comparar com análise de UX
   - Validar sensação de "calor" e "acolhimento"
   - Ajustar se necessário

**Saída:**
- Relatório de testes
- Bugs/correções identificados (se houver)
- Aprovação visual do PO

**Critérios de Aceite:**
- [ ] Todos os testes de navegador passaram
- [ ] Responsividade validada
- [ ] Acessibilidade WCAG AA atendida
- [ ] Performance adequada (60fps)
- [ ] Aprovado visualmente pelo PO

**Checklist de Validação:**
- [ ] Chrome: Cores e animações OK
- [ ] Firefox: Cores e animações OK
- [ ] Safari: Cores e animações OK
- [ ] Edge: Cores e animações OK
- [ ] Mobile (< 768px): Visual correto, sem ícones decorativos
- [ ] Tablet (768-1199px): Visual correto, sem ícones decorativos
- [ ] Desktop (≥ 1200px): Visual completo com ícones
- [ ] Contraste de texto: WCAG AA
- [ ] Animações: 60fps sem jank
- [ ] Visual aprovado pelo PO

---

### Tarefa 10: Documentação de Cores

**Responsável:** Dev  
**Prioridade:** 🟢 MÉDIA  
**Estimativa:** 1 hora  
**Tipo:** Documentação

**Descrição:**
Criar ou atualizar documentação das cores para referência futura.

**Entrada:**
- Variáveis CSS criadas
- Análise UX como referência

**Ações:**
1. Criar ou atualizar arquivo de documentação:
   - `docs/ux-color-palette.md` ou seção no README
2. Documentar todas as variáveis de cor:
   - Nome da variável
   - Valor hexadecimal
   - Uso recomendado
   - Exemplo visual (se possível)
3. Incluir gradientes principais
4. Incluir referência à análise de UX original

**Saída:**
- Documentação de cores completa

**Critérios de Aceite:**
- [ ] Todas as variáveis documentadas
- [ ] Gradientes documentados
- [ ] Exemplos de uso incluídos
- [ ] Referências corretas

**Arquivos Criados:**
- `docs/ux-color-palette.md`

---

## 📊 ESTIMATIVA TOTAL

**Total de Horas:** 16 horas  
**Duração Estimada:** 2-3 dias de desenvolvimento  
**Buffer para Impedimentos:** +4 horas  
**Total com Buffer:** 20 horas (2.5 dias)

---

## 🔄 DEPENDÊNCIAS

**Tarefas que podem ser paralelizadas:**
- Tarefas 1-4 (cores e gradientes) podem ser feitas em paralelo após Tarefa 1
- Tarefas 5-7 (elementos decorativos) podem ser feitas em paralelo

**Tarefas sequenciais:**
- Tarefa 1 → Tarefas 2, 3, 4 (variáveis CSS primeiro)
- Tarefa 5 → Tarefa 6, 7 (HTML antes do CSS)

---

## ✅ CHECKLIST DE INÍCIO DE SPRINT

**Antes de iniciar, confirmar:**
- [ ] Análise de UX aprovada (`ANALISE_UX_VISUAL_SOPHIA.md`)
- [ ] Arquivo CSS atual localizado e acessível
- [ ] Template HTML principal identificado
- [ ] Ambiente de desenvolvimento configurado
- [ ] Acesso a diferentes navegadores para testes
- [ ] Ferramentas de validação instaladas (WebAIM, Chrome DevTools)

---

## 📝 NOTAS IMPORTANTES

1. **Acessibilidade:** Sempre validar contraste WCAG AA. Elementos decorativos devem ter `aria-hidden="true"` e `pointer-events: none`.

2. **Performance:** Animações devem ser otimizadas para 60fps. Usar `transform` e `opacity` (propriedades que não causam reflow).

3. **Responsividade:** Ícones e formas decorativas devem ser ocultados em telas < 1200px para não poluir mobile/tablet.

4. **Manutenibilidade:** Usar variáveis CSS para facilitar futuras mudanças de cores.

5. **Compatibilidade:** Testar gradientes em navegadores antigos. Se necessário, adicionar fallbacks.

---

**Documento criado por:** PO (Sarah)  
**Data:** 2025-01-08  
**Versão:** 1.0  
**Próxima Revisão:** Após Sprint Review
