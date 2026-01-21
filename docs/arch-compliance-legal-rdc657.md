# Arquitetura: Compliance Legal - RDC 657/2022 e Ato Médico

**Arquiteto:** Winston  
**Contexto:** Reestruturação por Compliance Legal  
**Objetivo:** Garantir que o sistema seja classificado como Diretório de Dados Administrativos, não como SaMD

**Data:** {{date}}

---

## 🚨 Visão Geral - Mudança Crítica de Escopo

### Problema Identificado
Identificamos **risco legal** em utilizar inferência ("adivinhação") de serviços. Não somos médicos e o software **não pode realizar triagem ou induzir o paciente** com base em suposições.

### Base Legal
- **RDC 657/2022** - Regulamentação de Dispositivos Médicos
- **Ato Médico** - Lei que regulamenta o exercício da medicina
- **Classificação SaMD** - Software as Medical Device

### Nova Diretriz
O sistema deve atuar estritamente como um **Diretório de Dados Administrativos** (ferramenta de consulta/informação), não como Dispositivo Médico de Diagnóstico.

---

## 🏗️ Alterações Arquiteturais Obrigatórias

### 1. Remover Lógica de Inferência

#### ❌ LÓGICA REMOVIDA (Não pode mais existir)
- Função de detecção automática por palavras-chave
- Smart Check que tenta adivinhar se hospital tem maternidade
- Qualquer inferência baseada apenas no nome do hospital

#### ✅ NOVA LÓGICA
- **Apenas dados oficiais:** Banco de dados validado manualmente OU API CNES
- **Sem inferência:** Se dado for null, sistema retorna estado neutro
- **Transparência:** Usuário sempre informado sobre origem dos dados

---

## 📊 Estados do Sistema

### Estado 1: Confirmado (Oficial) - hasMaternity === true

#### Fonte dos Dados
- ✅ Banco de dados validado manualmente
- ✅ API CNES (Cadastro Nacional de Estabelecimentos de Saúde)
- ❌ **NUNCA** inferência automática

#### Exibição
- **Texto:** "Possui Ala Maternal" ou "Ala Maternal Habilitada"
- **Cor:** Verde (SUCCESS)
- **Ícone:** ✅
- **Confiança:** Alta (dado oficial)

---

### Estado 2: Sem Informação (Neutro) - hasMaternity === null

#### Fonte dos Dados
- Dado não disponível no banco
- Dado não disponível via API CNES
- **NÃO tentar inferir ou adivinhar**

#### Exibição
- **Texto:** "Informação sobre maternidade não disponível no cadastro" OU "Atendimento Geral / Ligue 192"
- **Cor:** Cinza (INFO - Neutro)
- **Ícone:** ℹ️ ou 📞
- **Confiança:** N/A (sem informação)

#### Regra Crítica
**NUNCA exibir "Não possui" quando o dado for null** - isso é inferência não autorizada.

---

### Estado 3: Negativo Confirmado - hasMaternity === false

#### Fonte dos Dados
- Banco de dados validado manualmente (confirmação de que não possui)
- API CNES (confirmação de que não possui)
- **Certeza absoluta**

#### Exibição
- **Texto:** "Não possui Ala Maternal"
- **Cor:** Laranja/Vermelho (ERROR/WARNING)
- **Ícone:** ⚠️
- **Confiança:** Alta (dado oficial)

---

## 🛡️ Proteções Legais Implementadas

### 1. Disclaimer Obrigatório

#### Localização
- Rodapé da lista de hospitais
- OU topo da lista de hospitais
- OU ambos (recomendado)

#### Texto Sugerido
```
"⚠️ Importante: As informações exibidas são baseadas no cadastro oficial de estabelecimentos de saúde (CNES/DATASUS). 
Em caso de emergência, ligue 192 (SAMU). 
Para confirmação de serviços disponíveis, consulte diretamente o estabelecimento por telefone."
```

#### Versão Curta (Para Mobile)
```
"ℹ️ Dados oficiais. Em emergência: 192. Confirme serviços por telefone."
```

---

### 2. Classificação do Sistema

#### Classificação Atual
- **Tipo:** Diretório de Dados Administrativos
- **Função:** Consulta de informações cadastrais
- **NÃO é:** Dispositivo Médico de Diagnóstico (SaMD)
- **NÃO é:** Ferramenta de triagem médica
- **NÃO é:** Sistema de recomendação médica

#### Justificativa
- Sistema apenas **exibe dados cadastrais oficiais**
- Não realiza **diagnóstico ou triagem**
- Não **recomenda** tratamento ou conduta médica
- Usuário toma decisão final (com ou sem dados)

---

## 🗄️ Estrutura de Dados Atualizada

### Schema: hospitals

