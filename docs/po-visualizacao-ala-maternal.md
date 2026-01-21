# User Stories: Visualização de Ala Maternal

**Contexto:** Sistema de Localizador de Hospitais - Feature: Visualização Clara de Ala Maternal

**Prioridade:** 🔴 CRÍTICA - Segurança do Paciente

**Data:** {{date}}

---

## 📋 User Story Principal

### US-001: Visualização Clara de Ala Maternal nos Cards de Hospitais

**Como** uma gestante em situação de emergência  
**Eu quero** visualizar de forma clara e imediata quais hospitais possuem Ala Maternal  
**Para que** eu possa tomar a decisão correta sobre qual hospital buscar, evitando ir a um hospital sem o serviço necessário.

---

## ✅ Critérios de Aceite

### AC-001: Priorização na Lista
**DADO** que o usuário busca hospitais próximos  
**QUANDO** a lista de hospitais é exibida  
**ENTÃO** os hospitais COM Ala Maternal confirmada DEVEM aparecer PRIMEIRO na lista (antes dos hospitais sem Ala Maternal)  
**E** o critério de desempate dentro de cada grupo (com/sem maternidade) DEVE ser a proximidade geográfica (mais próximo primeiro)

**Prioridade:** 🔴 ALTA - Regra de Negócio Crítica

---

