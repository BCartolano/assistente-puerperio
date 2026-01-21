# Arquitetura: Integração com API CNES (Dados Abertos SUS)

**Arquiteto:** Winston  
**Contexto:** Automação de validação de serviços de hospitais  
**Objetivo:** Integrar com API de Dados Abertos do SUS (CNES) para validação automática de serviços

**Data:** {{date}}

---

## 🏗️ Visão Geral

### Problema
O sistema precisa validar automaticamente se hospitais possuem habilitação para 'Obstetrícia' ou 'Centro de Parto Normal' sem intervenção manual no banco de dados. Isso deve funcionar para qualquer cidade do Brasil.

### Solução Proposta
Integração com API de Dados Abertos do SUS (CNES - Cadastro Nacional de Estabelecimentos de Saúde) para consultar serviços habilitados de estabelecimentos de saúde.

---

## 📊 API CNES - Dados Abertos SUS

### Informações da API

#### Endpoint Base
- **URL Base:** `https://apidadosabertos.saude.gov.br/cnes/`
- **Documentação:** Disponível em dadosabertos.saude.gov.br
- **Formato:** JSON
- **Autenticação:** Geralmente não requerida (API pública)

#### Endpoints Principais

1. **Busca por CNES (Cadastro Nacional de Estabelecimentos de Saúde)**
   - `GET /cnes/estabelecimentos/{cnes}`
   - Retorna informações do estabelecimento, incluindo serviços habilitados

2. **Busca por Nome/Endereço**
   - `GET /cnes/estabelecimentos?nome={nome}&municipio={municipio}`
   - Retorna lista de estabelecimentos correspondentes

3. **Serviços Habilitados**
   - `GET /cnes/estabelecimentos/{cnes}/servicos`
   - Retorna lista de serviços habilitados do estabelecimento

### Serviços Relevantes para Maternidade

#### Códigos de Serviços (Referência)
- **Obstetrícia:** Código relacionado a serviços obstétricos
- **Centro de Parto Normal:** Serviço específico para partos normais
- **Atendimento Hospitalar:** Serviço geral de atendimento hospitalar

**Nota:** Consultar documentação oficial da API para códigos exatos de serviços.

---

## 🗄️ Estrutura de Dados

### Modelo de Resposta da API CNES (Exemplo)

```json
{
  "estabelecimento": {
    "cnes": "1234567",
    "nome": "Hospital Maternidade São Paulo",
    "municipio": "São Paulo",
    "uf": "SP",
    "endereco": {
      "logradouro": "Rua Exemplo, 123",
      "bairro": "Centro",
      "cep": "01000-000"
    },
    "servicos": [
      {
        "codigo": "02.01.01",
        "descricao": "Atendimento Hospitalar - Obstetricia",
        "situacao": "Ativo"
      },
      {
        "codigo": "02.01.02",
        "descricao": "Centro de Parto Normal",
        "situacao": "Ativo"
      }
    ]
  }
}
```

### Schema de Banco de Dados (Atualização Proposta)

#### Tabela: `hospitals` (Atualizada)

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
    hasMaternityWard BOOLEAN DEFAULT false,
    
    -- Novos campos para integração CNES
    cnes TEXT UNIQUE,  -- CNES do estabelecimento (se disponível)
    cnes_validated_at TIMESTAMP,  -- Data da última validação via CNES
    cnes_validation_status TEXT,  -- 'validated' | 'not_found' | 'error' | 'pending'
    
    isEmergency BOOLEAN,
    acceptsSUS BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para busca por CNES
CREATE INDEX IF NOT EXISTS idx_hospitals_cnes ON hospitals(cnes);
```

---

## 🔧 Arquitetura de Integração

### Fluxo de Validação

```
1. Hospital encontrado (Overpass API / Google Places)
   ↓
2. Tentar buscar CNES (por nome + cidade)
   ↓
3. Se CNES encontrado:
   → Consultar serviços habilitados via API CNES
   → Verificar se possui serviço de Obstetrícia/Parto Normal
   → Atualizar hasMaternityWard baseado no resultado
   ↓
4. Se CNES não encontrado:
   → Usar detecção automática (função detectarServicoMaternal)
   → hasMaternityWard = null (desconhecido) ou true (se detectado)
```

### Componentes

#### 1. Serviço de Busca CNES (Backend)

```python
# backend/services/cnes_service.py

import requests
from typing import Optional, Dict, List
from datetime import datetime

