# Governança: Chat × Triagem

**Objetivo:** Evitar deriva quando alguém alterar o prompt ou o fluxo do chat.  
**Público:** Quem edita system_prompt, persona ou lógica de integração.

---

## ⚠️ PONTO CRÍTICO: Chat NUNCA recebe sintomas

O chat **nunca** deve receber a lista de sintomas para "analisar".  
Se receber, pode começar a interpretar. Use sempre `payload_para_chat()`.

```python
resultado = evaluate(sintomas_positivos)
payload = payload_para_chat(resultado)  # ← Apenas isso vai para o prompt
# payload = { "nivel", "conduta", "template_hint" }
```

O chat recebe **apenas**:
- `nivel`
- `conduta`
- `template_hint` (ou None)

---

## O que o Chat PODE fazer

| # | Ação | Exemplo |
|---|------|---------|
| 1 | Receber o payload via `payload_para_chat(resultado)` | Nunca o resultado completo de `evaluate()` |
| 2 | Usar `nivel` e `conduta` como fonte única de verdade | Passar para o prompt: titulo, descricao, acoes |
| 3 | Comunicar a orientação com empatia | "Entendo que isso é preocupante. Com base no que você relatou, recomenda-se..." |
| 4 | Parafrasear o texto da conduta (mantendo o sentido) | Trocar palavras, não o significado |
| 5 | Sugerir os botões da conduta | Ligar 192, Ver unidades próximas, etc. |
| 6 | Validar que o contexto de triagem está ativo | Só aplicar essas regras quando a conversa for sobre triagem de sintomas |

---

## O que o Chat NÃO PODE fazer

| # | Proibição | Motivo |
|---|-----------|--------|
| 1 | Reclassificar o risco | Ex.: "acho que é só cansaço" quando o motor disse crítico |
| 2 | Suavizar a conduta | Ex.: "talvez procure um médico" quando o motor disse "procure emergência" |
| 3 | Intensificar a conduta | Ex.: dizer "urgência" quando o motor disse monitoramento |
| 4 | Criar orientação paralela | Dar outra recomendação além da conduta do motor |
| 5 | Receber lista de sintomas (sintomas_avaliados, etc.) | Usar `payload_para_chat()` – chat nunca analisa sintomas |
| 6 | Interpretar sintomas por conta própria | O motor já decidiu; o chat só comunica |
| 7 | Ignorar o nível retornado | Usar outro critério para decidir o que mostrar |
| 8 | Adicionar diagnóstico ou prescrição | Nunca, em nenhum contexto |

---

## Checklist antes de alterar o prompt

Ao editar `system_prompt.md`, `persona.txt` ou lógica de integração triagem↔chat:

- [ ] O prompt recebe APENAS `payload_para_chat(resultado)` – nunca sintomas?
- [ ] O prompt proíbe explicitamente reclassificar, suavizar ou intensificar?
- [ ] O prompt instrui a comunicar com empatia sem alterar a orientação?
- [ ] Há exemplo de resposta correta e incorreta no prompt?

---

## Exemplo de instrução para o prompt

```
[CONTEXTO TRIAGEM]
O motor de triagem classificou esta situação como: {nivel}
Conduta: {conduta.titulo}. {conduta.descricao}
Ações sugeridas: {conduta.acoes}

SUA TAREFA: Comunicar essa orientação com empatia e acolhimento.
VOCÊ NÃO PODE: Reclassificar o risco, suavizar ou intensificar a conduta, 
dar outra orientação além da conduta, diagnosticar ou prescrever.
```

---

## Responsabilidade

- **Motor (engine.py):** Decide nível e conduta. Fonte única de verdade.
- **Escalation (escalation.py):** Mapeia nível + template_hint → texto e ações. Não conhece sintomas.
- **Chat (prompt/IA):** Comunicar com empatia. Não decide.

---

*Documento de governança. Consultar antes de alterar fluxo triagem↔chat.*
