# Arquitetura: Visualização de Ala Maternal

**Arquiteto:** Winston  
**Contexto:** Sistema de Localizador de Hospitais - Feature: Visualização Clara de Ala Maternal  
**Objetivo:** Definir estrutura de dados e lógica de ordenação para exibição de hospitais

**Data:** {{date}}

---

## 🏗️ Visão Geral

### Problema Técnico
O Frontend precisa exibir se um hospital tem maternidade ou não, mas o banco de dados atual tem inconsistências (campos nulos). Além disso, precisamos ordenar a lista priorizando quem tem o serviço.

### Solução Proposta
1. **Schema de Dados:** Adicionar campo `hasMaternityWard` (BOOLEAN, não nullable, default false)
2. **Algoritmo de Ordenação:** Priorizar hospitais com `hasMaternityWard = true`, depois ordenar por proximidade
3. **Sanitização:** Script para converter `NULL` → `false` no banco de dados

---

## 📊 Estrutura de Dados

### Objeto Hospital (JSON)

#### Versão Atual (Referência)
```json
{
  "id": 1,
  "name": "Hospital Exemplo",
  "lat": -23.5505,
  "lon": -46.6333,
  "address": "Rua Exemplo, 123",
  "city": "São Paulo",
  "phone": "(11) 1234-5678",
  "website": "https://exemplo.com",
  "distance": 2500,
  "isMaternity": false,
  "isEmergency": true,
  "acceptsSUS": true
}
```

#### Versão Proposta (Atualizada)
```json
{
  "id": 1,
  "name": "Hospital Exemplo",
  "lat": -23.5505,
  "lon": -46.6333,
  "address": "Rua Exemplo, 123",
  "city": "São Paulo",
  "phone": "(11) 1234-5678",
  "website": "https://exemplo.com",
  "distance": 2500,
  "hasMaternityWard": false,
  "isEmergency": true,
  "acceptsSUS": true
}
```

### Mudanças Propostas
1. **Renomear:** `isMaternity` → `hasMaternityWard` (nome mais descritivo)
2. **Garantir:** Campo sempre presente (não nullable)
3. **Garantir:** Valor padrão `false` se ausente

---

## 🗄️ Schema de Banco de Dados

### Tabela: `hospitals` (Proposta)

#### Estrutura Atual (Referência - Se Existir)
```sql
CREATE TABLE IF NOT EXISTS hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    address TEXT,
    city TEXT,
    phone TEXT,
    website TEXT,
    isMaternity BOOLEAN,  -- ⚠️ Pode ser NULL
    isEmergency BOOLEAN,
    acceptsSUS BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Estrutura Proposta (Atualizada)
```sql
CREATE TABLE IF NOT EXISTS hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    address TEXT,
    city TEXT,
    phone TEXT,
    website TEXT,
    hasMaternityWard BOOLEAN NOT NULL DEFAULT false,  -- ✅ Não nullable, default false
    isEmergency BOOLEAN,
    acceptsSUS BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Migração (Script SQL)

#### Passo 1: Adicionar Nova Coluna (Se Não Existir)
```sql
-- Adiciona coluna hasMaternityWard se não existir
ALTER TABLE hospitals ADD COLUMN hasMaternityWard BOOLEAN DEFAULT false;
```

#### Passo 2: Migrar Dados (Converter NULL → false)
```sql
-- Converte todos os NULL para false (segurança)
UPDATE hospitals 
SET hasMaternityWard = false 
WHERE hasMaternityWard IS NULL;
```

#### Passo 3: Migrar Dados (Converter isMaternity → hasMaternityWard - Se Existir)
```sql
-- Se existir coluna isMaternity, migra para hasMaternityWard
UPDATE hospitals 
SET hasMaternityWard = COALESCE(isMaternity, false)
WHERE hasMaternityWard IS NULL OR hasMaternityWard = false;
```

