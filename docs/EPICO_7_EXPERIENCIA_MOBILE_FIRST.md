# Épico 7: Experiência Mobile First

**Criado por:** Sarah (Product Owner)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ⏳ Planejamento

---

## 🎯 OBJETIVO

Adaptar todas as funcionalidades da versão desktop (V1.0 PROD) para dispositivos móveis, garantindo experiência fluida, acessível e intuitiva em smartphones e tablets, considerando que mães frequentemente usarão o aplicativo segurando o bebê com uma mão.

---

## 📊 CONTEXTO

### **Situação Atual:**
- ✅ Versão Desktop (V1.0 PROD) completa e funcional
- ✅ Layout de 3 colunas otimizado para telas ≥1024px
- ✅ Chat Inteligente com contexto personalizado
- ✅ Agenda de Vacinação Interativa
- ✅ Quick Replies contextuais
- ✅ Sistema de detecção emocional

### **Desafio:**
- ⚠️ Interface desktop não é otimizada para mobile
- ⚠️ Layout de 3 colunas não funciona em telas pequenas
- ⚠️ Botões podem não ser alcançáveis com uma mão
- ⚠️ Timeline de vacinação pode não ser legível em mobile
- ⚠️ Quick Replies podem estar muito pequenos ou mal posicionados

---

## 🎯 CRITÉRIOS DE SUCESSO

### **O que esperamos da Sophia no celular que seja diferente do computador?**

1. **Acessibilidade One-Handed:**
   - Todos os botões principais devem estar na "zona de alcance" (área inferior da tela)
   - Quick Replies devem ser grandes o suficiente para toque preciso
   - Input de chat deve ser facilmente acessível com polegar

2. **Navegação Simplificada:**
   - Chat e Timeline devem ser acessíveis via navegação intuitiva (Abas ou Drawer)
   - Prioridade visual clara: Chat primeiro, Timeline depois
   - Transições suaves entre seções

3. **Performance Otimizada:**
   - Scroll suave sem lag
   - Streaming de respostas otimizado para mobile
   - Carregamento rápido mesmo em conexões 3G/4G

4. **Experiência Touch-Friendly:**
   - Áreas de toque ≥ 44px × 44px (padrão iOS/Android)
   - Espaçamento adequado entre elementos clicáveis
   - Feedback visual imediato em interações

5. **Conteúdo Adaptado:**
   - Timeline de vacinação legível em telas pequenas
   - Quick Replies adaptados para mobile (tamanho e posicionamento)
   - Header fixo adaptado ou removido em mobile

---

## 📋 STORIES PRIORITIZADAS

### **Sprint MOBILE-1: Análise e Estrutura Base** ✅ CONCLUÍDA

1. ✅ **Análise de Adaptação Mobile (UX Expert)**
   - Como transformar 3 colunas em navegação mobile? → **Abas inferiores**
   - Prioridade visual: Chat vs Timeline? → **Chat primeiro (padrão)**
   - Acessibilidade one-handed: Zona de alcance → **Inferior da tela (30-40%)**

2. ✅ **Definir Estrutura de Navegação Mobile**
   - Abas na parte inferior vs Menu Drawer lateral → **Abas inferiores escolhidas**
   - Decisão baseada em análise UX → **Acessibilidade one-handed**

3. ✅ **Implementar Layout Base Mobile**
   - Container responsivo para mobile → **Media queries implementadas**
   - Sistema de navegação escolhido → **Bottom Navigation (3 abas)**
   - Ocultar/adaptar elementos desktop → **Sidebars e header fixo ocultos**

**Estimativa:** 1 sprint  
**Prioridade:** 🔴 CRÍTICA  
**Status:** ✅ Concluída em 2025-01-27

---

### **Sprint MOBILE-2: Chat e Interações** ⏳ EM PROGRESSO

4. ⏳ **Adaptar Chat para Mobile**
   - ✅ Header fixo removido em mobile
   - ⏳ Input de chat ajustado para não ser coberto pelo teclado virtual
   - ✅ Streaming de respostas otimizado (15ms no mobile vs 25ms desktop)

5. ✅ **Adaptar Quick Replies para Mobile**
   - ✅ Tamanho mínimo 44px × 44px implementado
   - ✅ Posicionamento na zona de alcance
   - ✅ Espaçamento adequado entre botões

