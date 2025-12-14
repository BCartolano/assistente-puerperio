# 📋 RF.EMO.010 - Plano de Implementação: Triagem de Isolamento e Sobrecarga

## 📊 Resumo Executivo

**Requisito Funcional:** RF.EMO.010  
**Nome:** Triagem para Sentimentos de Isolamento e Sobrecarga (Burnout Materno)  
**Status:** 📝 **PLANEJAMENTO**  
**Data:** 2025-01-27  
**Baseado em:** RF.EMO.009 (Mãe Ansiosa) - ✅ Implementado

---

## 🎯 Objetivo

Expandir o sistema de triagem emocional do chatbot "Sophia" para detectar e apoiar mães que apresentam sinais de isolamento social e sobrecarga emocional (burnout materno), complementando a triagem de ansiedade já implementada.

---

## 📐 Arquitetura da Solução

### Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│         SISTEMA DE TRIAGEM EMOCIONAL                    │
│              (BMad Core Integration)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐    ┌──────────────────┐         │
│  │ RF.EMO.009       │    │ RF.EMO.010       │         │
│  │ Mãe Ansiosa      │    │ Mãe Isolada/    │         │
│  │                  │    │ Sobrecarga      │         │
│  │ • Leve           │    │ • Leve          │         │
│  │ • Moderada       │    │ • Moderada      │         │
│  │ • Alta           │    │                 │         │
│  └──────────────────┘    └──────────────────┘         │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │  Função Genérica de Detecção                 │      │
│  │  detectar_triagem_emocional(perfil, mensagem)│      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │  Integração no Fluxo do Chatbot              │      │
│  │  1. Risco Suicídio (prioridade máxima)      │      │
│  │  2. RF.EMO.009 - Ansiedade                   │      │
│  │  3. RF.EMO.010 - Isolamento/Sobrecarga       │      │
│  │  4. Resposta Normal                          │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Tarefas de Implementação

### **TAREFA 1: Expandir Estrutura de Dados**

**Arquivo:** `dados/triagem_emocional.json`

**Ações:**
1. Adicionar novo perfil `"mae_isolada_sobrecarga"` ao objeto `perfis_emocionais`
2. Definir padrões de detecção:
   - **Palavras-chave (mínimo 10):**
     - Isolamento: "sozinha", "isolada", "ninguém me ajuda", "sem apoio", "abandonada"
     - Sobrecarga: "não aguento mais", "sobrecarregada", "exausta", "cansada demais", "esgotada"
     - Burnout: "não tenho forças", "sem energia", "desmotivada", "sem vontade"
   - **Frases completas (mínimo 5 por nível):**
     - Leve: "estou muito cansada", "ninguém me ajuda", "me sinto sozinha"
     - Moderada: "não aguento mais essa rotina", "estou completamente esgotada", "me sinto isolada de tudo"
3. Definir 2 níveis:
   - **Leve:** Sentimentos de dúvida/cansaço
   - **Moderada:** Exaustão/isolamento profundo
4. Criar respostas personalizadas para cada nível
5. Definir recursos de apoio específicos

**Estrutura Esperada:**
```json
{
  "perfis_emocionais": {
    "mae_ansiosa": { ... },  // Já existe
    "mae_isolada_sobrecarga": {
      "nome": "Mãe Isolada/Sobrecarga",
      "descricao": "...",
      "codigo": "RF.EMO.010",
      "padroes_deteccao": { ... },
      "niveis": {
        "leve": { ... },
        "moderada": { ... }
      },
      "recursos_apoio": { ... }
    }
  },
  "integracao_bmad": {
    "codigos_requisitos": ["RF.EMO.009", "RF.EMO.010"],
    "versao": "2.0.0"
  }
}
```

---

### **TAREFA 2: Refatorar Função de Detecção**

**Arquivo:** `backend/app.py`

**Ações:**
1. **Renomear função atual:**
   - `detectar_triagem_ansiedade()` → `detectar_triagem_emocional(perfil, mensagem, user_id)`
   
2. **Tornar função genérica:**
   - Aceitar parâmetro `perfil` ("mae_ansiosa" ou "mae_isolada_sobrecarga")
   - Buscar perfil dinamicamente em `TRIAGEM_EMOCIONAL["perfis_emocionais"][perfil]`
   - Adaptar lógica para diferentes estruturas de níveis (ansiedade tem 3 níveis, isolamento tem 2)

3. **Manter compatibilidade:**
   - Criar função wrapper `detectar_triagem_ansiedade()` que chama a genérica
   - Criar função `detectar_triagem_isolamento_sobrecarga()` que chama a genérica

