# BMAD-ORCHESTRATOR: Reestruturação Completa Sophia

**Documento de Orquestração**  
**Data:** 2025-02  
**Versão:** 1.0

---

## Sumário Executivo

Este documento consolida a análise dos 9 agentes BMAD para reestruturar o site Sophia, com foco em triagem, UX, arquitetura e responsabilidade jurídica. O sistema atual apresenta redundâncias, dispersão de regras e risco de alarmismo.

---

## 1. ANALYST — Estado Atual do Sistema

### 1.1 Mapeamento de Fluxos de Triagem

| Fluxo | Localização | Conduta Predominante | Observação |
|-------|-------------|----------------------|------------|
| Triagem física (sintomas) | `sintomas_puerperio.json` + `chat.js` | Crítico/Médio → Hospital | 12 sintomas, 1 baixo sem hospital |
| Triagem emocional (ansiedade) | `app.py` `detectar_triagem_ansiedade` | Leve→IA; Moderada/Alta→CVV | Não bloqueia fluxo em leve |
| Triagem isolamento (RF.EMO.010) | `RF_EMO_010_CODIGO_PLACEHOLDER.py` | Placeholder não integrado | Código órfão |
| Alerta de risco (suicídio/autoagressão) | `app.py` `alerta_risco` | CVV 188 + bloqueia resposta | Prioridade alta |
| Orientação via LLM | `system_prompt.md` + `persona.txt` | GRAVE/ALERTA/OK em texto | Sem motor determinístico |
| Quick Replies / Botões hospital | `chat.js` | Sempre "Ver Hospitais Próximos" | Aparece em muitos contextos |

### 1.2 Redundâncias Identificadas

1. **Todos os caminhos levam ao hospital em sintomas médios:** Exceto `tristeza_intensa` (CVV) e `cansaco_extremo` (monitorar), os sintomas médios sempre mostram botão "Ver Hospitais Próximos".
2. **Duplicação de regras:** Gravidade definida em `sintomas_puerperio.json`, `system_prompt.md` e `persona.txt` sem fonte única de verdade.
3. **Fluxos paralelos não integrados:** Triagem sintomas (modal) é separada do chat; a IA não sabe que o usuário já passou pela triagem.

### 1.3 Problemas Estruturais

- **Ausência de motor de decisão central:** Regras espalhadas em JSON, Python, prompts.
- **Sem combinação de sintomas:** Se usuária marca "sangramento" + "febre", não há escalonamento progressivo.
- **Frontend como fonte de conduta:** `sintomas_puerperio.json` define gravidade e ações; deveria ser camada de dados, não de decisão.
- **RF_EMO_010 (isolamento):** Código em arquivo separado, não integrado ao `chat_routes` ou `app.py`.

### 1.4 Riscos Jurídicos e de Usabilidade

| Risco | Severidade | Descrição |
|-------|------------|-----------|
| Alarmismo | Alta | Se a Sophia orienta hospital em excesso, usuárias podem ignorar alertas reais |
| Subestimação | Alta | Se a IA minimiza sintoma grave, pode atrasar atendimento |
| Diagnóstico implícito | Média | Frases como "isso pode ser mastite" podem ser interpretadas como diagnóstico |
| Prescrição | Média | Filtro `filtrar_recomendacoes_medicas` existe, mas LLM pode vazar |
| Responsabilidade difusa | Média | Regras em múltiplos arquivos dificultam auditoria |

---

## 2. ARCHITECT — Arquitetura Proposta

### 2.1 Modelo de Escalonamento Real

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    NÍVEIS DE TRIAGEM (3 NÍVEIS)                         │
├─────────────────────────────────────────────────────────────────────────┤
│ CRÍTICO          │ Emergência imediata │ Hospital/192 agora             │
│ ALERTA           │ Avaliação em 24h    │ UPA, posto ou consulta agendada │
│ MONITORAMENTO    │ Observação domiciliar│ Orientar sinais de piora       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Separação de Responsabilidades

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CAMADA 1: DADOS DOS SINTOMAS                                            │
│ backend/data/sintomas_regras.yaml (ou JSON)                              │
│ - id, titulo, pergunta, categoria                                        │
│ - NÃO contém conduta (conduta vem das regras)                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CAMADA 2: REGRAS DE DECISÃO                                             │
│ backend/triage/decision_engine.py                                        │
│ - Mapeamento sintoma → nível base (critico/alerta/monitoramento)         │
│ - Regras de combinação (ex: sangramento + febre = crítico)               │
│ - Critérios objetivos (ex: febre > 38°C = crítico)                       │
│ - NUNCA diagnostica; NUNCA prescreve                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CAMADA 3: RESPOSTA E CONDUTA                                             │
│ backend/triage/response_templates.py                                     │
│ - Por nível: texto, ações (hospital, telefone, monitorar)                │
│ - Linguagem padronizada, sem alarmismo desnecessário                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Critérios Objetivos de Escalonamento

