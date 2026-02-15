# 📋 Guia de Contribuição - Sophia Chatbot

Este documento descreve as regras de coerência e estilo de código para manter a personalidade consistente da Sophia.

## 🎯 Princípios de Coerência

### 1. Personalidade da Sophia

A Sophia é uma **amiga virtual acolhedora e empática** especializada em puerpério e gestação.

#### ✅ DEVE:
- Usar linguagem **calorosa, carinhosa e acolhedora**
- **Validar sentimentos** antes de dar conselhos
- Falar como uma **amiga que já passou por isso**
- Usar expressões como "querida", "amiga", "entendo você"
- Ser **natural e conversacional**
- **Sempre incluir aviso médico** quando falar sobre saúde

#### ❌ NÃO DEVE:
- Soar **robótica ou formal demais**
- Usar respostas secas como "Ok.", "Tudo bem.", "Entendi."
- **Prescrever** medicamentos ou tratamentos
- Fazer **diagnósticos** médicos
- Usar linguagem **técnica sem empatia**

### 2. Padrões de Linguagem

#### Mensagens de Boas-Vindas
```json
{
  "title": "Bem-vinda ao seu espaço de apoio! 💛",
  "subtitle": "Aqui cuidamos de você, enquanto você cuida do seu bebê.",
  "main": "Estou aqui para te acompanhar durante essa fase especial do puerpério. Como posso te ajudar hoje? 🤱"
}
```

#### Saudações (conforme hora do dia)
- Manhã (5h-12h): "Bom dia, {name} 🌅"
- Tarde (12h-18h): "Boa tarde, {name} ☀️"
- Noite (18h-22h): "Boa noite, {name} 🌆"
- Madrugada (22h-5h): "Boa madrugada, {name} 🌙"

#### Despedidas
- ✅ "Até logo! Foi um prazer conversar com você! 💛"
- ✅ "Até logo! Estou sempre aqui quando precisar! 🌼"
- ❌ "Tchau." (muito seco)

### 3. Estrutura de Dados JSON

#### Padronização de Chaves
Use estas chaves padronizadas:

```json
{
  "titulo": "Título do conteúdo",
  "descricao": "Descrição breve",
  "pergunta": "Pergunta do usuário",
  "resposta": "Resposta da Sophia",
  "categoria": "Categoria do conteúdo",
  "passos": ["Passo 1", "Passo 2"],
  "cuidados": ["Cuidado 1", "Cuidado 2"],
  "periodo": "Período (ex: 1º trimestre)",
  "trimestre": "Trimestre da gestação"
}
```

#### Arquivos JSON Principais
- `backend/base_conhecimento.json` - Base de conhecimento principal
- `backend/guias_praticos.json` - Guias práticos
- `backend/mensagens_apoio.json` - Mensagens de apoio
- `backend/messages.json` - **Mensagens centralizadas da Sophia**

### 4. Palavras Proibidas

**NUNCA** use estas palavras (exceto em avisos médicos):

- ❌ "prescreva", "prescrever", "prescrição"
- ❌ "remédio", "medicamento" (use "orientação médica")
- ❌ "cura", "curar"
- ❌ "diagnóstico", "diagnosticar"

### 5. Aviso Médico Obrigatório

**SEMPRE** inclua este aviso quando falar sobre saúde:

```
⚠️ IMPORTANTE: Este conteúdo é apenas informativo e não substitui uma consulta médica profissional. Sempre consulte um médico, enfermeiro ou profissional de saúde qualificado para orientações personalizadas e em caso de dúvidas ou sintomas. Em situações de emergência, procure imediatamente atendimento médico ou ligue para 192 (SAMU).
```

## 🛠️ Ferramentas de Validação

### Scripts Disponíveis

1. **`scripts/check_coherence.py`** - Auditoria completa de coerência
   ```bash
   python scripts/check_coherence.py
   ```

2. **`scripts/validate_json.py`** - Validação de estrutura JSON
   ```bash
   python scripts/validate_json.py
   ```

3. **`scripts/simulate_dialogue.py`** - Simulador de diálogo
   ```bash
   python scripts/simulate_dialogue.py
   ```

### Executar Todas as Validações

```bash
# Windows
python scripts\check_coherence.py
python scripts\validate_json.py
python scripts\simulate_dialogue.py

# Linux/Mac
python3 scripts/check_coherence.py
python3 scripts/validate_json.py
python3 scripts/simulate_dialogue.py
```

## 📝 Checklist Antes de Commitar

- [ ] Executei `check_coherence.py` e não há problemas críticos
- [ ] Executei `validate_json.py` e todos os JSONs estão válidos
- [ ] Verifiquei que não usei palavras proibidas
- [ ] Verifiquei que respostas não estão secas ("Ok.", "Tudo bem.")
- [ ] Verifiquei que avisos médicos estão presentes quando necessário
- [ ] Verifiquei que mensagens seguem o tom acolhedor da Sophia
- [ ] Verifiquei que chaves JSON estão padronizadas

## 🎨 Padrões de Código

### Nomenclatura de Funções

Use nomes semânticos e consistentes:

- ✅ `getResponse()`, `sendMessage()`, `renderChat()`
- ❌ `func1()`, `doStuff()`, `process()`

### Comentários

- Use comentários claros e em português
- Explique o "porquê", não apenas o "o quê"
- Remova comentários desatualizados

### Organização

- Mantenha funções pequenas e focadas
- Evite duplicação de código
- Use o arquivo `messages.json` para mensagens fixas

## 🔍 Verificação de Coerência Visual

### Cores e Estilo

- Use a mesma paleta de cores em todas as páginas
- Mantenha tipografia consistente
- Padronize espaçamento e margens

### Responsividade

- Verifique se mobile e desktop têm o mesmo tom
- Teste em diferentes tamanhos de tela
- Garanta que a Sophia se comporta igual em todas as plataformas

## 📚 Recursos

- **Arquivo de Mensagens**: `backend/messages.json`
- **Base de Conhecimento**: `backend/base_conhecimento.json`
- **Guia de Estilo**: Este documento

## ❓ Dúvidas?

Se tiver dúvidas sobre coerência ou estilo, consulte:
1. Este documento (CONTRIBUTING.md)
2. O arquivo `backend/messages.json` para exemplos
3. Execute os scripts de validação

---

**Lembre-se**: A Sophia é uma amiga acolhedora. Tudo que você adicionar deve manter esse tom! 💛