**Código Placeholder:**
```python
def detectar_triagem_emocional(perfil_id, mensagem, user_id=None):
    """
    Função genérica de triagem emocional.
    Suporta múltiplos perfis emocionais (RF.EMO.009, RF.EMO.010, etc.)
    
    Args:
        perfil_id: ID do perfil ("mae_ansiosa", "mae_isolada_sobrecarga")
        mensagem: Texto da mensagem do usuário
        user_id: ID do usuário (opcional)
    
    Returns:
        {
            "detectado": True/False,
            "nivel": "leve"/"moderada"/"alta"/None,
            "perfil": perfil_id,
            "resposta": "...",
            "recursos": {...}
        }
    """
    # Implementação genérica aqui
    pass

def detectar_triagem_ansiedade(mensagem, user_id=None):
    """Wrapper para RF.EMO.009 - Mantém compatibilidade"""
    return detectar_triagem_emocional("mae_ansiosa", mensagem, user_id)

def detectar_triagem_isolamento_sobrecarga(mensagem, user_id=None):
    """RF.EMO.010 - Detecta isolamento e sobrecarga"""
    return detectar_triagem_emocional("mae_isolada_sobrecarga", mensagem, user_id)
```

---

### **TAREFA 3: Integrar no Fluxo do Chatbot**

**Arquivo:** `backend/app.py` - Método `chat()` da classe `ChatbotPuerperio`

**Localização:** Após detecção de ansiedade (RF.EMO.009), antes da resposta normal

**Código Placeholder:**
```python
# No método chat(), após RF.EMO.009:

# ========================================================================
# RF.EMO.010 - TRIAGEM EMOCIONAL: ISOLAMENTO E SOBRECARGA
# ========================================================================
logger.info(f"[TRIAGEM] Verificando triagem emocional - Isolamento/Sobrecarga")
triagem_isolamento = detectar_triagem_isolamento_sobrecarga(pergunta, user_id=user_id)

if triagem_isolamento.get("detectado"):
    nivel_isolamento = triagem_isolamento.get("nivel")
    resposta_triagem = triagem_isolamento.get("resposta", "")
    recursos = triagem_isolamento.get("recursos", {})
    
    logger.info(f"[TRIAGEM] ✅ Isolamento/Sobrecarga detectado - Nível: {nivel_isolamento}")
    
    # Adiciona recursos de apoio à resposta
    resposta_final = resposta_triagem
    if recursos.get("telefones"):
        telefones_texto = "\n\n**Recursos de Apoio:**\n"
        for telefone in recursos["telefones"]:
            telefones_texto += f"- **{telefone.get('nome', '')}**: {telefone.get('numero', '')}\n"
        resposta_final += telefones_texto
    
    # Nível moderado bloqueia resposta normal (prioridade alta)
    if nivel_isolamento == "moderada":
        return {
            "resposta": resposta_final,
            "fonte": "triagem_emocional",
            "alerta": True,
            "nivel": nivel_isolamento,
            "tipo": "isolamento_sobrecarga",
            "perfil": "mae_isolada_sobrecarga",
            "codigo_requisito": "RF.EMO.010"
        }
    elif nivel_isolamento == "leve":
        # Ansiedade leve: será combinada com resposta normal
        logger.info(f"[TRIAGEM] Isolamento leve detectado - será combinado com resposta normal")
```

---

### **TAREFA 4: Atualizar Rota API**

**Arquivo:** `backend/app.py` - Rota `/api/triagem-emocional`

**Ações:**
1. Adicionar suporte a parâmetro `perfil` (opcional)
2. Se não especificado, verifica todos os perfis disponíveis
3. Retornar código do requisito correspondente

