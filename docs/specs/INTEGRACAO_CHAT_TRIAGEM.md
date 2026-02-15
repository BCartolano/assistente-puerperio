# Integração Chat ↔ Motor de Triagem

**Princípio:** O chat **não** reclassifica, não suaviza, não interpreta em paralelo.  
Recebe o nível do motor → comunica com empatia. Nada além disso.

**Documento de governança (o que pode / o que não pode):**  
→ Ver [GOVERNANCA_CHAT_TRIAGEM.md](./GOVERNANCA_CHAT_TRIAGEM.md)

---

## Fluxo

```
Motor (engine.evaluate) → { nivel, conduta, versao_regra, timestamp }
                              ↓
Chat (prompt) recebe nivel + conduta → comunica com empatia
```

## Payload para o prompt

Use `payload_para_chat(resultado)`. O chat recebe **apenas**:

- `nivel`: critico | alerta | monitoramento
- `conduta.titulo`
- `conduta.descricao`
- `conduta.acoes`
- `template_hint`: ex. "saude_mental" ou None

**Nunca** passar `sintomas_avaliados` ou qualquer lista de sintomas ao chat.
