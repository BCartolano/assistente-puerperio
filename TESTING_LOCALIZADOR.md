# 🧪 Guia de Testes - Localizador Puerperal

Este guia descreve como testar o Localizador Puerperal usando dados de seed para validação visual e funcional.

## 🎯 Objetivo

Validar a lógica visual (cores, badges, filtros) antes de usar dados reais do CNES, garantindo **100% de certeza** no funcionamento do sistema.

## 🚀 Setup Rápido

### 1. Popular Banco com Dados de Teste

```bash
# Executar script de seed
python backend/etl/seed_data.py
```

Este script cria 5 estabelecimentos simulados ao redor de São Paulo:
1. **Hospital das Clínicas** - SUS, Maternidade (AZUL)
2. **Maternidade Santa Joana** - Privado, Maternidade (VERDE)
3. **UPA 24h Vergueiro** - SUS, Emergência (AMARELO)
4. **UBS República** - SUS, Sem Maternidade (CINZA)
5. **Hospital Misto Modelo** - SUS, Maternidade (AZUL/Misto)

### 2. Iniciar Backend

```bash
# Terminal 1 - Backend
uvicorn backend.api.main:app --reload
```

Backend disponível em: http://localhost:5000

### 3. Iniciar Frontend

```bash
# Terminal 2 - Frontend
cd frontend
npm install  # Primeira vez
npm run dev
```

Frontend disponível em: http://localhost:3000

## 🧪 Testes de Validação (QA Scenarios)

### ✅ Teste 1: Cenário Feliz (Puerpério SUS)

**Ação:**
1. Abrir aplicação: http://localhost:3000
2. Permitir geolocalização (ou usar coordenadas de SP: -23.5505, -46.6333)
3. Filtrar: **"SUS"**
4. Marcar checkbox: **"Apenas Maternidades"**

**Resultado Esperado:**
- ✅ Deve aparecer apenas:
  - Hospital das Clínicas (AZUL)
  - Hospital Misto Modelo (AZUL/Misto)
- ❌ NÃO deve aparecer:
  - Maternidade Santa Joana (Privada)
  - UPA Vergueiro (Sem maternidade)
  - UBS República (Sem maternidade)

**Validação:**
- Cards devem ter cor AZUL (borda azul + fundo azul claro)
- Badges devem mostrar: "ACEITA SUS", "MATERNIDADE"

---

### ✅ Teste 2: Cenário Particular

**Ação:**
1. Mudar toggle para **"Privado/Convênio"**
2. Checkbox **"Apenas Maternidades"** mantido marcado

**Resultado Esperado:**
- ✅ Deve aparecer apenas:
  - Maternidade Santa Joana (VERDE)
- ❌ NÃO deve aparecer:
  - Hospitais SUS
  - UPA ou UBS

**Validação:**
- Card deve ter cor VERDE (borda verde + fundo verde claro)
- Badge deve mostrar: "MATERNIDADE", "PRIVADO"

---

### ✅ Teste 3: O Pesadelo (UPA)

**Ação:**
1. Desmarcar checkbox **"Apenas Maternidades"**
2. Filtrar: **"SUS"** ou **"Todos"**

**Resultado Esperado:**
- ✅ Deve aparecer:
  - UPA Vergueiro (AMARELO)
  - Outros hospitais SUS

**Validação Crítica (QA):**
- ✅ Card UPA deve ter cor AMARELO (borda amarela + fundo amarelo claro)
- ✅ Card UPA deve ter aviso VERMELHO:
  > "⚠️ Esta unidade não realiza partos, apenas estabilização. Em caso de emergência obstétrica, estabilização e transferência para hospital com maternidade."
- ✅ Badge deve mostrar: "EMERGÊNCIA APENAS", "NÃO REALIZA PARTO"

**Se o aviso não aparecer:** FALHA CRÍTICA - BLOQUEAR DEPLOY

---

### ✅ Teste 4: O Pânico (Botão de Emergência)

**Ação:**
1. Clicar no botão vermelho **"EMERGÊNCIA"** no header
2. Confirmar no modal
3. Observar resultados

**Resultado Esperado:**
- ✅ TODAS as unidades devem aparecer no mapa:
  - Hospital das Clínicas (SUS)
  - Maternidade Santa Joana (Privado)
  - UPA Vergueiro (Emergência)
  - Hospital Misto
- ✅ Banner vermelho deve aparecer: "MODO EMERGÊNCIA ATIVO"

