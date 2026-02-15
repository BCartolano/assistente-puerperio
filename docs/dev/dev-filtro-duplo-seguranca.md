# Implementação: Filtro Duplo Obrigatório de Segurança no Localizador

**Desenvolvedor:** James  
**Contexto:** Regra de segurança crítica para prevenir direcionamento incorreto  
**Objetivo:** Garantir que apenas hospitais com infraestrutura completa e equipe especializada apareçam

**Data:** {{date}}

---

## 🎯 Objetivo

Implementar validação dupla obrigatória para garantir que apenas estabelecimentos que atendam **AMBAS** as condições simultaneamente sejam exibidos:

1. **Classificação:** Ser do tipo "Hospital" (excluir UBS, Clínicas, UPAs, Postos, etc)
2. **Infraestrutura:** Possuir explicitamente "Ala de Maternidade" ou "Serviço de Obstetrícia" ativo

---

## ⚠️ Justificativa de Segurança

### Problema Identificado
Hospitais gerais sem ala de maternidade, embora obrigados por lei a prestar primeiro socorro, não possuem:
- Equipe técnica adequada (neonatologistas/obstetras de plantão)
- Infraestrutura adequada (incubadoras, UTI neonatal)
- Requisitos para partos complexos

### Risco
Direcionar gestantes para hospitais sem infraestrutura adequada:
- Requer transferência posterior (perda de tempo crítico)
- Coloca em risco a vida do recém-nascido
- Gera falsa sensação de segurança

### Solução
O localizador deve mostrar **APENAS** o destino definitivo e seguro: hospitais com infraestrutura completa de maternidade confirmada.

---

## 💻 Implementação Técnica

### 1. Função de Validação de TIPO

```javascript
validateHospitalType(tags, hospitalName)
```

**Responsabilidade:** Verificar se o estabelecimento é realmente um "Hospital"

**Exclui:**
- UBS (Unidade Básica de Saúde)
- Clínicas
- UPAs (Unidade de Pronto Atendimento)
- Postos de Saúde
- Centros de Saúde
- Ambulatórios
- Consultórios
- Laboratórios
- Farmácias
- Policlínicas

**Lógica:**
1. Verifica se o nome contém palavras de exclusão
2. Se contiver palavra de exclusão E não contiver "hospital" no nome → **REJEITA**
3. Verifica se é do tipo `healthcare=hospital` ou `healthcare=maternity`
4. Verifica se tem `amenity=hospital`
5. Aceita se: tem palavra de inclusão OU é do tipo hospital OU tem amenity=hospital

**Palavras-chave de inclusão:**
- "hospital"
- "maternidade" (são hospitais especializados)
- "hsp" (abreviação)
- "hosp." (abreviação)

---

### 2. Função de Validação de INFRAESTRUTURA

```javascript
validateMaternityInfrastructure(tags, hospitalName, specialty, healthcare)
```

**Responsabilidade:** Verificar se o hospital possui infraestrutura confirmada de maternidade

**Indicadores explícitos:**
- "maternidade" / "maternity"
- "obstetrícia" / "obstetrics"
- "ala maternal" / "ala de maternidade"
- "mulher" / "women" / "saúde da mulher"
- "ginecologia" / "gynaecology"
- "parto" / "birth" / "centro de parto"

**Lógica:**
1. Verifica no nome do estabelecimento
2. Verifica na especialidade (`healthcare:speciality`)
3. Verifica no tipo de healthcare (`healthcare`)
4. Verifica nas tags OSM (`healthcare:speciality`)
5. Aceita se encontrar indicador em **QUALQUER** uma das fontes

---

### 3. Aplicação do Filtro Duplo

**Localização:** `searchHospitalsNearby()` - Loop de processamento de elementos

**Fluxo:**
```javascript
for (const element of data.elements) {
    // ... processa dados básicos ...
    
    // ========================================
    // FILTRO DUPLO OBRIGATÓRIO DE SEGURANÇA
    // ========================================
    
    // REGRA 1: Validar TIPO
    const isValidHospitalType = this.validateHospitalType(element.tags, hospitalName);
    if (!isValidHospitalType) {
        continue; // REJEITA: Não é hospital
    }
    
    // REGRA 2: Validar INFRAESTRUTURA
    const hasMaternityInfrastructure = this.validateMaternityInfrastructure(
        element.tags, 
        hospitalName, 
        specialty, 
        healthcare
    );
    if (!hasMaternityInfrastructure) {
        continue; // REJEITA: Sem infraestrutura confirmada
    }
    
    // Se chegou aqui, passou no filtro duplo obrigatório
    // ========================================
    
    // Marca como maternidade confirmada
    const isMaternity = true; // Confirmado pelo filtro duplo
    
    // ... cria objeto hospital e adiciona à lista ...
}
```