6. ⏳ **Implementar Aba Dicas Mobile**
   - ⏳ Lista vertical de cards (Dica do Dia, Afirmação, Próxima Vacina)
   - ⏳ Modal de vídeo fullscreen no mobile
   - ⏳ Lazy loading de vídeos YouTube (só carrega quando aba é ativada)

7. ⏳ **Otimizar Performance Touch**
   - ✅ Scroll suave implementado
   - ✅ Feedback visual imediato
   - ⏳ Prevenção de toques acidentais (a implementar)

8. ⏳ **Indicador de Digitação Mobile**
   - ⏳ Indicador sticky no topo da aba de chat
   - ⏳ Animação discreta de 3 pontos pulsantes
   - ⏳ Estilo visual com paleta quente

**Estimativa:** 1 sprint  
**Prioridade:** 🔴 CRÍTICA  
**Status:** ⏳ Em Progresso (40% concluído)

---

### **Sprint MOBILE-3: Timeline e Testes**

7. **Adaptar Timeline de Vacinação para Mobile**
   - Layout vertical otimizado
   - Cards compactos mas legíveis
   - Scroll horizontal se necessário

8. **Testes de Usabilidade em Dispositivos Reais**
   - Testes com mães reais
   - Feedback e ajustes
   - Validação de acessibilidade

9. **Otimização Final**
   - Performance para touch devices
   - Ajustes finos baseados em feedback
   - Documentação de uso mobile

**Estimativa:** 1 sprint  
**Prioridade:** 🟠 ALTA

---

## 🎨 DIRETRIZES DE DESIGN

### **Zona de Alcance One-Handed:**
- **Área Segura:** Inferior da tela (últimos 30-40% da altura)
- **Botões Principais:** Input de chat, Quick Replies, ações principais
- **Tamanho Mínimo:** 44px × 44px (padrão iOS/Android)

### **Navegação:**
- **Opção 1: Abas Inferiores** (Recomendado)
  - Chat | Vacinas | Perfil
  - Sempre visível, fácil acesso
  - Padrão mobile conhecido

- **Opção 2: Menu Drawer Lateral**
  - Menu hambúrguer no topo
  - Drawer deslizante da esquerda
  - Mais espaço para conteúdo

### **Prioridade Visual:**
1. **Chat** (primário) - Acesso imediato
2. **Timeline de Vacinas** (secundário) - Via navegação
3. **Perfil/Configurações** (terciário) - Via menu

---

## 📱 BREAKPOINTS MOBILE

### **Mobile Portrait (< 480px)**
- Layout de coluna única
- Navegação por abas inferiores
- Botões na zona de alcance

### **Mobile Landscape (480px - 768px)**
- Layout adaptado para horizontal
- Navegação mantida
- Ajustes de espaçamento

### **Tablet (768px - 1024px)**
- Layout intermediário
- Possível manter algumas colunas
- Navegação adaptada

---

## ✅ DEFINITION OF DONE

- [ ] Análise UX Mobile completa
- [ ] Estrutura de navegação definida e implementada
- [ ] Chat adaptado para mobile
- [ ] Quick Replies adaptados (tamanho e posicionamento)
- [ ] Timeline de vacinação adaptada
- [ ] Todos os botões na zona de alcance
- [ ] Performance otimizada (scroll suave, sem lag)
- [ ] Testes de usabilidade realizados
- [ ] Feedback incorporado
- [ ] Documentação atualizada

---

## 📊 MÉTRICAS DE SUCESSO

- **Taxa de Conclusão de Tarefas:** ≥ 90% em mobile
- **Tempo de Interação:** ≤ 3 toques para ações principais
- **Satisfação do Usuário:** ≥ 4.5/5 em testes de usabilidade
- **Performance:** Scroll a 60fps, sem lag perceptível
- **Acessibilidade:** 100% dos botões na zona de alcance

---

## 🔄 PRÓXIMOS PASSOS

1. **UX Expert (Sally):** Análise completa de adaptação mobile
2. **Dev:** Implementar estrutura base de navegação
3. **PO (Sarah):** Validar decisões de design
4. **Testes:** Usabilidade com usuários reais

---

**Versão:** 1.0  
**Status:** ⏳ Planejamento  
**Próxima Revisão:** Após análise UX Mobile