**Código Placeholder:**
```python
@app.route('/api/triagem-emocional', methods=['POST'])
def api_triagem_emocional():
    """
    API de Triagem Emocional - Suporta múltiplos perfis
    RF.EMO.009 (Ansiedade) e RF.EMO.010 (Isolamento/Sobrecarga)
    """
    data = request.get_json()
    mensagem = data.get('mensagem', '')
    user_id = data.get('user_id', 'default')
    perfil = data.get('perfil', None)  # Novo: permite especificar perfil
    
    if not mensagem.strip():
        return jsonify({"erro": "Mensagem não pode estar vazia"}), 400
    
    logger.info(f"[TRIAGEM_API] Analisando mensagem - Perfil: {perfil or 'todos'}")
    
    # Se perfil especificado, verifica apenas esse
    if perfil:
        if perfil == "mae_ansiosa":
            resultado = detectar_triagem_ansiedade(mensagem, user_id)
            codigo = "RF.EMO.009"
        elif perfil == "mae_isolada_sobrecarga":
            resultado = detectar_triagem_isolamento_sobrecarga(mensagem, user_id)
            codigo = "RF.EMO.010"
        else:
            return jsonify({"erro": f"Perfil '{perfil}' não encontrado"}), 400
    else:
        # Verifica todos os perfis (prioridade: ansiedade > isolamento)
        resultado_ansiedade = detectar_triagem_ansiedade(mensagem, user_id)
        if resultado_ansiedade.get("detectado"):
            resultado = resultado_ansiedade
            codigo = "RF.EMO.009"
        else:
            resultado = detectar_triagem_isolamento_sobrecarga(mensagem, user_id)
            codigo = "RF.EMO.010" if resultado.get("detectado") else None
    
    return jsonify({
        "codigo_requisito": codigo,
        "integracao_bmad": True,
        **resultado
    })
```

---

## 📊 Estrutura de Dados Detalhada

### Perfil: Mãe Isolada/Sobrecarga