**Validação Crítica (PM):**
- ✅ Filtros de convênio devem ser ignorados
- ✅ UPA deve aparecer (mesmo sem maternidade) pois serve para estabilização

**Por quê?** Em emergência, a distância importa mais que o convênio. A UPA serve para estabilizar a mãe antes de transferir.

---

## 🔍 Testes de Regressão (QA - Cenários de Pesadelo)

### ❌ Cenário 1: Duplicidade

**Teste:** Verificar se o mesmo hospital aparece duas vezes com nomes diferentes.

**Resultado Esperado:**
- ✅ Cada hospital aparece apenas UMA vez
- ✅ CNES ID é chave primária (evita duplicatas)

**Se falhar:** FALHA GRAVE - BLOQUEAR DEPLOY

---

### ❌ Cenário 2: Falso SUS

**Teste:** 
1. Filtrar por **"SUS"**
2. Verificar se algum hospital privado aparece

**Resultado Esperado:**
- ✅ Apenas hospitais com `is_sus = 1` devem aparecer
- ✅ Maternidade Santa Joana (Privada) NÃO deve aparecer no filtro SUS

**Se falhar:** ERRO CRÍTICO - RISCO DE PROCESSO - BLOQUEAR DEPLOY

---

### ❌ Cenário 3: UPA para Parto

**Teste:**
1. Filtrar por **"Apenas Maternidades"**
2. Verificar se UPA aparece

**Resultado Esperado:**
- ✅ UPA NÃO deve aparecer (não tem maternidade)
- ✅ `has_maternity = 0` para UPAs

**Se falhar:** ERRO DE LÓGICA - UPA não faz parto - BLOQUEAR DEPLOY

---

## 🐳 Testes com Docker (Opcional)

### Iniciar Tudo com Docker Compose

```bash
# Build e start todos os serviços
docker-compose up --build

# Em modo detached
docker-compose up -d --build
```

Serviços disponíveis:
- Backend: http://localhost:5000
- Frontend: http://localhost:3000

### Parar Serviços

```bash
docker-compose down
```

---

## 📊 Dados de Seed

Os dados de seed estão localizados em `backend/etl/seed_data.py` e incluem:

| CNES ID | Nome | Tipo | SUS | Maternidade | Cor |
|---------|------|------|-----|-------------|-----|
| 9990001 | Hospital das Clínicas | Hospital | ✅ | ✅ | 🔵 Azul |
| 9990002 | Maternidade Santa Joana | Hospital | ❌ | ✅ | 🟢 Verde |
| 9990003 | UPA 24h Vergueiro | UPA | ✅ | ❌ | 🟡 Amarelo |
| 9990004 | UBS República | UBS | ✅ | ❌ | ⚪ Cinza |
| 9990005 | Hospital Misto Modelo | Hospital | ✅ | ✅ | 🔵 Azul |

**Coordenadas Base:** -23.5505, -46.6333 (Centro de São Paulo)

---

## ✅ Checklist de Validação

Antes de considerar o sistema pronto para produção:

- [ ] Teste 1 passa (SUS + Maternidade)
- [ ] Teste 2 passa (Privado)
- [ ] Teste 3 passa (UPA com aviso)
- [ ] Teste 4 passa (Emergência ignora filtros)
- [ ] Cenário Duplicidade: Sem duplicatas
- [ ] Cenário Falso SUS: Privados não aparecem em SUS
- [ ] Cenário UPA: UPA não aparece em "Apenas Maternidade"
- [ ] Cores corretas em todos os cards
- [ ] Badges corretos baseados em tags
- [ ] Aviso legal sempre visível
- [ ] Botão "Navegar" abre Google Maps
- [ ] Mapas carregam corretamente
- [ ] Mobile responsivo

---

## 🚨 Troubleshooting

### Banco vazio após seed

```bash
# Verificar se banco foi criado
ls -la backend/cnes_cache.db

# Re-executar seed
python backend/etl/seed_data.py
```

### Erro de conexão com API

```bash
# Verificar se backend está rodando
curl http://localhost:5000/api/v1/facilities/health

# Verificar logs do backend
```

### Mapas não carregam

- Verificar conexão com internet (Leaflet usa OpenStreetMap)
- Verificar console do navegador para erros

---

**Desenvolvido seguindo diretrizes de Health Data Audit**  
**Safety by Design - Segurança pelo Design**