class CNESService:
    """
    Serviço para integração com API CNES (Dados Abertos SUS)
    """
    
    BASE_URL = "https://apidadosabertos.saude.gov.br/cnes"
    
    def buscar_por_nome(self, nome: str, municipio: str, uf: str = None) -> Optional[Dict]:
        """
        Busca estabelecimento por nome e município
        
        Args:
            nome: Nome do estabelecimento
            municipio: Nome do município
            uf: Sigla do estado (opcional)
            
        Returns:
            Dicionário com dados do estabelecimento ou None
        """
        try:
            params = {
                "nome": nome,
                "municipio": municipio
            }
            if uf:
                params["uf"] = uf
                
            response = requests.get(
                f"{self.BASE_URL}/estabelecimentos",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Retornar primeiro resultado (ou fazer matching mais sofisticado)
                if data.get("estabelecimentos") and len(data["estabelecimentos"]) > 0:
                    return data["estabelecimentos"][0]
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar CNES: {e}")
            return None
    
    def buscar_servicos(self, cnes: str) -> List[Dict]:
        """
        Busca serviços habilitados de um estabelecimento
        
        Args:
            cnes: CNES do estabelecimento
            
        Returns:
            Lista de serviços habilitados
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/estabelecimentos/{cnes}/servicos",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("servicos", [])
            
            return []
            
        except Exception as e:
            print(f"Erro ao buscar serviços CNES: {e}")
            return []
    
    def verificar_servico_maternal(self, cnes: str) -> bool:
        """
        Verifica se estabelecimento possui serviço de maternidade
        
        Args:
            cnes: CNES do estabelecimento
            
        Returns:
            True se possui serviço de maternidade, False caso contrário
        """
        servicos = self.buscar_servicos(cnes)
        
        # Palavras-chave para identificar serviços de maternidade
        keywords = [
            "obstetricia",
            "obstetrícia",
            "parto normal",
            "maternidade",
            "gestante"
        ]
        
        for servico in servicos:
            descricao = servico.get("descricao", "").lower()
            situacao = servico.get("situacao", "").lower()
            
            # Verificar se serviço está ativo e possui palavra-chave
            if situacao == "ativo":
                for keyword in keywords:
                    if keyword in descricao:
                        return True
        
        return False
    
    def validar_hospital(self, nome: str, municipio: str, uf: str = None) -> Dict:
        """
        Valida hospital completo: busca CNES e verifica serviços
        
        Args:
            nome: Nome do hospital
            municipio: Município
            uf: Sigla do estado
            
        Returns:
            Dicionário com resultado da validação
        """
        estabelecimento = self.buscar_por_nome(nome, municipio, uf)
        
        if not estabelecimento:
            return {
                "cnes": None,
                "hasMaternityWard": None,
                "status": "not_found",
                "confidence": "unknown"
            }
        
        cnes = estabelecimento.get("cnes")
        hasMaternityWard = self.verificar_servico_maternal(cnes)
        
        return {
            "cnes": cnes,
            "hasMaternityWard": hasMaternityWard,
            "status": "validated",
            "confidence": "high",
            "estabelecimento": estabelecimento
        }
```

#### 2. Endpoint de API (Backend)

```python
# backend/routes/hospitals.py

from flask import Blueprint, request, jsonify
from services.cnes_service import CNESService

hospitals_bp = Blueprint('hospitals', __name__)
cnes_service = CNESService()

@hospitals_bp.route('/api/hospitals/validate-cnes', methods=['POST'])
def validate_hospital_cnes():
    """
    Valida hospital via API CNES
    
    Request Body:
    {
        "name": "Nome do Hospital",
        "city": "São Paulo",
        "state": "SP"
    }
    
    Response:
    {
        "cnes": "1234567",
        "hasMaternityWard": true,
        "status": "validated",
        "confidence": "high"
    }
    """
    data = request.get_json()
    
    nome = data.get("name")
    cidade = data.get("city")
    estado = data.get("state")
    
    if not nome or not cidade:
        return jsonify({"error": "Nome e cidade são obrigatórios"}), 400
    
    resultado = cnes_service.validar_hospital(nome, cidade, estado)
    
    return jsonify(resultado), 200
```

#### 3. Integração Frontend (JavaScript)

```javascript
/**
 * Valida hospital via API CNES
 * @param {Object} hospital - Objeto do hospital
 * @returns {Promise<Object>} Resultado da validação
 */
async function validarHospitalCNES(hospital) {
    try {
        const response = await fetch('/api/hospitals/validate-cnes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: hospital.name,
                city: hospital.city,
                state: hospital.state
            })
        });
        
        if (!response.ok) {
            throw new Error('Erro ao validar hospital via CNES');
        }
        
        const resultado = await response.json();
        return resultado;
        
    } catch (error) {
        console.error('Erro ao validar hospital via CNES:', error);
        return {
            hasMaternityWard: null,
            status: 'error',
            confidence: 'unknown'
        };
    }
}

/**
 * Valida hospital com fallback: CNES → Detecção Automática
 * @param {Object} hospital - Objeto do hospital
 * @returns {Promise<Object>} Resultado da validação
 */
async function validarHospitalCompleto(hospital) {
    // 1. Tentar validação via CNES
    const resultadoCNES = await validarHospitalCNES(hospital);
    
    if (resultadoCNES.status === 'validated' && resultadoCNES.hasMaternityWard !== null) {
        // Validação via CNES bem-sucedida
        return resultadoCNES;
    }
    
    // 2. Fallback: Detecção automática
    const resultadoDetecao = detectarServicoMaternal(hospital);
    
    return {
        hasMaternityWard: resultadoDetecao.hasMaternityWard,
        status: 'detected',
        confidence: resultadoDetecao.confidence,
        source: 'automatic_detection'
    };
}
```

---

## 🔄 Fluxo de Integração Completo

### Exemplo de Uso

```javascript
// No código de busca de hospitais (searchHospitalsNearby)
async searchHospitalsNearby(lat, lon, radius = 50000) {
    // ... código existente de busca Overpass API ...
    
    // Para cada hospital encontrado
    for (const hospital of hospitals) {
        // Se hasMaternityWard não está definido, fazer validação
        if (hospital.hasMaternityWard === null || hospital.hasMaternityWard === undefined) {
            // Tentar validação via CNES primeiro
            const validacaoCNES = await validarHospitalCNES(hospital);
            
            if (validacaoCNES.status === 'validated') {
                // Usar resultado do CNES
                hospital.hasMaternityWard = validacaoCNES.hasMaternityWard;
                hospital.cnes = validacaoCNES.cnes;
                hospital.validationSource = 'cnes';
            } else {
                // Fallback: Detecção automática
                const resultadoDetecao = detectarServicoMaternal(hospital);
                hospital.hasMaternityWard = resultadoDetecao.hasMaternityWard;
                hospital.validationSource = 'automatic_detection';
            }
        }
    }
    
    // ... resto do código ...
}
```

---

## ⚠️ Considerações Importantes

### Limitações da API CNES
1. **Rate Limiting:** API pode ter limites de requisições
2. **Disponibilidade:** API pode estar temporariamente indisponível
3. **Matching de Nomes:** Nomes podem variar entre fontes (Overpass vs CNES)
4. **Cobertura:** Nem todos os hospitais podem estar cadastrados no CNES

### Estratégias de Fallback
1. **Cache:** Armazenar resultados de validação CNES para evitar requisições repetidas
2. **Detecção Automática:** Usar função `detectarServicoMaternal()` como fallback
3. **Timeout:** Implementar timeout para não bloquear a aplicação
4. **Assíncrono:** Processar validações em background quando possível

### Performance
- Validação via CNES pode ser lenta (requisições HTTP)
- Considerar processar validações em background
- Implementar cache para evitar requisições repetidas
- Usar detecção automática como fallback rápido

---

## 📋 Checklist de Implementação

### Backend
- [ ] Serviço CNES implementado (`CNESService`)
- [ ] Endpoint de validação criado (`/api/hospitals/validate-cnes`)
- [ ] Tratamento de erros implementado
- [ ] Cache de resultados implementado (opcional)
- [ ] Testes unitários criados

### Frontend
- [ ] Função `validarHospitalCNES()` implementada
- [ ] Função `validarHospitalCompleto()` implementada
- [ ] Integração com `searchHospitalsNearby()` implementada
- [ ] Tratamento de erros implementado
- [ ] Testes de integração executados

### Banco de Dados
- [ ] Campos CNES adicionados à tabela `hospitals`
- [ ] Índice criado para busca por CNES
- [ ] Script de migração criado

### Documentação
- [ ] Documentação da API CNES consultada
- [ ] Códigos de serviços mapeados
- [ ] Exemplos de uso documentados

---

## 📝 Notas para o Time

### Para @architect
- **Pesquisar:** Documentação oficial da API CNES
- **Validar:** Endpoints e formatos de resposta reais
- **Mapear:** Códigos de serviços relacionados a maternidade

### Para @dev
- **Implementar:** Serviço CNES no backend
- **Integrar:** Validação CNES no fluxo de busca de hospitais
- **Testar:** Funcionamento com diferentes hospitais/cidades

### Para @qa
- **Testar:** Validação via CNES funciona corretamente
- **Testar:** Fallback para detecção automática quando CNES falha
- **Testar:** Performance (timeout, rate limiting)

---

## 🔄 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| {{date}} | 1.0 | Criação inicial da especificação de integração CNES | Architect (Winston) |