| Nível | Critérios | Conduta |
|-------|-----------|---------|
| **Crítico** | Sangramento >1 abs/hora, febre >38°C, dor peito, falta de ar, visão alterada, pensamentos de autoagressão | 192 + hospital agora |
| **Alerta** | Febre 37.5–38°C, secreção fétida, mastite, inchaço face/mãos, tristeza intensa >2 sem | Atendimento em 24–48h |
| **Monitoramento** | Cansaço, desconforto leve, baby blues | Observar, orientar quando procurar |

### 2.4 Fluxo Revisado (Alto Nível)

```
Usuária descreve sintoma/conversa
        │
        ▼
┌───────────────────┐
│ Detecção de risco │ (keywords suicídio/autoagressão) → CVV 188
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Motor de decisão  │ (sintomas selecionados ou extraídos)
│ (isolado)         │ → Nível: Crítico | Alerta | Monitoramento
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Camada de resposta│ Texto + ações conforme nível
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ IA (quando usado) │ Acolhe + reforça orientação (não redefine conduta)
└───────────────────┘
```

---

## 3. UX-EXPERT — Melhorias de Linguagem e Visual

### 3.1 Ajustes de Linguagem

| Situação | Evitar | Preferir |
|----------|--------|----------|
| Crítico | "Vá ao Hospital AGORA" (excessivo) | "Procure atendimento de emergência imediatamente. Se não puder ir sozinha, ligue 192." |
| Alerta | "Procure atendimento médico" (vago) | "Recomenda-se avaliação médica nas próximas 24 horas." |
| Monitoramento | "Fique em casa" (pode parecer negligência) | "Você pode observar em casa. Se notar [sinais X], procure avaliação." |

### 3.2 Hierarquia Visual

- **Crítico:** Vermelho suave, ícone alerta, botão "Ligar 192" em destaque.
- **Alerta:** Amarelo/laranja, ícone atenção, botão "Ver unidades próximas" secundário.
- **Monitoramento:** Azul/verde suave, ícone informação, sem botão de emergência.

### 3.3 Níveis Compreensíveis para o Usuário

| Nível Técnico | Label para Usuária |
|---------------|--------------------|
| Crítico | "Atenção imediata" |
| Alerta | "Avaliar em até 24h" |
| Monitoramento | "Observar e acompanhar" |

---

## 4. DEV — Plano de Implementação Técnica

### 4.1 Remoção de Código Morto

- [ ] `RF_EMO_010_CODIGO_PLACEHOLDER.py`: integrar ou remover
- [ ] Duplicação de `detectar_triagem_ansiedade` se houver em múltiplos lugares
- [ ] Código não utilizado em `chat.js` relacionado a triagem antiga

### 4.2 Modularização

```
backend/
├── triage/
│   ├── __init__.py
│   ├── decision_engine.py   # Motor de decisão (regras puras)
│   ├── response_builder.py  # Monta texto + ações
│   ├── data/
│   │   └── sintomas_regras.yaml
│   └── integration.py       # Integra com chat (chamadas ao motor)
```

### 4.3 Sistema de Escalonamento por Múltiplos Sintomas

- Entrada: lista de sintomas (ids) + respostas (sim/não)
- Regras de combinação em YAML, ex.:
  ```yaml
  combinacoes:
    - sintomas: [sangramento_excessivo, febre_alta]
      nivel: critico
    - sintomas: [tristeza_intensa, pensamentos_negativos]
      nivel: critico  # Encaminhar CVV + avaliar urgência
  ```

### 4.4 Garantias

- Motor de decisão **nunca** emite diagnóstico.
- Motor **nunca** sugere medicamentos ou dosagens.
- Todas as condutas vêm de templates aprovados.

---

## 5. QA — Plano de Testes

### 5.1 Fluxos Isolados

| Teste | Entrada | Resultado Esperado |
|-------|---------|---------------------|
| Sintoma crítico único | sangramento_excessivo = sim | Crítico, 192 + hospital |
| Sintoma médio único | mastite = sim | Alerta, hospital 24h |
| Sintoma baixo único | cansaco_extremo = sim | Monitoramento, sem hospital |
| Resposta "não" | Qualquer sintoma = não | Sem conduta de emergência |

### 5.2 Combinação de Sintomas

| Teste | Entrada | Resultado Esperado |
|-------|---------|---------------------|
| Sangramento + Febre | ambos sim | Crítico |
| Cansaço + Tristeza | ambos sim | Alerta (não crítico) |

### 5.3 Validações Obrigatórias

- [ ] Nem todos os caminhos levam ao hospital.
- [ ] Conduta coerente com o nível (crítico ≠ alerta ≠ monitoramento).
- [ ] Mensagens de risco (suicídio) sempre acionam CVV.
- [ ] Nenhum texto contém diagnóstico ou prescrição.

