# Fluxo – Emergência Obstétrica

Descrição do fluxo para referência e para geração de diagrama (ex.: flows.png).

---

## Sequência

1. **Botão Emergência** – Usuária aciona “Emergência” ou equivalente na tela principal.
2. **Consentimento GPS** – Sistema pede permissão de localização.  
   - Se **negado:** toast “Ative o GPS para encontrar hospitais perto de você.” e oferta de fallback (CEP/cidade) se disponível.
3. **Sintomas graves?** – Se usuária indicar sangramento intenso, convulsão, dor intensa, desmaio ou ausência de movimentos do bebê → **192 no topo** e banner “Sintomas graves detectados. Ligue 192 (SAMU) agora.”
4. **Lista top 3** – Exibição dos 3 estabelecimentos mais relevantes (has_maternity > distância > SUS [se filtro] > telefone), com cards conforme `docs/ux/cards_spec.md`.
5. **Ações no card** – Ligar (tel) e Rotas (deep link); disclaimer sempre visível.

---

## Diagrama

Para gerar `flows.png`, usar esta ordem:

```
[Botão Emergência] → [Consentimento GPS] → [Sintomas graves?]
       ↓                      ↓                      ↓
   (sim)                 (negado → Toast)      (sim → 192 + Banner)
       ↓                      ↓                      ↓
   [Lista top 3] ←────────────┴──────────────────────┘
       ↓
   [Card 1: Ligar | Rotas]
   [Card 2: Ligar | Rotas]
   [Card 3: Ligar | Rotas]
   [Disclaimer 192 + CNES]
```

---

**Versão:** 1.0  
**Data:** 2025-02
