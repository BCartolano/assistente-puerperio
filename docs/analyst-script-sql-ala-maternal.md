# Script SQL: Atualização de Hospitais - Ala Maternal

**Analyst:** Mary  
**Contexto:** Atualização de hospitais específicos para `hasMaternityWard = true` baseado em lista oficial  
**Objetivo:** Gerar script SQL para atualizar hospitais X, Y e Z conforme lista oficial

**Data:** {{date}}

---

## 📋 Visão Geral

### Objetivo
Atualizar hospitais específicos (Hospital X, Y e Z) para `hasMaternityWard = true` baseado em lista oficial.

### Contexto
- Lista oficial confirma que determinados hospitais possuem Ala Maternal
- Necessário atualizar banco de dados para refletir essa informação
- Script deve ser seguro (não afetar outros hospitais)

---

## 🔧 Script SQL

### Script Base (Template)

```sql
-- =====================================================
-- Script de Atualização: Hospitais com Ala Maternal
-- Baseado em: Lista Oficial de Hospitais com Maternidade
-- Data: {{date}}
-- Autor: Analyst (Mary)
-- =====================================================

-- IMPORTANTE: Substituir os nomes dos hospitais (Hospital X, Y, Z) 
-- pelos nomes reais conforme lista oficial antes de executar

BEGIN TRANSACTION;

-- Verificar hospitais antes da atualização
SELECT 
    id,
    name,
    hasMaternityWard,
    city,
    address
FROM hospitals
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
)
ORDER BY name;

-- Atualizar hospitais específicos para hasMaternityWard = true
UPDATE hospitals
SET 
    hasMaternityWard = true,
    updated_at = CURRENT_TIMESTAMP
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
);

-- Verificar resultado da atualização
SELECT 
    id,
    name,
    hasMaternityWard,
    city,
    address,
    updated_at
FROM hospitals
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
)
ORDER BY name;

-- Verificar quantos registros foram atualizados
SELECT 
    COUNT(*) as total_atualizados
FROM hospitals
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
)
AND hasMaternityWard = true;

-- Confirmar transação
COMMIT;

-- Em caso de erro, executar: ROLLBACK;
```

---

## 📝 Script com Nomes de Exemplo

### Exemplo: Hospitais com Nomes Reais (Substituir pelos reais)

```sql
-- =====================================================
-- Script de Atualização: Hospitais com Ala Maternal
-- Baseado em: Lista Oficial de Hospitais com Maternidade
-- Data: {{date}}
-- Autor: Analyst (Mary)
-- =====================================================

BEGIN TRANSACTION;

-- Verificar hospitais antes da atualização
SELECT 
    id,
    name,
    hasMaternityWard,
    city,
    address
FROM hospitals
WHERE name IN (
    'Hospital das Clínicas',
    'Hospital Sírio-Libanês',
    'Hospital Albert Einstein'
)
ORDER BY name;

-- Atualizar hospitais específicos para hasMaternityWard = true
UPDATE hospitals
SET 
    hasMaternityWard = true,
    updated_at = CURRENT_TIMESTAMP
WHERE name IN (
    'Hospital das Clínicas',
    'Hospital Sírio-Libanês',
    'Hospital Albert Einstein'
);

-- Verificar resultado da atualização
SELECT 
    id,
    name,
    hasMaternityWard,
    city,
    address,
    updated_at
FROM hospitals
WHERE name IN (
    'Hospital das Clínicas',
    'Hospital Sírio-Libanês',
    'Hospital Albert Einstein'
)
ORDER BY name;

-- Verificar quantos registros foram atualizados
SELECT 
    COUNT(*) as total_atualizados
FROM hospitals
WHERE name IN (
    'Hospital das Clínicas',
    'Hospital Sírio-Libanês',
    'Hospital Albert Einstein'
)
AND hasMaternityWard = true;

-- Confirmar transação
COMMIT;
```

---

## 🔍 Script com Busca por ID (Alternativa)

### Se tiver os IDs dos hospitais

```sql
-- =====================================================
-- Script de Atualização: Hospitais com Ala Maternal (por ID)
-- Baseado em: Lista Oficial de Hospitais com Maternidade
-- Data: {{date}}
-- Autor: Analyst (Mary)
-- =====================================================

BEGIN TRANSACTION;

-- Verificar hospitais antes da atualização
SELECT 
    id,
    name,
    hasMaternityWard,
    city,
    address
FROM hospitals
WHERE id IN (1, 2, 3)  -- ⚠️ SUBSTITUIR pelos IDs reais dos hospitais
ORDER BY name;

-- Atualizar hospitais específicos para hasMaternityWard = true
UPDATE hospitals
SET 
    hasMaternityWard = true,
    updated_at = CURRENT_TIMESTAMP
WHERE id IN (1, 2, 3);  -- ⚠️ SUBSTITUIR pelos IDs reais dos hospitais

-- Verificar resultado da atualização
SELECT 
    id,
    name,
    hasMaternityWard,
    city,
    address,
    updated_at
FROM hospitals
WHERE id IN (1, 2, 3)  -- ⚠️ SUBSTITUIR pelos IDs reais dos hospitais
ORDER BY name;

-- Confirmar transação
COMMIT;
```

---

## 🛡️ Script com Validação e Segurança

### Versão Mais Segura (com validações)