---

## 6. PM — Prioridades de Implementação

| Prioridade | Item | Esforço | Dependência |
|------------|------|---------|-------------|
| P0 | Motor de decisão isolado + dados em YAML | M | — |
| P0 | Separar dados/regras/resposta | M | P0 |
| P1 | Integrar triagem sintomas com motor (backend) | M | P0 |
| P1 | Regras de combinação de sintomas | S | P0 |
| P2 | Ajustes de linguagem (UX) | S | P1 |
| P2 | Integrar RF_EMO.010 (isolamento) ou descartar | M | — |
| P3 | Hierarquia visual revisada | S | P2 |

---

## 7. PO — Alinhamento ao Propósito

### 7.1 Princípios Reforçados

- **Tecnologia assistiva:** Apoia a decisão, não substitui o julgamento médico.
- **Educação em saúde:** Informa sinais de alerta e quando procurar ajuda.
- **Não substituição médica:** Toda orientação reforça a necessidade de avaliação profissional quando aplicável.

### 7.2 Decisões de Produto

1. Triagem física e emocional devem convergir para o mesmo motor de decisão quando fizer sentido.
2. Nível Monitoramento deve ter conduta clara: "observar" + sinais de piora para procurar ajuda.
3. Mensagens de emergência (192, CVV) devem ser objetivas e não alarmistas.

---

## 8. SM — Execução e Entregas

### 8.1 Sprint 1 (Base)

- Criar `backend/triage/` com estrutura proposta.
- Migrar dados de `sintomas_puerperio.json` para YAML (dados + regras).
- Implementar `decision_engine.py` com mapeamento sintoma → nível.

### 8.2 Sprint 2 (Integração)

- Integrar motor com fluxo do chat (quando triagem sintomas for acionada).
- Implementar combinação de sintomas.
- Ajustar templates de resposta (linguagem UX).

### 8.3 Sprint 3 (Refino)

- Revisão visual dos níveis.
- Integração ou remoção de RF_EMO.010.
- Documentação final e checklist jurídico.

### 8.4 Validação Entre Agentes

- Architect valida estrutura antes de DEV codar.
- QA valida critérios antes de merge.
- PO valida textos de conduta.
- BMAD-MASTER valida coerência ao final de cada sprint.

---

## 9. BMAD-MASTER — Validação Global

### 9.1 Critérios de Sucesso

- [ ] **Seguro:** Nenhum caminho negligencia risco grave.
- [ ] **Escalável:** Novos sintomas/regras via configuração, sem alterar código.
- [ ] **Sustentável:** Código modular, documentado, testável.
- [ ] **Responsável:** Sem diagnóstico, sem prescrição, linguagem adequada.

### 9.2 Pontos Críticos Corrigidos

| Ponto | Antes | Depois |
|-------|-------|--------|
| Redundância hospital | Quase tudo → hospital | Apenas Crítico/Alerta quando aplicável |
| Regras dispersas | JSON + Python + prompt | Motor único + YAML |
| Alarmismo | "Vá AGORA" | "Procure atendimento imediatamente; se não puder, ligue 192" |
| Sem combinação | 1 sintoma = 1 conduta | Regras de combinação (ex: sangramento + febre) |
| RF_EMO.010 órfão | Código não usado | Integrado ou removido |

---

## 10. Entregas Consolidadas

### 10.1 Arquitetura Final Proposta

- Motor de decisão em `backend/triage/`
- Separação dados (YAML) | regras (decision_engine) | resposta (templates)
- Integração com chat via `triage.integration`

### 10.2 Fluxo Revisado

```
Usuária → [Risco vida?] → CVV/192
        → [Sintomas] → Motor → Nível → Resposta padronizada
        → [Conversa geral] → IA (reforça, não redefine conduta)
```

### 10.3 Lista de Melhorias Aplicadas

1. Motor de decisão isolado e testável
2. Dados e regras em arquivos de configuração
3. Níveis com condutas distintas (Crítico ≠ Alerta ≠ Monitoramento)
4. Regras de combinação de sintomas
5. Linguagem revisada (clara, segura, não alarmista)
6. Integração triagem física + backend

### 10.4 Pontos Críticos Corrigidos

- Redundância "tudo ao hospital" eliminada
- Responsabilidade jurídica clarificada (sem diagnóstico/prescrição)
- Código morto identificado (RF_EMO.010)
- Hierarquia de gravidade objetiva e auditável

---

**Regras obrigatórias mantidas:**

- Nunca diagnosticar
- Nunca prescrever
- Sempre orientar com base em segurança
- Cada nível com conduta diferente
- Sistema permitindo expansão futura

---

*Documento gerado pelo BMAD-ORCHESTRATOR.*