---

## 📊 Resultado

### Antes
- Exibia qualquer estabelecimento com `amenity=hospital`
- Podia incluir UBS, Clínicas, UPAs disfarçadas
- Podia incluir hospitais gerais sem ala de maternidade
- Usuário podia ser direcionado para local sem infraestrutura adequada

### Depois
- Exibe **APENAS** hospitais que passaram no filtro duplo
- **TODOS** os hospitais exibidos têm:
  - ✅ Tipo confirmado como "Hospital"
  - ✅ Infraestrutura de maternidade confirmada
- Mensagem na interface: "Encontrados X hospital(is) com Ala de Maternidade confirmada próximo(s):"
- Badge em cada card: "✅ Ala de Maternidade Confirmada"

---

## ✅ Checklist de Implementação

### Validação de TIPO
- [x] Função `validateHospitalType()` criada
- [x] Lista de palavras-chave de exclusão implementada
- [x] Lista de palavras-chave de inclusão implementada
- [x] Validação de `healthcare` tipo
- [x] Validação de `amenity` tipo
- [x] Lógica de exceções (ex: "Hospital da Mulher" contém "mulher" mas também "hospital")

### Validação de INFRAESTRUTURA
- [x] Função `validateMaternityInfrastructure()` criada
- [x] Lista de indicadores de maternidade implementada
- [x] Verificação no nome
- [x] Verificação na especialidade
- [x] Verificação no tipo de healthcare
- [x] Verificação nas tags OSM

### Aplicação do Filtro
- [x] Filtro duplo aplicado no loop de processamento
- [x] Hospitais rejeitados são ignorados (continue)
- [x] Apenas hospitais aprovados são adicionados à lista
- [x] `isMaternity` sempre `true` para hospitais exibidos

### Interface
- [x] Mensagem atualizada: "com Ala de Maternidade confirmada"
- [x] Badge "✅ Ala de Maternidade Confirmada" em todos os cards
- [x] Removida lógica antiga de detecção por palavras-chave

---

## 🔍 Validação e Testes

### Cenários de Teste

#### ✅ Deve INCLUIR:
1. "Hospital da Mulher" → ✅ Tipo: Hospital | ✅ Infra: Maternidade
2. "Maternidade Municipal" → ✅ Tipo: Maternidade | ✅ Infra: Maternidade
3. "Hospital Geral com Obstetrícia" → ✅ Tipo: Hospital | ✅ Infra: Obstetrícia
4. "Hospital São Paulo" (com tag `healthcare:speciality=obstetrics`) → ✅ Tipo: Hospital | ✅ Infra: Obstetrics

#### ❌ Deve EXCLUIR:
1. "UBS Centro" → ❌ Tipo: UBS (não é hospital)
2. "Clínica Médica ABC" → ❌ Tipo: Clínica (não é hospital)
3. "Hospital Geral" (sem tags de maternidade) → ❌ Tipo: Hospital | ❌ Infra: Sem maternidade
4. "UPA 24h" → ❌ Tipo: UPA (não é hospital)
5. "Posto de Saúde Municipal" → ❌ Tipo: Posto (não é hospital)

---

## 📝 Notas Importantes

### Regra de Segurança
- **CRÍTICO:** O filtro duplo é obrigatório. Um hospital só aparece se passar em AMBAS as validações.
- **Não há exceções:** Mesmo que seja um hospital reconhecido, se não tiver infraestrutura confirmada, não aparece.

### Logging e Debug
- Em modo de desenvolvimento, considere adicionar logs para hospitais rejeitados
- Isso ajuda a validar se o filtro está funcionando corretamente

### Futuras Melhorias
- Integração com API CNES (SUS Dados Abertos) para validação oficial
- Cache de resultados validados para melhor performance
- Interface para reportar falsos positivos/negativos

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Implementação do filtro duplo obrigatório | Dev (James) |
