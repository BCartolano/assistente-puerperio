# Plano de Testes: Visualização de Ala Maternal

**QA Engineer:** Quinn  
**Contexto:** Feature que indica se hospital tem Ala Maternal  
**Objetivo:** Garantir que o sistema não minta para o paciente

**Data:** {{date}}

---

## 🎯 Visão Geral

### Contexto Crítico
Vamos lançar uma feature que indica se há Ala Maternal. Um erro aqui pode levar um paciente ao local errado, colocando a vida em risco.

### Objetivo dos Testes
Garantir que:
1. ✅ O sistema nunca exibe informação falsa ou ambígua
2. ✅ Dados nulos são tratados como "não possui" (por segurança)
3. ✅ A ordenação funciona corretamente (maternidade primeiro)
4. ✅ A interface é clara e acessível (incluindo usuários daltônicos)
5. ✅ O sistema não quebra em casos extremos

---

## 📋 Casos de Teste Principais

### TC-001: Teste de Dados Nulos

#### Descrição
Verificar o que acontece se o campo `hasMaternityWard` vier `null` ou `undefined` do backend.

#### Cenário
**DADO** que o backend retorna um hospital com `hasMaternityWard: null`  
**QUANDO** o frontend processa e renderiza o card  
**ENTÃO** o sistema DEVE tratar como `false` (não possui)  
**E** DEVE exibir badge negativo (laranja/cinza)  
**E** NÃO DEVE quebrar a interface  
**E** NÃO DEVE deixar o campo em branco

#### Passos de Teste
1. Preparar mock de API retornando hospital com `hasMaternityWard: null`
2. Fazer requisição de busca de hospitais
3. Verificar renderização do card
4. Verificar que badge negativo é exibido
5. Verificar que texto "Não possui Ala Maternal - Apenas PS Geral" está presente
6. Verificar que não há erros no console
7. Verificar que interface não quebra

#### Resultado Esperado
✅ Badge negativo (laranja/cinza) é exibido  
✅ Texto "Não possui Ala Maternal - Apenas PS Geral" está presente  
✅ Interface não quebra  
✅ Console não exibe erros

#### Prioridade
🔴 **CRÍTICA** - Segurança do Paciente

#### Severidade se Falhar
🔴 **ALTA** - Pode levar paciente ao hospital errado

---

### TC-002: Teste de Ordenação (Prioridade)

#### Descrição
Verificar se hospitais com Ala Maternal aparecem primeiro na lista, mesmo que sejam mais distantes.

#### Cenário
**DADO** que há 4 hospitais:
- Hospital A: `hasMaternityWard: true`, `distance: 5km`
- Hospital B: `hasMaternityWard: false`, `distance: 2km`
- Hospital C: `hasMaternityWard: true`, `distance: 8km`
- Hospital D: `hasMaternityWard: false`, `distance: 1km`

**QUANDO** a lista de hospitais é exibida  
**ENTÃO** a ordem DEVE ser:
1. Hospital A (5km) - Tem maternidade (mais próximo)
2. Hospital C (8km) - Tem maternidade (mais distante)
3. Hospital D (1km) - Sem maternidade (mais próximo)
4. Hospital B (2km) - Sem maternidade (mais distante)

#### Passos de Teste
1. Preparar mock de API retornando 4 hospitais com diferentes valores de `hasMaternityWard` e `distance`
2. Fazer requisição de busca de hospitais
3. Verificar ordem de renderização dos cards
4. Verificar que Hospital A aparece primeiro (tem maternidade, 5km)
5. Verificar que Hospital C aparece segundo (tem maternidade, 8km)
6. Verificar que Hospital D aparece terceiro (sem maternidade, 1km)
7. Verificar que Hospital B aparece quarto (sem maternidade, 2km)

#### Resultado Esperado
✅ Hospitais com `hasMaternityWard: true` aparecem primeiro  
✅ Dentro de cada grupo (com/sem maternidade), ordenação é por distância (mais próximo primeiro)

#### Prioridade
🔴 **ALTA** - Regra de Negócio Crítica