### AC-002: Exibição Positiva (Hospital TEM Ala Maternal)
**DADO** que um hospital possui Ala Maternal confirmada (hasMaternityWard = true)  
**QUANDO** o card do hospital é renderizado  
**ENTÃO** DEVE exibir um badge/indicador visual DESTACADO com:
- Cor: Verde (#28a745 ou similar - alta visibilidade)
- Ícone: ✅ (check) ou ícone de bebê/maternidade
- Texto: "✅ Possui Ala Maternal" ou "✅ Ala Maternal Confirmada"
- Posição: Destaque visual no topo do card (após o nome do hospital, antes dos badges secundários)

**Prioridade:** 🔴 ALTA - Informação Crítica

---

### AC-003: Exibição Negativa Explícita (Hospital NÃO TEM Ala Maternal)
**DADO** que um hospital NÃO possui Ala Maternal (hasMaternityWard = false)  
**QUANDO** o card do hospital é renderizado  
**ENTÃO** DEVE exibir um badge/indicador visual EXPLÍCITO com:
- Cor: Laranja (#ffb703) ou Cinza Escuro (#6c757d) para alerta
- Ícone: ⚠️ (aviso) ou ícone de atenção
- Texto: "⚠️ Não possui Ala Maternal - Apenas PS Geral" ou "⚠️ Não contém Ala Maternal"
- Posição: Destaque visual no topo do card (mesma posição do badge positivo)
- **NÃO PODE** deixar o campo em branco ou vazio - DEVE ser explícito

**Prioridade:** 🔴 CRÍTICA - Segurança do Paciente (Evitar Ambiguidade)

---

### AC-004: Tratamento de Dados Nulos/Vazios (Fallback de Segurança)
**DADO** que um hospital retorna com campo de maternidade NULL ou VAZIO  
**QUANDO** o sistema processa os dados  
**ENTÃO** DEVE tratar como "NÃO POSSUI" (hasMaternityWard = false) por padrão  
**E** DEVE exibir o badge negativo (AC-003)  
**E** NÃO DEVE quebrar a interface ou deixar informações ausentes

**Justificativa:** Em casos de emergência, é mais seguro assumir que o hospital NÃO possui o serviço se a informação não está confirmada, do que deixar o usuário adivinhar.

**Prioridade:** 🔴 CRÍTICA - Prevenção de Erros de Segurança

---

### AC-005: Consistência Visual Entre Estados
**DADO** que há múltiplos hospitais na lista  
**QUANDO** os cards são exibidos  
**ENTÃO** TODOS os cards DEVEM ter o indicador de Ala Maternal (positivo ou negativo)  
**E** a posição e tamanho do indicador DEVEM ser consistentes em todos os cards  
**E** a diferença visual entre "TEM" e "NÃO TEM" DEVE ser OBVIA mesmo em leitura rápida

**Prioridade:** 🟡 MÉDIA - UX/Consistência

---

## 🔒 Regras de Negócio

### RN-001: Princípio da Segurança do Paciente
> **"Em caso de dúvida ou dado ausente, sempre assumir o cenário mais conservador (hospital NÃO possui Ala Maternal) até confirmação manual."**

**Aplicação:**
- Campos NULL → Tratados como `hasMaternityWard = false`
- Campos vazios ("") → Tratados como `hasMaternityWard = false`
- Dados inconsistentes → Tratados como `hasMaternityWard = false`
- Exceção: Apenas `hasMaternityWard = true` explícito e confirmado exibe badge positivo

---

### RN-002: Ordenação de Prioridade
1. **Primeiro Critério:** Hospitais com `hasMaternityWard = true` (ordem: mais próximo primeiro)
2. **Segundo Critério:** Hospitais com `hasMaternityWard = false` (ordem: mais próximo primeiro)

**Exemplo:**
```
Hospital A (com maternidade, 5km)      ← 1º
Hospital B (com maternidade, 8km)      ← 2º
Hospital C (sem maternidade, 2km)      ← 3º
Hospital D (sem maternidade, 4km)      ← 4º
```

---

### RN-003: Clareza Negativa Obrigatória
> **"Nunca deixar o usuário inferir pela ausência de informação. Se não tem maternidade, DEVE estar explícito."**

- Badge negativo é OBRIGATÓRIO quando `hasMaternityWard = false` ou `null`
- Não é aceitável ter cards "neutros" sem informação sobre maternidade
- O texto do badge negativo DEVE ser claro: "Não possui Ala Maternal - Apenas PS Geral"

---

## 📊 Definições Técnicas (Para Time de Desenvolvimento)

### Campo de Dados
- **Nome do Campo:** `hasMaternityWard` (boolean)
- **Tipo:** `BOOLEAN` (não nullable)
- **Valor Padrão:** `false`
- **Valores Aceitos:** `true` | `false`
- **Tratamento de NULL:** Converter para `false` antes da renderização

### Estados da Interface
1. **Estado POSITIVO:** `hasMaternityWard === true` → Badge Verde
2. **Estado NEGATIVO:** `hasMaternityWard === false` → Badge Laranja/Cinza
3. **Estado FALLBACK:** `hasMaternityWard === null || undefined` → Tratar como `false` → Badge Laranja/Cinza

---

## 🎯 Definições de Sucesso

### Métricas de Aceitação
- ✅ 100% dos cards exibem indicador de Ala Maternal (positivo ou negativo)
- ✅ 0% de cards com informação ausente/ambígua sobre maternidade
- ✅ Ordenação funciona corretamente: hospitais com maternidade sempre primeiro
- ✅ Teste de acessibilidade: Usuários daltônicos conseguem distinguir os badges
- ✅ Tempo de compreensão: Usuário identifica se hospital tem maternidade em < 2 segundos

---

## 📝 Notas para o Time

### Para @dev (Desenvolvedor)
- Implementar validação no frontend para garantir que `hasMaternityWard` nunca seja `null` na renderização
- Usar fallback: `const hasMaternity = hospital.hasMaternityWard ?? false;`
- Priorizar implementação de AC-004 (tratamento de nulos) antes de outras features

### Para @ux-expert (UX Designer)
- Badge positivo e negativo devem ter contraste suficiente para daltônicos (usar ferramenta de contraste)
- Considerar uso de ícones + cores + texto para máxima clareza
- Testar em dispositivos móveis (usuários podem estar em situação de estresse)

### Para @architect (Arquiteto)
- Definir estrutura de dados que garanta `hasMaternityWard` não nullable
- Script de migração: converter todos `NULL` para `false` no banco
- API deve retornar sempre boolean, nunca `null`

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial da User Story | PO (Sarah) |
