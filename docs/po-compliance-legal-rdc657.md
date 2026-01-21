# Regras de Negócio: Compliance Legal - RDC 657/2022

**Product Owner:** Sarah  
**Contexto:** Atualização de Regras de Negócio por Compliance Legal  
**Objetivo:** Garantir compliance com RDC 657/2022 e Ato Médico

**Data:** {{date}}

---

## 🚨 Mudança Crítica de Escopo

### Contexto Legal
Identificamos **risco legal crítico** em utilizar inferência ("adivinhação") de serviços. O sistema não pode realizar triagem ou induzir o paciente com base em suposições.

### Base Legal
- **RDC 657/2022** - Regulamentação de Dispositivos Médicos
- **Ato Médico** - Lei que regulamenta o exercício da medicina
- **Classificação:** Sistema deve ser Diretório de Dados Administrativos, NÃO SaMD

---

## 📋 Regras de Negócio Atualizadas

### RN-001: Remoção de Lógica de Inferência (CRÍTICO)

#### Regra
**O sistema NÃO PODE, em hipótese alguma, inferir ou adivinhar se um hospital possui serviço de maternidade baseado apenas no nome do local.**

#### Aplicação
- ❌ **PROIBIDO:** Detecção automática por palavras-chave
- ❌ **PROIBIDO:** Smart Check que tenta adivinhar
- ❌ **PROIBIDO:** Qualquer inferência baseada em nome/descrição
- ✅ **PERMITIDO:** Apenas dados oficiais (CNES ou validação manual)

#### Justificativa Legal
Inferência incorreta pode ser interpretada como exercício ilegal da medicina ou triagem médica não autorizada.

---

### RN-002: Estados do Sistema (3 Estados Apenas)

#### Estado 1: Confirmado (Oficial) - hasMaternityWard = true

**Fonte Aceita:**
- ✅ API CNES (validação oficial)
- ✅ Validação manual (administrador)
- ❌ NUNCA inferência automática

**Exibição:**
- **Texto:** "Possui Ala Maternal" ou "Ala Maternal Habilitada"
- **Cor:** Verde (SUCCESS)
- **Ícone:** ✅
- **Badge:** `tipo: 'SUCCESS'`

**Condição:**
- Apenas quando dados oficiais confirmam presença do serviço

---

#### Estado 2: Sem Informação (Neutro) - hasMaternityWard = null

**Fonte:**
- Dado não disponível no banco
- Dado não disponível via API CNES
- **NÃO tentar inferir**

**Exibição:**
- **Texto:** "Informação sobre maternidade não disponível no cadastro" OU "Atendimento Geral / Ligue 192"
- **Cor:** Cinza (INFO - Neutro)
- **Ícone:** ℹ️ ou 📞
- **Badge:** `tipo: 'INFO'`

**Condição:**
- Quando informação não está disponível (padrão)

**Regra Crítica:**
- **NUNCA** exibir "Não possui" quando null
- **NUNCA** tentar adivinhar baseado em nome
- **SEMPRE** exibir texto neutro e informativo

---

#### Estado 3: Negativo Confirmado - hasMaternityWard = false

**Fonte Aceita:**
- ✅ API CNES (confirmação de que não possui)
- ✅ Validação manual (administrador confirmou que não possui)
- ❌ NUNCA inferência automática

**Exibição:**
- **Texto:** "Não possui Ala Maternal"
- **Cor:** Laranja/Vermelho (ERROR/WARNING)
- **Ícone:** ⚠️
- **Badge:** `tipo: 'ERROR'`

**Condição:**
- Apenas quando dados oficiais confirmam ausência do serviço

---

### RN-003: Fontes de Dados Aceitas

#### Fontes Válidas (Apenas)
1. **API CNES (Dados Abertos SUS)**
   - Validação oficial de serviços habilitados
   - Consulta pública e confiável
   - Status: Aceita

2. **Validação Manual (Administrador)**
   - Administrador do sistema valida manualmente
   - Requer auditoria (quem, quando, fonte)
   - Status: Aceita

3. **Banco de Dados Prévio**
   - Dados validados anteriormente (CNES ou manual)
   - Requer registro de origem
   - Status: Aceita

#### Fontes Proibidas
- ❌ Inferência automática (palavras-chave)
- ❌ Detecção por nome do hospital
- ❌ Smart Check baseado em descrição
- ❌ Qualquer método que não seja validação oficial

---

### RN-004: Disclaimer Obrigatório

#### Regra
**O sistema DEVE exibir disclaimer informando que dados são baseados em cadastro oficial e que o usuário deve confirmar por telefone em casos não emergenciais.**

#### Localização
- Rodapé da lista de hospitais (obrigatório)
- Topo da lista de hospitais (recomendado)
- Ambos (melhor opção)

#### Texto Padrão (Versão Completa)
```
"⚠️ Importante: As informações exibidas são baseadas no cadastro oficial de estabelecimentos de saúde (CNES/DATASUS). 
Em caso de emergência, ligue 192 (SAMU). 
Para confirmação de serviços disponíveis, consulte diretamente o estabelecimento por telefone."
```