```json
{
  "mae_isolada_sobrecarga": {
    "nome": "Mãe Isolada/Sobrecarga",
    "descricao": "Perfil de mãe que apresenta sinais de isolamento social e sobrecarga emocional (burnout materno)",
    "codigo": "RF.EMO.010",
    "padroes_deteccao": {
      "palavras_chave": [
        // ISOLAMENTO (10+ palavras)
        "sozinha", "sozinho", "isolada", "isolado", "solitária", "solitário",
        "ninguém me ajuda", "ninguem me ajuda", "sem ajuda", "sem apoio",
        "abandonada", "abandonado", "esquecida", "esquecido",
        "não tenho ninguém", "nao tenho ninguem", "sem ninguém", "sem ninguem",
        "me sinto sozinha", "me sinto sozinho", "estou sozinha", "estou sozinho",
        "ninguém entende", "ninguem entende", "ninguém me entende",
        "sem rede de apoio", "sem suporte", "sem companhia",
        
        // SOBRECARGA (10+ palavras)
        "não aguento mais", "nao aguento mais", "não aguento", "nao aguento",
        "sobrecarregada", "sobrecarregado", "sobrecarga", "sobrecarregar",
        "exausta", "exausto", "exaustão", "exaustao", "esgotada", "esgotado",
        "cansada demais", "cansado demais", "muito cansada", "muito cansado",
        "sem forças", "sem forcas", "sem energia", "sem disposição",
        "desmotivada", "desmotivado", "sem motivação", "sem motivacao",
        "sem vontade", "sem ânimo", "sem animo", "sem esperança",
        "não tenho forças", "nao tenho forcas", "sem forças para",
        "burnout", "burn out", "esgotamento", "esgotamento mental",
        "não consigo mais", "nao consigo mais", "não consigo lidar",
        "muito trabalho", "muita responsabilidade", "tudo sozinha",
        "fazer tudo sozinha", "fazer tudo sozinho", "carregar tudo sozinha"
      ],
      "frases_completas": [
        // LEVE (5+ frases)
        "estou muito cansada",
        "ninguém me ajuda",
        "me sinto sozinha",
        "não tenho ninguém para ajudar",
        "estou sobrecarregada",
        "faço tudo sozinha",
        "me sinto isolada",
        "não tenho apoio",
        
        // MODERADA (5+ frases)
        "não aguento mais essa rotina",
        "estou completamente esgotada",
        "me sinto isolada de tudo",
        "não tenho forças para continuar",
        "estou em burnout",
        "não consigo mais lidar com tudo",
        "me sinto abandonada",
        "ninguém entende o que estou passando",
        "estou fazendo tudo sozinha e não aguento mais"
      ],
      "contextos": [
        "gestação", "gravidez", "grávida", "gestante",
        "parto", "pós-parto", "pos parto", "puerpério",
        "bebê", "recém-nascido", "neném", "filho", "filha",
        "maternidade", "mãe", "mamãe", "mamae",
        "cuidados", "cuidar", "rotina", "dia a dia",
        "casa", "trabalho", "família", "responsabilidades"
      ]
    },
    "niveis": {
      "leve": {
        "descricao": "Sentimentos de dúvida e cansaço - sobrecarga leve",
        "indicadores": [
          "cansaço frequente",
          "sentimentos de solidão ocasionais",
          "dificuldade em pedir ajuda",
          "sobrecarga de tarefas"
        ],
        "respostas": [
          "Entendo que você esteja se sentindo sobrecarregada. 💛 É muito comum sentir isso na maternidade, especialmente quando parece que tudo recai sobre você.\n\n**Você não está sozinha nessa.** Muitas mães passam por momentos parecidos.\n\n**Algumas sugestões que podem ajudar:**\n- Peça ajuda à família e amigos - você não precisa fazer tudo sozinha\n- Priorize o que é realmente essencial\n- Reserve alguns minutos para você, mesmo que sejam poucos\n- Converse com outras mães - grupos de apoio podem ajudar muito\n- Lembre-se: pedir ajuda não é fraqueza, é sabedoria\n\n**Se precisar de apoio emocional:**\n- **CVV (188)** - disponível 24 horas, gratuito e sigiloso\n- **Disque Saúde (136)** - orientação em saúde\n\nVocê está fazendo um trabalho incrível. 💛",
          "Percebo que você está se sentindo sobrecarregada e talvez um pouco isolada. 💛 Isso pode ser muito difícil.\n\n**É importante lembrar:** Você não precisa fazer tudo sozinha. Pedir ajuda é um ato de autocuidado.\n\n**Algumas ideias:**\n- Identifique pessoas que podem ajudar (família, amigos, vizinhos)\n- Aceite ajuda quando oferecida\n- Considere grupos de mães na sua região ou online\n- Reserve tempo para você, mesmo que sejam 10 minutos por dia\n- Não se culpe por não conseguir fazer tudo\n\n**Recursos de apoio:**\n- **CVV (188)** - 24 horas\n- **Disque Saúde (136)**\n\nVocê merece apoio e cuidado também. 💛"
        ]
      },
      "moderada": {
        "descricao": "Exaustão e isolamento profundo - burnout materno",
        "indicadores": [
          "exaustão física e emocional intensa",
          "isolamento social significativo",
          "sentimentos de desesperança",
          "dificuldade extrema em lidar com responsabilidades",
          "sintomas de burnout"
        ],
        "respostas": [
          "Vejo que você está passando por um momento muito difícil de exaustão e isolamento. 💛 Isso é sério e precisa de atenção.\n\n**Burnout materno é real e tratável.** Você não precisa enfrentar isso sozinha.\n\n**Por favor, busque ajuda:**\n- **Fale com seu médico ou vá ao posto de saúde** - eles podem te orientar\n- **Busque um psicólogo** - especialista em saúde mental materna\n- **Procure grupos de apoio** - outras mães podem entender o que você passa\n- **Peça ajuda prática** - família, amigos, ou serviços de apoio\n\n**Apoio imediato:**\n- **CVV (188)** - 24 horas, gratuito e sigiloso\n- **Disque Saúde (136)** - orientação\n- **SAMU (192)** - se for urgente\n\n**Lembre-se:**\n- Você não está sozinha\n- Muitas mães passam por isso\n- Há ajuda disponível\n- Buscar apoio é um ato de coragem\n\n**Por favor, não hesite em buscar ajuda profissional.** Sua saúde e bem-estar são fundamentais. 💛",
          "Percebo que você está em sofrimento profundo com exaustão e isolamento. 💛 Isso precisa de cuidado profissional.\n\n**Burnout materno pode ser tratado e você não precisa sofrer sozinha.**\n\n**Ações imediatas:**\n1. **Se for urgente:** SAMU 192 ou UPA mais próxima\n2. **Para acompanhamento:** Seu médico, posto de saúde ou psicólogo\n3. **Apoio emocional:** CVV (188) - 24 horas\n\n**Recursos de apoio:**\n- **CVV (188)** - apoio emocional 24h\n- **Disque Saúde (136)** - orientação\n- **Grupos de apoio materno** - busque na sua região\n- **Serviços de apoio domiciliar** - alguns municípios oferecem\n\n**Você não está sozinha.** Há pessoas e serviços prontos para te ajudar. Por favor, não hesite em buscar apoio. Você merece cuidado e suporte. 💛"
        ]
      }
    },
    "recursos_apoio": {
      "telefones": [
        {
          "nome": "CVV - Centro de Valorização da Vida",
          "numero": "188",
          "descricao": "Apoio emocional 24 horas, gratuito e sigiloso",
          "horario": "24 horas por dia"
        },
        {
          "nome": "Disque Saúde",
          "numero": "136",
          "descricao": "Orientação em saúde",
          "horario": "Segunda a Sexta, 8h às 18h"
        }
      ],
      "orientacoes": [
        "Pedir ajuda não é fraqueza - é autocuidado",
        "Grupos de mães podem oferecer apoio emocional e prático",
        "Reservar tempo para si mesma é essencial",
        "Dividir responsabilidades com parceiro/família pode aliviar sobrecarga",
        "Serviços de apoio domiciliar podem ajudar em tarefas práticas",
        "Terapia pode ajudar a lidar com sentimentos de isolamento",
        "Estabelecer limites é importante para evitar burnout"
      ]
    }
  }
}
```