#### Passo 4: Tornar Coluna NOT NULL (Se Suportado)
```sql
-- SQLite não suporta ALTER COLUMN, então usar recriação da tabela
-- Para PostgreSQL:
ALTER TABLE hospitals 
ALTER COLUMN hasMaternityWard SET NOT NULL,
ALTER COLUMN hasMaternityWard SET DEFAULT false;
```

#### Passo 5: Remover Coluna Antiga (Opcional - Se Existir)
```sql
-- Se existir coluna isMaternity antiga, remover após migração
ALTER TABLE hospitals DROP COLUMN isMaternity;
```

---

## 🔍 Algoritmo de Ordenação

### Pseudocódigo

```
FUNÇÃO ordenarHospitais(hospitais):
    ORDENAR hospitais POR:
        1. PRIORIDADE: hasMaternityWard DESC (true primeiro)
        2. DESEMPATE: distance ASC (mais próximo primeiro)
    
    RETORNAR hospitais ordenados
FIM
```

### Implementação JavaScript

```javascript
function ordenarHospitais(hospitais) {
    return hospitais.sort((a, b) => {
        // Prioridade 1: Hospitais com Ala Maternal primeiro
        if (a.hasMaternityWard && !b.hasMaternityWard) return -1;
        if (!a.hasMaternityWard && b.hasMaternityWard) return 1;
        
        // Prioridade 2: Entre mesmos tipos, ordena por distância (mais próximo primeiro)
        return a.distance - b.distance;
    });
}
```

### Implementação Python (Backend)

```python
def ordenar_hospitais(hospitais):
    """
    Ordena hospitais por prioridade:
    1. Hospitais com Ala Maternal primeiro (hasMaternityWard=True)
    2. Entre mesmos tipos, ordena por distância (mais próximo primeiro)
    """
    def chave_ordenacao(hospital):
        # Prioridade: True (1) > False (0) para hasMaternityWard
        # Distância: menor primeiro
        return (
            not hospital.get('hasMaternityWard', False),  # False primeiro (ordem inversa)
            hospital.get('distance', float('inf'))
        )
    
    return sorted(hospitais, key=chave_ordenacao)
```

### Exemplo de Ordenação

#### Entrada (Lista Não Ordenada)
```
Hospital A: hasMaternityWard=false, distance=2km
Hospital B: hasMaternityWard=true,  distance=5km
Hospital C: hasMaternityWard=false, distance=1km
Hospital D: hasMaternityWard=true,  distance=3km
```

#### Saída (Lista Ordenada)
```
1. Hospital D: hasMaternityWard=true,  distance=3km  ← Tem maternidade (mais próximo)
2. Hospital B: hasMaternityWard=true,  distance=5km  ← Tem maternidade (mais distante)
3. Hospital C: hasMaternityWard=false, distance=1km  ← Sem maternidade (mais próximo)
4. Hospital A: hasMaternityWard=false, distance=2km  ← Sem maternidade (mais distante)
```

---

## 🔧 Query de Busca (API Backend)

### Endpoint: `GET /api/hospitals?lat={lat}&lon={lon}&radius={radius}`

#### Resposta (JSON)
```json
{
  "hospitals": [
    {
      "id": 1,
      "name": "Hospital Exemplo",
      "lat": -23.5505,
      "lon": -46.6333,
      "address": "Rua Exemplo, 123",
      "city": "São Paulo",
      "phone": "(11) 1234-5678",
      "website": "https://exemplo.com",
      "distance": 2500,
      "hasMaternityWard": true,
      "isEmergency": true,
      "acceptsSUS": true
    }
  ],
  "total": 1,
  "radius": 50000
}
```

#### Validação (Pydantic - Python)
```python
from pydantic import BaseModel, Field
from typing import Optional

class HospitalResponse(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    distance: float
    hasMaternityWard: bool = Field(default=False)  # ✅ Sempre presente, default false
    isEmergency: bool = Field(default=False)
    acceptsSUS: bool = Field(default=False)
```

---

## 🛠️ Script de Sanitização

### Script SQL (Sanitização Completa)