```sql
CREATE TABLE IF NOT EXISTS hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    address TEXT,
    city TEXT,
    state TEXT,
    phone TEXT,
    website TEXT,
    
    -- Campo de Maternidade (Obrigatório: apenas valores oficiais)
    hasMaternityWard BOOLEAN,  -- NULL = sem informação, true/false = confirmado oficialmente
    hasMaternityWardSource TEXT,  -- 'manual' | 'cnes' | NULL (origem do dado)
    hasMaternityWardValidatedAt TIMESTAMP,  -- Data da validação oficial
    
    -- Campos CNES
    cnes TEXT UNIQUE,
    cnes_validated_at TIMESTAMP,
    
    isEmergency BOOLEAN,
    acceptsSUS BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Regras de Validação
- **hasMaternityWard = true:** Apenas se validado manualmente OU via API CNES
- **hasMaternityWard = false:** Apenas se confirmado oficialmente (não possui)
- **hasMaternityWard = null:** Padrão quando informação não está disponível
- **NUNCA** preencher true/false baseado em inferência automática

---

## 🔧 Arquitetura de Validação

### Fluxo de Validação de Dados

```
1. Busca Hospital (Overpass API / Google Places)
   ↓
2. Tentar buscar CNES (API CNES)
   ↓
3. Se CNES encontrado:
   → Consultar serviços habilitados via API CNES
   → hasMaternityWard = true/false (baseado em CNES)
   → hasMaternityWardSource = 'cnes'
   ↓
4. Se CNES não encontrado:
   → hasMaternityWard = null (NÃO INFERIR)
   → hasMaternityWardSource = null
   ↓
5. Renderização:
   → true → Badge verde "Possui Ala Maternal"
   → false → Badge laranja "Não possui Ala Maternal"
   → null → Badge cinza "Informação não disponível"
```

### Validação Manual (Admin)

#### Interface de Administração
- Permitir edição manual de `hasMaternityWard`
- Requerir confirmação de fonte (CNES, validação manual, etc.)
- Registrar data/hora e usuário da validação
- Permitir apenas valores: `true`, `false`, `null`

---

## 📋 Checklist de Implementação

### Backend
- [ ] Remover função de detecção automática (palavras-chave)
- [ ] Atualizar schema: adicionar `hasMaternityWardSource`
- [ ] Implementar validação: apenas dados oficiais (CNES ou manual)
- [ ] API: nunca retornar true/false baseado em inferência
- [ ] Endpoint de validação manual (admin) com auditoria

### Frontend
- [ ] Remover lógica de Smart Check (palavras-chave)
- [ ] Implementar 3 estados apenas: true/false/null
- [ ] Estado null: exibir texto neutro (não "não possui")
- [ ] Adicionar disclaimer obrigatório
- [ ] Atualizar funções de renderização

### Documentação
- [ ] Atualizar documentação: classificação como Diretório de Dados
- [ ] Documentar fontes de dados aceitas (CNES, manual)
- [ ] Documentar proibições (inferência automática)
- [ ] Adicionar disclaimer em termos de uso

### Compliance
- [ ] Revisar com equipe jurídica
- [ ] Validar classificação (não é SaMD)
- [ ] Confirmar que não viola RDC 657/2022
- [ ] Confirmar que não viola Ato Médico

---

## ⚠️ Riscos Mitigados

### Risco 1: Falso-Positivo
- **Antes:** Sistema podia indicar "Provável Maternidade" baseado apenas no nome
- **Depois:** Apenas dados oficiais (CNES/manual) podem indicar presença
- **Mitigação:** Remoção completa de inferência automática

### Risco 2: Exercício Ilegal da Medicina
- **Antes:** Sistema podia sugerir conduta médica (induzir paciente)
- **Depois:** Sistema apenas informa dados cadastrais, não recomenda
- **Mitigação:** Estado neutro para informações não confirmadas

### Risco 3: Classificação como SaMD
- **Antes:** Sistema podia ser interpretado como dispositivo médico
- **Depois:** Claramente classificado como Diretório de Dados Administrativos
- **Mitigação:** Disclaimer explícito + remoção de inferência

---

## 📝 Notas para o Time

### Para @architect
- **Prioridade:** Validar arquitetura com equipe jurídica
- **Validar:** Classificação do sistema (não é SaMD)
- **Documentar:** Fontes de dados aceitas e proibidas

### Para @po
- **Atualizar:** Regras de negócio (remover inferência)
- **Validar:** Textos de exibição (compliance)
- **Documentar:** Estados do sistema (3 estados apenas)

### Para @dev
- **Implementar:** Remoção de lógica de inferência
- **Implementar:** 3 estados apenas (true/false/null)
- **Implementar:** Disclaimer obrigatório

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial: Reestruturação por Compliance Legal | Architect (Winston) |