---

## 🔄 Ordem de Prioridade no Fluxo

```
1. RISCO SUICÍDIO (prioridade máxima)
   ↓
2. RF.EMO.009 - ANSIEDADE
   ├─ Alta → Bloqueia resposta normal
   ├─ Moderada → Bloqueia resposta normal
   └─ Leve → Combina com resposta normal
   ↓
3. RF.EMO.010 - ISOLAMENTO/SOBRECARGA
   ├─ Moderada → Bloqueia resposta normal
   └─ Leve → Combina com resposta normal
   ↓
4. RESPOSTA NORMAL DO CHATBOT
```

---

## ✅ Checklist de Implementação

### Fase 1: Preparação
- [ ] Revisar estrutura atual do RF.EMO.009
- [ ] Criar backup do arquivo `triagem_emocional.json`
- [ ] Documentar padrões de detecção identificados

### Fase 2: Estrutura de Dados
- [ ] Adicionar perfil `mae_isolada_sobrecarga` ao JSON
- [ ] Definir palavras-chave (mínimo 20 total)
- [ ] Definir frases completas (mínimo 10 total)
- [ ] Criar respostas para nível leve (mínimo 2)
- [ ] Criar respostas para nível moderada (mínimo 2)
- [ ] Definir recursos de apoio
- [ ] Atualizar metadados de integração BMad

### Fase 3: Refatoração de Código
- [ ] Criar função genérica `detectar_triagem_emocional()`
- [ ] Refatorar `detectar_triagem_ansiedade()` como wrapper
- [ ] Criar função `detectar_triagem_isolamento_sobrecarga()`
- [ ] Testar compatibilidade com código existente

### Fase 4: Integração
- [ ] Adicionar chamada no método `chat()`
- [ ] Implementar lógica de prioridade
- [ ] Adicionar logs apropriados
- [ ] Atualizar rota API `/api/triagem-emocional`

### Fase 5: Testes
- [ ] Testar detecção nível leve
- [ ] Testar detecção nível moderada
- [ ] Testar integração no fluxo do chatbot
- [ ] Testar API dedicada
- [ ] Validar respostas e recursos

### Fase 6: Documentação
- [ ] Atualizar documentação RF.EMO.009
- [ ] Criar documentação RF.EMO.010
- [ ] Documentar exemplos de uso
- [ ] Criar guia de testes

---

## 📝 Notas de Implementação

### Considerações Importantes

1. **Compatibilidade:** Manter funções wrapper para não quebrar código existente
2. **Performance:** Função genérica deve ser eficiente (evitar loops desnecessários)
3. **Logs:** Adicionar logs detalhados para debugging
4. **Testes:** Testar ambos os perfis em conjunto e separadamente
5. **Documentação:** Atualizar README e documentação de API

### Pontos de Atenção

- ⚠️ Níveis diferentes: Ansiedade tem 3 níveis, Isolamento tem 2
- ⚠️ Prioridade: Ansiedade moderada/alta tem prioridade sobre Isolamento
- ⚠️ Contexto: Ambos verificam contexto de maternidade
- ⚠️ Recursos: Alguns recursos podem ser compartilhados (CVV, Disque Saúde)

---

## 🎯 Resultado Esperado

Após a implementação completa:

1. ✅ Sistema detecta isolamento e sobrecarga em mensagens
2. ✅ Classifica em níveis (leve/moderada)
3. ✅ Retorna respostas personalizadas e recursos de apoio
4. ✅ Integrado ao fluxo do chatbot com prioridade adequada
5. ✅ API atualizada para suportar múltiplos perfis
6. ✅ Código refatorado e genérico para futuras expansões

---

## 📚 Referências

- RF.EMO.009 - Implementação Completa (base)
- Documentação BMad Core
- Estrutura atual: `backend/app.py` linhas 1443-1604
- Arquivo de dados: `dados/triagem_emocional.json`

---

**Criado por:** BMad Orchestrator  
**Data:** 2025-01-27  
**Versão do Plano:** 1.0.0