#### Severidade se Falhar
🟡 **MÉDIA** - Funcionalidade não funciona como esperado, mas não coloca paciente em risco

---

### TC-003: Teste Visual (Acessibilidade - Daltonismo)

#### Descrição
Verificar se as cores Verde (positivo) e Laranja/Cinza (negativo) são distintas o suficiente para usuários daltônicos.

#### Cenário
**DADO** que há dois hospitais na lista:
- Hospital A: `hasMaternityWard: true` (badge verde)
- Hospital B: `hasMaternityWard: false` (badge laranja/cinza)

**QUANDO** um usuário daltônico visualiza a lista  
**ENTÃO** DEVE conseguir distinguir visualmente os badges  
**E** DEVE conseguir identificar qual hospital tem maternidade  
**E** NÃO DEVE depender apenas da cor (deve ter texto/ícone)

#### Passos de Teste
1. Renderizar lista com 2 hospitais (um com badge positivo, outro com badge negativo)
2. Usar simulador de daltonismo (ferramenta: Chrome DevTools > Rendering > Emulate vision deficiencies)
3. Testar com Protanopia (vermelho-verde)
4. Testar com Deuteranopia (vermelho-verde)
5. Testar com Tritanopia (azul-amarelo)
6. Verificar que badges ainda são distinguíveis
7. Verificar que texto/ícones são claros mesmo sem cor

#### Resultado Esperado
✅ Badges são distinguíveis mesmo com daltonismo  
✅ Texto/ícones são claros (não dependem apenas da cor)  
✅ Contraste de texto atende WCAG AAA (4.5:1)

#### Prioridade
🟡 **MÉDIA** - Acessibilidade

#### Severidade se Falhar
🟡 **MÉDIA** - Impacta acessibilidade, mas não impede uso (texto/ícone ainda disponíveis)

---

### TC-004: Teste de Rendering (Estados Positivo e Negativo)

#### Descrição
Verificar que os badges são renderizados corretamente em ambos os estados (positivo e negativo).

#### Cenário
**DADO** que há dois hospitais na lista:
- Hospital A: `hasMaternityWard: true`
- Hospital B: `hasMaternityWard: false`

**QUANDO** os cards são renderizados  
**ENTÃO** Hospital A DEVE exibir badge verde com texto "Possui Ala Maternal"  
**E** Hospital B DEVE exibir badge laranja/cinza com texto "Não possui Ala Maternal - Apenas PS Geral"  
**E** Ambos os badges DEVEM estar na mesma posição no card  
**E** Ambos os badges DEVEM ter o mesmo tamanho

#### Passos de Teste
1. Renderizar lista com 2 hospitais (um com badge positivo, outro com badge negativo)
2. Verificar que Hospital A exibe badge verde
3. Verificar que texto "Possui Ala Maternal" está presente
4. Verificar que Hospital B exibe badge laranja/cinza
5. Verificar que texto "Não possui Ala Maternal - Apenas PS Geral" está presente
6. Verificar que ambos os badges estão na mesma posição (após o header)
7. Verificar que ambos os badges têm o mesmo tamanho

#### Resultado Esperado
✅ Badge positivo renderizado corretamente (verde, texto correto)  
✅ Badge negativo renderizado corretamente (laranja/cinza, texto correto)  
✅ Posição e tamanho são consistentes

#### Prioridade
🟡 **MÉDIA** - Consistência Visual

#### Severidade se Falhar
🟢 **BAIXA** - Impacta UX, mas não coloca paciente em risco

---

### TC-005: Teste de Leitura Rápida (Tempo de Compreensão)

#### Descrição
Verificar que usuários conseguem identificar se hospital tem maternidade em menos de 2 segundos.

#### Cenário
**DADO** que há 5 hospitais na lista (alguns com maternidade, outros sem)  
**QUANDO** um usuário visualiza a lista pela primeira vez  
**ENTÃO** DEVE conseguir identificar quais hospitais têm maternidade em < 2 segundos  
**E** DEVE conseguir distinguir rapidamente entre "tem" e "não tem"

