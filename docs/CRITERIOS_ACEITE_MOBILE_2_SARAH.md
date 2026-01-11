# Critérios de Aceite - Sprint MOBILE-2

**Criado por:** Sarah (Product Owner)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Aprovado

---

## ✅ CRITÉRIOS DE ACEITE PRINCIPAIS

### **1. Chat 100% Funcional com Teclado Aberto**

**Critérios:**
- ✅ Input de chat visível e acessível quando teclado virtual está aberto
- ✅ Mãe consegue ver o que está digitando enquanto digita
- ✅ Botão de enviar permanece acessível (não coberto pelo teclado)
- ✅ Histórico de mensagens permanece visível acima do input

**Como Testar:**
1. Abrir aplicativo em dispositivo mobile
2. Tocar no input de chat
3. Verificar se input permanece visível acima do teclado virtual
4. Verificar se mensagens anteriores continuam visíveis
5. Verificar se botão de enviar está acessível

**Aceitação:**
- ✅ Input sempre visível com teclado aberto
- ✅ Histórico de mensagens acessível via scroll
- ✅ Botão de enviar acessível (área de toque ≥ 44px × 44px)

---

### **2. Quick Replies Não Quebram o Layout**

**Critérios:**
- ✅ Quick Replies ocupam largura total da tela (margens laterais adequadas)
- ✅ Layout vertical (empilhadas) em mobile
- ✅ Altura mínima de 44px × 44px para facilitar toque
- ✅ Espaçamento adequado entre botões (≥ 8px)
- ✅ Texto não quebra em múltiplas linhas de forma incorreta
- ✅ Quick Replies não ultrapassam bordas da tela

**Como Testar:**
1. Fazer pergunta que gere Quick Replies
2. Verificar se botões ocupam largura total (com margens)
3. Verificar se botões estão empilhados verticalmente
4. Verificar se altura mínima é 44px
5. Verificar se espaçamento entre botões é adequado (≥ 8px)
6. Testar em diferentes tamanhos de tela (iPhone SE, iPhone 12, Android)

**Aceitação:**
- ✅ Quick Replies sempre visíveis e acessíveis
- ✅ Layout não quebra em nenhum tamanho de tela
- ✅ Área de toque adequada (≥ 44px × 44px)
- ✅ Sem scroll horizontal indesejado

---

### **3. Aba Dicas Funcional**

**Critérios:**
- ✅ Lista vertical de cards (Dica do Dia, Afirmação Positiva, Próxima Vacina)
- ✅ Cards ocupam quase toda largura (margens de 15px)
- ✅ Bordas arredondadas de 16px
- ✅ Scroll vertical suave
- ✅ Conteúdo carregado dinamicamente

**Como Testar:**
1. Tocar na aba "Dicas" na bottom navigation
2. Verificar se lista de cards aparece
3. Verificar se cards têm margens de 15px
4. Verificar se bordas são arredondadas (16px)
5. Verificar se scroll funciona suavemente
6. Verificar se conteúdo (dicas, afirmações) está presente

**Aceitação:**
- ✅ Lista de cards visível e acessível
- ✅ Layout respeita especificações de margens e bordas
- ✅ Scroll suave e funcional
- ✅ Conteúdo carregado corretamente

---

### **4. Modal de Vídeo Fullscreen no Mobile**

**Critérios:**
- ✅ Modal ocupa 100% da largura e altura (fullscreen) em mobile
- ✅ Botão de fechar tem 44px × 44px (área de toque adequada)
- ✅ Vídeo para imediatamente ao fechar (remove `src` do iframe)
- ✅ ESC key fecha o modal e para o vídeo
- ✅ Fundo escuro para destacar vídeo

**Como Testar:**
1. Tocar em vídeo na aba Dicas
2. Verificar se modal abre em fullscreen
3. Verificar se botão de fechar é grande o suficiente (44px × 44px)
4. Fechar modal e verificar se áudio para imediatamente
5. Abrir modal novamente e pressionar ESC
6. Verificar se modal fecha e vídeo para

**Aceitação:**
- ✅ Modal fullscreen em mobile
- ✅ Botão de fechar acessível (44px × 44px)
- ✅ Vídeo para imediatamente ao fechar
- ✅ ESC key funciona corretamente

---

### **5. Lazy Loading de Vídeos YouTube**

**Critérios:**
- ✅ Vídeos do YouTube NÃO carregam iframes até que aba Dicas seja ativada
- ✅ Apenas thumbnails são carregadas inicialmente
- ✅ Iframes só são criados quando usuário clica em um vídeo
- ✅ Economia de dados no 4G verificável (Network tab do DevTools)