#### Texto Padrão (Versão Curta - Mobile)
```
"ℹ️ Dados oficiais. Em emergência: 192. Confirme serviços por telefone."
```

#### Texto Padrão (Versão Mínima)
```
"ℹ️ Informações oficiais. Confirme serviços por telefone."
```

---

### RN-005: Classificação do Sistema

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
- Não **induz** o paciente a tomar decisão específica

---

## ✅ Critérios de Aceite Atualizados

### AC-001: Remoção de Inferência Automática

**DADO** que o sistema processa informações de hospitais  
**QUANDO** o campo `hasMaternityWard` é `null`  
**ENTÃO** o sistema DEVE exibir estado neutro ("Informação não disponível")  
**E** NÃO DEVE tentar inferir baseado em nome/descrição  
**E** NÃO DEVE exibir "Não possui"  

**Prioridade:** 🔴 **CRÍTICA** - Compliance Legal

---

### AC-002: Estados do Sistema (3 Estados Apenas)

**DADO** que o sistema exibe informações de maternidade  
**QUANDO** renderiza o card do hospital  
**ENTÃO** DEVE exibir apenas um dos 3 estados:
1. `true` (oficial) → Badge verde "Possui Ala Maternal"
2. `false` (oficial) → Badge laranja "Não possui Ala Maternal"
3. `null` (sem informação) → Badge cinza "Informação não disponível"

**Prioridade:** 🔴 **CRÍTICA** - Compliance Legal

---

### AC-003: Disclaimer Obrigatório

**DADO** que o sistema exibe lista de hospitais  
**QUANDO** a lista é renderizada  
**ENTÃO** DEVE exibir disclaimer informando:
- Dados são baseados em cadastro oficial
- Em emergência, ligar 192
- Confirmar serviços por telefone

**Prioridade:** 🔴 **ALTA** - Compliance Legal

---

### AC-004: Fontes de Dados Aceitas

**DADO** que o sistema valida informações de maternidade  
**QUANDO** atribui valor `true` ou `false` a `hasMaternityWard`  
**ENTÃO** valor DEVE vir apenas de:
- API CNES (validação oficial)
- Validação manual (administrador)
- Banco de dados pré-validado

**E** NÃO DEVE vir de:
- Inferência automática
- Detecção por palavras-chave
- Smart Check baseado em nome

**Prioridade:** 🔴 **CRÍTICA** - Compliance Legal

---

## 🔒 Regras de Segurança Jurídica

### RSJ-001: Princípio da Neutralidade
> **"Quando informação não está disponível, sistema deve permanecer neutro. NUNCA inferir ou adivinhar."**

**Aplicação:**
- `hasMaternityWard = null` → Estado neutro sempre
- NUNCA tentar preencher null com inferência
- NUNCA exibir "não possui" quando null

---

### RSJ-002: Princípio da Transparência
> **"Sistema deve sempre informar origem dos dados e limitações."**

**Aplicação:**
- Disclaimer obrigatório sobre origem dos dados
- Usuário informado sobre necessidade de confirmar
- Sistema não oculta limitações

---

### RSJ-003: Princípio da Não-Indução
> **"Sistema não deve induzir paciente a tomar decisão médica específica."**

**Aplicação:**
- Apenas exibe dados cadastrais
- Não recomenda conduta
- Não sugere tratamento
- Usuário toma decisão final

---

## 📊 Matriz de Decisão

| Valor BD | Fonte | Exibição | Badge Tipo | Justificativa |
|----------|-------|----------|------------|---------------|
| `true` | CNES | "Possui Ala Maternal" | SUCCESS (Verde) | Dado oficial confirmado |
| `true` | Manual | "Possui Ala Maternal" | SUCCESS (Verde) | Dado validado manualmente |
| `false` | CNES | "Não possui Ala Maternal" | ERROR (Laranja) | Dado oficial confirmado |
| `false` | Manual | "Não possui Ala Maternal" | ERROR (Laranja) | Dado validado manualmente |
| `null` | N/A | "Informação não disponível" | INFO (Cinza) | Sem informação oficial |
| `null` | Inferência | ❌ PROIBIDO | ❌ PROIBIDO | Inferência não permitida |

---

## 📝 Notas para o Time

### Para @po (Product Owner)
- **Prioridade:** Validar regras com equipe jurídica
- **Documentar:** Mudanças de regras de negócio
- **Comunicar:** Impacto da mudança para stakeholders

### Para @architect
- **Validar:** Arquitetura atende novas regras
- **Documentar:** Fontes de dados aceitas e proibidas
- **Garantir:** Sistema classificado corretamente

### Para @dev
- **Implementar:** Remoção de lógica de inferência
- **Implementar:** 3 estados apenas (true/false/null)
- **Implementar:** Disclaimer obrigatório
- **Testar:** Nenhuma inferência automática funciona

### Para @qa
- **Testar:** Estados do sistema (3 estados apenas)
- **Testar:** Disclaimer exibido corretamente
- **Testar:** Nenhuma inferência automática funciona
- **Validar:** Compliance com regras legais

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial: Atualização de Regras de Negócio por Compliance Legal | PO (Sarah) |