#### Passos de Teste
1. Renderizar lista com 5 hospitais (mix de com/sem maternidade)
2. Medir tempo de compreensão:
   - Mostrar lista para usuário
   - Cronometrar tempo até usuário identificar quais hospitais têm maternidade
3. Repetir teste com 10 usuários diferentes
4. Calcular tempo médio de compreensão
5. Verificar que tempo médio é < 2 segundos

#### Resultado Esperado
✅ Tempo médio de compreensão é < 2 segundos  
✅ 80%+ dos usuários conseguem identificar corretamente em < 2 segundos

#### Prioridade
🟡 **MÉDIA** - UX/Usabilidade

#### Severidade se Falhar
🟢 **BAIXA** - Impacta UX, mas não coloca paciente em risco

---

## 🧪 Testes Adicionais (Opcional)

### TC-006: Teste de Responsividade (Mobile)

#### Descrição
Verificar que badges funcionam bem em dispositivos móveis (tela pequena).

#### Passos de Teste
1. Renderizar lista em dispositivo móvel (< 480px)
2. Verificar que badges são legíveis
3. Verificar que texto não é cortado
4. Verificar que layout não quebra

#### Resultado Esperado
✅ Badges são legíveis em mobile  
✅ Texto não é cortado  
✅ Layout não quebra

---

### TC-007: Teste de Performance (Renderização)

#### Descrição
Verificar que renderização de lista com muitos hospitais não causa lentidão.

#### Passos de Teste
1. Renderizar lista com 50 hospitais
2. Medir tempo de renderização
3. Verificar que não há travamentos
4. Verificar que interface responde bem

#### Resultado Esperado
✅ Renderização é rápida (< 1 segundo para 50 hospitais)  
✅ Não há travamentos  
✅ Interface responde bem

---

## ✅ Checklist de Testes

### Testes Críticos
- [ ] TC-001: Teste de Dados Nulos (CRÍTICO)
- [ ] TC-002: Teste de Ordenação (ALTA)
- [ ] TC-003: Teste Visual (Acessibilidade - Daltonismo) (MÉDIA)
- [ ] TC-004: Teste de Rendering (Estados Positivo e Negativo) (MÉDIA)
- [ ] TC-005: Teste de Leitura Rápida (Tempo de Compreensão) (MÉDIA)

### Testes Adicionais
- [ ] TC-006: Teste de Responsividade (Mobile) (OPCIONAL)
- [ ] TC-007: Teste de Performance (Renderização) (OPCIONAL)

---

## 📊 Matriz de Risco

| Caso de Teste | Prioridade | Severidade se Falhar | Status |
|---------------|------------|---------------------|--------|
| TC-001: Dados Nulos | 🔴 CRÍTICA | 🔴 ALTA | ⏳ Pendente |
| TC-002: Ordenação | 🔴 ALTA | 🟡 MÉDIA | ⏳ Pendente |
| TC-003: Acessibilidade | 🟡 MÉDIA | 🟡 MÉDIA | ⏳ Pendente |
| TC-004: Rendering | 🟡 MÉDIA | 🟢 BAIXA | ⏳ Pendente |
| TC-005: Leitura Rápida | 🟡 MÉDIA | 🟢 BAIXA | ⏳ Pendente |

---

## 📝 Notas para o Time

### Para @dev (Desenvolvedor)
- **Prioridade:** Implementar tratamento de NULL: `hasMaternityWard ?? false`
- **Prioridade:** Implementar ordenação correta (maternidade primeiro)
- **Testar:** Todos os casos de teste críticos antes de deploy

### Para @po (Product Owner)
- **Validar:** Regra de negócio de ordenação (maternidade primeiro, mesmo que mais distante)
- **Validar:** Tratamento de NULL como "não possui" (por segurança)

### Para @ux (UX Designer)
- **Validar:** Cores são distinguíveis para daltônicos
- **Validar:** Texto/ícones são claros mesmo sem cor

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial do plano de testes | QA (Quinn) |