**Como Testar:**
1. Abrir aplicativo em mobile
2. Verificar Network tab do DevTools
3. Navegar pelas abas (Chat, Vacinas, Dicas)
4. Verificar que iframes YouTube NÃO são carregados até clicar em vídeo
5. Verificar que apenas thumbnails são carregadas na aba Dicas
6. Clicar em vídeo e verificar se iframe é carregado naquele momento

**Aceitação:**
- ✅ Sem iframes YouTube carregados até interação
- ✅ Thumbnails carregadas apenas quando necessário
- ✅ Economia de dados verificável
- ✅ Performance melhorada em conexões lentas

---

### **6. Streaming de Respostas Otimizado**

**Critérios:**
- ✅ Velocidade de streaming adaptativa: 15ms no mobile, 25ms no desktop
- ✅ Resposta não parece "travada" em conexões lentas
- ✅ Indicador visual de streaming funciona corretamente

**Como Testar:**
1. Fazer pergunta no mobile
2. Verificar se resposta aparece com streaming (efeito typewriter)
3. Verificar se velocidade é adequada (não muito lenta)
4. Testar em conexão 4G lenta (throttle no DevTools)
5. Verificar se resposta não parece "engasgada"

**Aceitação:**
- ✅ Streaming mais rápido no mobile (15ms)
- ✅ Resposta fluida mesmo em conexões lentas
- ✅ Indicador visual funcional

---

### **7. Indicador de Digitação da Sophia**

**Critérios:**
- ✅ Indicador aparece quando Sophia está "digitando"
- ✅ Posicionamento sticky no topo da aba de chat (mobile)
- ✅ Animação discreta de 3 pontos pulsantes
- ✅ Estilo visual com paleta quente (coral)

**Como Testar:**
1. Fazer pergunta no mobile
2. Verificar se indicador aparece no topo da aba de chat
3. Verificar se animação é discreta e suave
4. Verificar se indicador desaparece quando resposta completa
5. Verificar se cor segue paleta quente

**Aceitação:**
- ✅ Indicador visível mas discreto
- ✅ Posicionamento correto (topo sticky)
- ✅ Animação suave e não intrusiva
- ✅ Estilo visual consistente com paleta

---

## 📊 AVALIAÇÃO: AVISO DE USO DE DADOS PARA VÍDEOS

### **Análise:**

**Argumentos a Favor:**
- ✅ Conscientiza sobre uso de dados móveis
- ✅ Transparência com usuário (LGPD)
- ✅ Bom para usuários com planos limitados

**Argumentos Contra:**
- ❌ Pode criar atrito desnecessário
- ❌ Avisos podem ser ignorados ou irritantes
- ❌ Usuário já espera usar dados ao clicar em vídeo

### **Recomendação:**

✅ **Implementar Aviso Discreto (Opcional)**

**Implementação:**
- **Localização:** Pequeno texto abaixo dos vídeos na aba Dicas
- **Texto:** "📱 Vídeos podem consumir dados móveis"
- **Estilo:** Texto pequeno (0.75rem), cinza, discreto
- **Não bloqueante:** Apenas informativo, não impede reprodução

**Exemplo:**
```html
<div class="mobile-videos-card">
    <h3>📺 Vídeos Educativos</h3>
    <p class="data-usage-warning" style="font-size: 0.75rem; color: #999; padding: 0.5rem 1rem;">
        📱 Vídeos podem consumir dados móveis
    </p>
    <div id="mobile-videos-list"></div>
</div>
```

**Justificativa:**
- Transparência sem criar atrito
- Usuário informado mas não bloqueado
- Boa prática de UX responsável

---

## ✅ DEFINITION OF DONE

- [x] Critérios de aceite definidos
- [x] Critérios de aceite validados pela equipe
- [ ] Implementação concluída
- [ ] Testes realizados
- [ ] Critérios de aceite atendidos
- [ ] Documentação atualizada

---

## 📝 PRÓXIMOS PASSOS

1. **Dev:** Implementar todas as funcionalidades conforme critérios
2. **QA:** Testar cada critério de aceite em dispositivos reais
3. **PO (Sarah):** Validar se critérios foram atendidos
4. **UX (Sally):** Validar experiência do usuário
5. **Release:** Publicar quando todos os critérios forem atendidos

---

**Versão:** 1.0  
**Status:** ✅ Aprovado  
**Próxima Revisão:** Após conclusão da Sprint MOBILE-2
