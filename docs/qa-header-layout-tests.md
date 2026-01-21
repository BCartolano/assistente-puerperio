# Casos de Teste: Correção Visual do Header

**QA Engineer:** Quinn  
**Contexto:** Validação da correção de layout no Header  
**Objetivo:** Garantir que botão e logo não se sobrepõem e que acessibilidade foi mantida

**Data:** {{date}}

---

## 🎯 Objetivo dos Testes

### Validar Correção
Verificar se a correção do layout do header resolve o problema de sobreposição entre:
- `#menu-toggle-header` (botão de menu)
- `.header-logo-text` (texto "Sophia")

### Garantir Qualidade
- ✅ Sem sobreposição visual
- ✅ Área de toque funcional
- ✅ Acessibilidade mantida
- ✅ Responsividade adequada

---

## 📋 Casos de Teste

### TC-001: Validação de Não-Sobreposição (Pixel Perfect)

#### Descrição
Verificar se o botão `#menu-toggle-header` e o texto `.header-logo-text` não possuem interseção de pixels.

#### Cenário
**DADO** que a página está carregada  
**QUANDO** o header é renderizado  
**ENTÃO** os elementos `#menu-toggle-header` e `.header-logo-text` NÃO DEVEM se sobrepor  
**E** DEVE haver espaço visível entre eles (gap de 12-16px)

#### Passos de Teste
1. Abrir página no navegador
2. Inspecionar elemento `.header-left` no DevTools
3. Verificar propriedade `display: flex`
4. Verificar propriedade `gap: 15px` (ou margin equivalente)
5. Medir distância entre botão e logo usando DevTools (régua/medida)
6. Verificar que distância é ≥ 12px
7. Verificar visualmente que não há sobreposição

#### Resultado Esperado
✅ **PASS:** Botão e logo têm gap de 12-16px  
✅ **PASS:** Sem sobreposição visual  
✅ **PASS:** Elementos claramente separados

#### Resultado Atual (Antes da Correção)
❌ **FAIL:** Botão sobrepõe logo  
❌ **FAIL:** Gap ausente ou insuficiente

#### Prioridade
🔴 **ALTA** - Correção visual crítica

---

### TC-002: Validação de Área Clicável

#### Descrição
Verificar se a área clicável do botão `#menu-toggle-header` não invade o espaço do texto `.header-logo-text`.

#### Cenário
**DADO** que o botão de menu está visível  
**QUANDO** o usuário tenta clicar no botão  
**ENTÃO** apenas o botão DEVE ser clicável  
**E** o texto "Sophia" NÃO DEVE ser clicável  
**E** clicar no texto NÃO DEVE abrir o menu

#### Passos de Teste
1. Abrir página no navegador
2. Usar DevTools para verificar área clicável do botão
3. Clicar no botão `#menu-toggle-header`
4. Verificar que menu abre corretamente
5. Clicar na área do texto `.header-logo-text` (próximo ao botão)
6. Verificar que menu NÃO abre quando clica no texto
7. Medir área clicável do botão (mínimo 44x44px para acessibilidade)

#### Resultado Esperado
✅ **PASS:** Botão clicável e funcional  
✅ **PASS:** Texto não é clicável  
✅ **PASS:** Área de toque do botão ≥ 44x44px  
✅ **PASS:** Sem interseção de áreas clicáveis

#### Prioridade
🔴 **ALTA** - Funcionalidade crítica

---

### TC-003: Validação de Acessibilidade (Contraste)

#### Descrição
Verificar se o contraste e foco foram mantidos após a alteração de posicionamento.

#### Cenário
**DADO** que a correção foi aplicada  
**QUANDO** o usuário navega com teclado (Tab)  
**ENTÃO** o botão DEVE receber foco  
**E** o contraste DEVE ser adequado (WCAG AA mínimo)  
**E** o indicador de foco DEVE ser visível

#### Passos de Teste
1. Abrir página no navegador
2. Navegar com teclado (pressionar Tab até chegar no botão)
3. Verificar que botão recebe foco (indicador visível)
4. Verificar contraste do botão (usar ferramenta de contraste)
5. Verificar contraste do texto "Sophia"
6. Verificar que contraste atende WCAG AA (4.5:1 para texto normal)
7. Verificar que indicador de foco é visível e claro

#### Resultado Esperado
✅ **PASS:** Botão recebe foco corretamente  
✅ **PASS:** Contraste do botão ≥ 4.5:1 (WCAG AA)  
✅ **PASS:** Contraste do texto ≥ 4.5:1 (WCAG AA)  
✅ **PASS:** Indicador de foco visível e claro

#### Prioridade
🟡 **MÉDIA** - Acessibilidade

---

### TC-004: Validação de Alinhamento Vertical

#### Descrição
Verificar se o botão e o logo estão alinhados verticalmente (mesma linha base).