```sql
-- Script de Sanitização: Converter NULL → false
-- Executar antes de implementar a feature

-- 1. Verificar quantos registros têm NULL
SELECT COUNT(*) as total_null
FROM hospitals
WHERE hasMaternityWard IS NULL;

-- 2. Converter todos NULL para false (por segurança)
UPDATE hospitals
SET hasMaternityWard = false
WHERE hasMaternityWard IS NULL;

-- 3. Verificar resultado
SELECT 
    hasMaternityWard,
    COUNT(*) as total
FROM hospitals
GROUP BY hasMaternityWard;

-- 4. (Opcional) Se existir coluna isMaternity antiga, migrar dados
-- UPDATE hospitals
-- SET hasMaternityWard = COALESCE(isMaternity, false)
-- WHERE hasMaternityWard IS NULL OR hasMaternityWard = false;
```

### Script Python (Sanitização)

```python
import sqlite3
from pathlib import Path

def sanitizar_dados_hospitais(db_path='backend/users.db'):
    """
    Sanitiza dados de hospitais: converte NULL → false para hasMaternityWard
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Verificar quantos registros têm NULL
    cursor.execute("SELECT COUNT(*) FROM hospitals WHERE hasMaternityWard IS NULL")
    total_null = cursor.fetchone()[0]
    print(f"Registros com NULL: {total_null}")
    
    # 2. Converter todos NULL para false (por segurança)
    cursor.execute("UPDATE hospitals SET hasMaternityWard = false WHERE hasMaternityWard IS NULL")
    conn.commit()
    
    # 3. Verificar resultado
    cursor.execute("SELECT hasMaternityWard, COUNT(*) FROM hospitals GROUP BY hasMaternityWard")
    resultados = cursor.fetchall()
    print("Distribuição após sanitização:")
    for valor, total in resultados:
        print(f"  hasMaternityWard={valor}: {total} registros")
    
    conn.close()
    print("✅ Sanitização concluída!")

if __name__ == '__main__':
    sanitizar_dados_hospitais()
```

---

## 🎯 Validação de Dados (Frontend)

### Validação JavaScript

```javascript
function validarHospital(hospital) {
    // Garantir que hasMaternityWard sempre seja boolean
    const hasMaternityWard = hospital.hasMaternityWard ?? false;
    
    // Garantir que nunca seja null/undefined na renderização
    return {
        ...hospital,
        hasMaternityWard: Boolean(hasMaternityWard)
    };
}

// Uso
const hospitaisValidados = hospitais.map(validarHospital);
```

---

## 📋 Checklist de Implementação

### Backend
- [ ] Adicionar coluna `hasMaternityWard` (BOOLEAN, default false)
- [ ] Executar script de sanitização (NULL → false)
- [ ] Atualizar query de busca para incluir `hasMaternityWard`
- [ ] Implementar algoritmo de ordenação
- [ ] Validar resposta da API (garantir boolean, nunca null)

### Frontend
- [ ] Atualizar interface para usar `hasMaternityWard` (renomear `isMaternity` se existir)
- [ ] Implementar validação: `hasMaternityWard ?? false`
- [ ] Implementar algoritmo de ordenação (fallback)
- [ ] Renderizar badge condicional (positivo/negativo)

### Testes
- [ ] Testar ordenação (hospitais com maternidade primeiro)
- [ ] Testar tratamento de NULL (converter para false)
- [ ] Testar query de busca (retornar sempre boolean)

---

## 📝 Notas para o Time

### Para @dev (Desenvolvedor)
- **Prioridade:** Implementar validação no frontend: `hasMaternityWard ?? false`
- **Prioridade:** Implementar algoritmo de ordenação antes da renderização
- **Backend:** Garantir que API sempre retorne boolean, nunca null

### Para @qa (QA)
- **Testar:** Ordenação funciona corretamente (hospitais com maternidade primeiro)
- **Testar:** Tratamento de NULL (converter para false)
- **Testar:** Query de busca retorna sempre boolean

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial da especificação de arquitetura | Architect (Winston) |
