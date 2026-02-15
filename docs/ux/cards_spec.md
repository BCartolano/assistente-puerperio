# Especificação de Cards – Emergência Obstétrica

Especificação de card para lista “top 3” e detalhe de estabelecimento. Microcopy em pt-BR e requisitos de acessibilidade.

---

## 1. Estrutura do card

| Elemento | Conteúdo | Obrigatório |
|----------|----------|-------------|
| **Título** | Nome do estabelecimento (fantasy_name ou name) | Sim |
| **Subtítulo** | Esfera (Público/Privado/Filantrópico) • Atende SUS: Sim/Não/Desc. | Sim |
| **Selo** | “Ala de Maternidade” OU “Provável maternidade (ligue para confirmar)” OU “Não listado” | Sim |
| **Ações** | **Ligar** (tel formatado: `telefone_formatado`; link `tel:` usa `phone_e164`) | Se houver telefone |
| | **Rotas** (deep link para app de mapas) | Sempre |
| **Dados** | Endereço, distância/tempo estimado, lat/long (para rotas) | Conforme disponível |
| **Evidências** | GET /api/v1/establishments/{cnes_id}/evidence retorna has_maternity, score, evidence (tipo, código, fonte) | Para auditoria/admin |

---

## 2. Regras de exibição

- **Telefone ausente:** Exibir “Telefone não informado”; botão “Rotas” continua ativo.
- **Ala de Maternidade:**  
  - **Sim** = evidência CNES (leito/serviço/habilitação/tipo).  
  - **Provável** = score 0,4–0,59 + keyword no nome fantasia; texto: “Provável maternidade (ligue para confirmar)”.  
  - **Não listado** = caso contrário.
- **Convênios:** Sempre “Ligue para confirmar” (CNES não é fonte para rede credenciada).

---

## 3. Microcopy (pt-BR) – Aprovado PO

| Contexto | Texto |
|----------|--------|
| **Toast GPS desligado** | “Ative o GPS para encontrar hospitais perto de você.” |
| **Banner 192 (sintomas graves)** | “Sintomas graves detectados. Ligue 192 (SAMU) agora.” |
| **Disclaimer geral** | “Informações do CNES de <MM/AAAA>. Confirme convênios por telefone. Em emergência, ligue 192.” |
| **Botão Ligar** | “Ligar” |
| **Botão Rotas** | “Rotas” |
| **Telefone ausente** | “Telefone não informado” |
| **Selo maternidade Sim** | “Ala de Maternidade” |
| **Selo maternidade Provável** | “Provável maternidade (ligue para confirmar)” |
| **Selo maternidade Não** | “Não listado” |
| **Atende SUS** | “Atende SUS: Sim” / “Atende SUS: Não” / “Atende SUS: Desc.” |

---

## 4. Acessibilidade

- **Contraste:** Mínimo AA (WCAG 2.1); texto e fundo com razão ≥ 4,5:1 (texto normal).
- **Tamanho mínimo de fonte:** 16px para texto principal (evitar zoom em mobile).
- **Foco/teclado:** Todos os botões (Ligar, Rotas) focáveis e ativáveis por teclado; ordem de tabulação lógica.
- **Labels:** Botões com texto visível ou aria-label (ex.: “Ligar para [nome do hospital]”, “Abrir rotas até [nome]”).
- **Screen reader:** Selo “Ala de Maternidade” e subtítulo (esfera, SUS) anunciados de forma clara; evitar apenas ícones sem texto alternativo.

---

## 5. Fluxo (referência para flows.png)

1. Usuária aciona **botão Emergência**.
2. Sistema solicita **consentimento de localização (GPS)**. Se negado: toast “Ative o GPS para encontrar hospitais perto de você.” e opção CEP/endereço se aplicável.
3. **Sintomas graves?** (sangramento intenso, convulsão, dor intensa, desmaio, ausência de movimentos do bebê): se sim → **priorizar 192 no topo** e banner “Sintomas graves detectados. Ligue 192 (SAMU) agora.”
4. Exibir **lista top 3** com cards conforme esta especificação; disclaimer visível.
5. Ações: **Ligar** (se tel) e **Rotas** (deep link).

*(Diagrama flows.png pode ser criado a partir deste fluxo.)*

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** UX Expert (BMAD)