```sql
-- =====================================================
-- Script de Atualização: Hospitais com Ala Maternal (Versão Segura)
-- Baseado em: Lista Oficial de Hospitais com Maternidade
-- Data: {{date}}
-- Autor: Analyst (Mary)
-- =====================================================

BEGIN TRANSACTION;

-- 1. Verificar se hospitais existem antes de atualizar
SELECT 
    id,
    name,
    hasMaternityWard,
    city,
    address
FROM hospitals
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
)
ORDER BY name;

-- 2. Validar que todos os hospitais foram encontrados
-- (Verificar manualmente que o número de linhas retornadas é igual ao número de hospitais na lista)

-- 3. Atualizar apenas hospitais que existem no banco
UPDATE hospitals
SET 
    hasMaternityWard = true,
    updated_at = CURRENT_TIMESTAMP
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
)
AND EXISTS (
    SELECT 1 FROM hospitals h2 
    WHERE h2.name = hospitals.name
);

-- 4. Verificar resultado da atualização
SELECT 
    id,
    name,
    hasMaternityWard,
    city,
    address,
    updated_at
FROM hospitals
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
)
ORDER BY name;

-- 5. Confirmar que todos foram atualizados corretamente
SELECT 
    COUNT(*) as total_encontrados,
    SUM(CASE WHEN hasMaternityWard = true THEN 1 ELSE 0 END) as total_com_maternidade,
    SUM(CASE WHEN hasMaternityWard = false THEN 1 ELSE 0 END) as total_sem_maternidade
FROM hospitals
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
);

-- 6. Se tudo estiver correto, confirmar transação
COMMIT;

-- Em caso de erro, executar: ROLLBACK;
```

---

## 📊 Script de Validação (Pós-Execução)

### Verificar se atualização foi bem-sucedida

```sql
-- =====================================================
-- Script de Validação: Verificar Atualização de Hospitais
-- Data: {{date}}
-- Autor: Analyst (Mary)
-- =====================================================

-- Verificar todos os hospitais atualizados
SELECT 
    id,
    name,
    hasMaternityWard,
    city,
    address,
    updated_at
FROM hospitals
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
)
ORDER BY name;

-- Verificar estatísticas
SELECT 
    COUNT(*) as total_hospitais,
    SUM(CASE WHEN hasMaternityWard = true THEN 1 ELSE 0 END) as com_maternidade,
    SUM(CASE WHEN hasMaternityWard = false THEN 1 ELSE 0 END) as sem_maternidade
FROM hospitals
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
);

-- Verificar que todos têm hasMaternityWard = true
SELECT 
    name,
    hasMaternityWard
FROM hospitals
WHERE name IN (
    'Hospital X',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital X
    'Hospital Y',  -- ⚠️ SUBSTITUIR pelo nome real do Hospital Y
    'Hospital Z'   -- ⚠️ SUBSTITUIR pelo nome real do Hospital Z
)
AND hasMaternityWard != true;  -- Deve retornar 0 linhas
```

---

## 📝 Instruções de Uso

### Passo 1: Preparar Lista de Hospitais
1. Obter lista oficial de hospitais com Ala Maternal
2. Identificar nomes exatos dos hospitais no banco de dados
3. Verificar se nomes estão corretos (pode variar: "Hospital X" vs "Hospital X - Unidade Centro")

### Passo 2: Substituir Nomes no Script
1. Abrir script SQL
2. Substituir `'Hospital X'`, `'Hospital Y'`, `'Hospital Z'` pelos nomes reais
3. Verificar que nomes estão entre aspas simples

### Passo 3: Executar Script
1. **IMPORTANTE:** Fazer backup do banco de dados antes de executar
2. Executar script em ambiente de desenvolvimento/teste primeiro
3. Verificar resultado (SELECT antes e depois)
4. Se tudo estiver correto, executar em produção

### Passo 4: Validar Resultado
1. Executar script de validação
2. Verificar que todos os hospitais foram atualizados corretamente
3. Verificar que `hasMaternityWard = true` para todos os hospitais da lista

---

## ⚠️ Avisos Importantes

### Segurança
- ✅ **SEMPRE** fazer backup do banco antes de executar
- ✅ **SEMPRE** testar em ambiente de desenvolvimento primeiro
- ✅ **SEMPRE** usar transações (BEGIN TRANSACTION / COMMIT / ROLLBACK)
- ✅ **SEMPRE** verificar resultado antes de confirmar transação

### Validação
- ✅ Verificar que nomes dos hospitais estão corretos
- ✅ Verificar que todos os hospitais foram encontrados
- ✅ Verificar que todos foram atualizados corretamente

---

## 📋 Checklist de Execução

### Antes de Executar
- [ ] Backup do banco de dados feito
- [ ] Lista oficial de hospitais obtida
- [ ] Nomes dos hospitais verificados no banco
- [ ] Script testado em ambiente de desenvolvimento
- [ ] Script validado por outro desenvolvedor/DBA

### Durante Execução
- [ ] Transação iniciada (BEGIN TRANSACTION)
- [ ] SELECT antes da atualização executado
- [ ] Resultado do SELECT verificado
- [ ] UPDATE executado
- [ ] SELECT depois da atualização executado
- [ ] Resultado do SELECT verificado
- [ ] Transação confirmada (COMMIT)

### Depois de Executar
- [ ] Script de validação executado
- [ ] Todos os hospitais atualizados corretamente
- [ ] `hasMaternityWard = true` para todos os hospitais da lista
- [ ] Log da execução salvo

---

## 📝 Notas para o Time

### Para @analyst (Analyst)
- **Gerar:** Lista oficial de hospitais com Ala Maternal
- **Verificar:** Nomes exatos dos hospitais no banco de dados
- **Validar:** Script antes de passar para desenvolvimento

### Para @dev (Desenvolvedor)
- **Executar:** Script em ambiente de desenvolvimento primeiro
- **Validar:** Resultado antes de executar em produção
- **Testar:** Verificar que atualização não afeta outros hospitais

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial do script SQL | Analyst (Mary) |