#### Cenário
**DADO** que o header é renderizado  
**QUANDO** o usuário visualiza o header  
**ENTÃO** o botão `#menu-toggle-header` e o texto `.header-logo-text` DEVEM estar alinhados verticalmente (mesma altura)  
**E** não deve haver desalinhamento visual

#### Passos de Teste
1. Abrir página no navegador
2. Inspecionar `.header-left` no DevTools
3. Verificar propriedade `align-items: center`
4. Verificar visualmente que botão e texto estão na mesma linha
5. Usar régua/medida do DevTools para confirmar alinhamento
6. Verificar em diferentes resoluções (Mobile, Tablet, Desktop)

#### Resultado Esperado
✅ **PASS:** `align-items: center` aplicado  
✅ **PASS:** Botão e texto alinhados verticalmente  
✅ **PASS:** Sem desalinhamento visual  
✅ **PASS:** Consistente em todas as resoluções

#### Prioridade
🟡 **MÉDIA** - Qualidade visual

---

### TC-005: Validação de Responsividade

#### Descrição
Verificar se a correção funciona corretamente em diferentes resoluções (Mobile, Tablet, Desktop).

#### Cenário
**DADO** que a correção foi aplicada  
**QUANDO** a página é visualizada em diferentes tamanhos de tela  
**ENTÃO** o layout DEVE funcionar corretamente em todas as resoluções  
**E** não deve haver sobreposição em nenhuma resolução  
**E** o gap deve ser adequado para cada breakpoint

#### Passos de Teste
1. Abrir página no navegador
2. Testar em Mobile (≤768px):
   - Verificar gap de 12px (ou equivalente)
   - Verificar sem sobreposição
3. Testar em Tablet (769px - 1023px):
   - Verificar gap de 15px (ou equivalente)
   - Verificar sem sobreposição
4. Testar em Desktop (≥1024px):
   - Verificar gap de 15-16px (ou equivalente)
   - Verificar sem sobreposição
5. Testar em diferentes navegadores (Chrome, Firefox, Safari, Edge)

#### Resultado Esperado
✅ **PASS:** Layout funciona em Mobile  
✅ **PASS:** Layout funciona em Tablet  
✅ **PASS:** Layout funciona em Desktop  
✅ **PASS:** Sem sobreposição em nenhuma resolução  
✅ **PASS:** Gap adequado para cada breakpoint

#### Prioridade
🟡 **MÉDIA** - Responsividade

---

## 📊 Matriz de Testes

| Caso de Teste | Prioridade | Status | Resultado |
|---------------|------------|--------|-----------|
| TC-001: Não-Sobreposição | 🔴 ALTA | ⏳ Pendente | - |
| TC-002: Área Clicável | 🔴 ALTA | ⏳ Pendente | - |
| TC-003: Acessibilidade | 🟡 MÉDIA | ⏳ Pendente | - |
| TC-004: Alinhamento | 🟡 MÉDIA | ⏳ Pendente | - |
| TC-005: Responsividade | 🟡 MÉDIA | ⏳ Pendente | - |

---

## ✅ Checklist de Validação

### Visual
- [ ] TC-001: Botão e logo não se sobrepõem
- [ ] TC-001: Gap visível e adequado (12-16px)
- [ ] TC-004: Alinhamento vertical correto

### Funcional
- [ ] TC-002: Botão clicável e funcional
- [ ] TC-002: Texto não é clicável
- [ ] TC-002: Área de toque ≥ 44x44px

### Acessibilidade
- [ ] TC-003: Botão recebe foco corretamente
- [ ] TC-003: Contraste adequado (WCAG AA)
- [ ] TC-003: Indicador de foco visível

### Responsividade
- [ ] TC-005: Funciona em Mobile
- [ ] TC-005: Funciona em Tablet
- [ ] TC-005: Funciona em Desktop

---

## 🔧 Ferramentas de Teste

### DevTools (Chrome/Firefox)
- Inspeção de elementos
- Medição de distâncias (régua)
- Verificação de propriedades CSS
- Teste de área clicável

### Ferramentas de Acessibilidade
- Contraste de cores (WCAG checker)
- Navegação por teclado
- Leitores de tela (opcional)

### Responsividade
- DevTools Device Mode
- Diferentes resoluções de tela
- Diferentes navegadores

---

## 📝 Notas para Execução

### Para @qa
- **Prioridade:** Executar TC-001 e TC-002 primeiro (críticos)
- **Validar:** Usar DevTools para medições precisas
- **Documentar:** Screenshots de antes/depois (opcional)
- **Reportar:** Qualquer sobreposição encontrada

### Para @dev
- **Validar:** TC-001 antes de marcar como completo
- **Garantir:** Gap de 12-16px implementado
- **Testar:** Em diferentes navegadores

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial: Casos de teste para correção do header | QA (Quinn) |
