# Especificação: Motor de Triagem e Escalonamento

**Referência:** BMAD_ORQUESTRACAO_REESTRUTURACAO.md  
**Status:** Proposta

---

## 1. Níveis de Escalonamento

| Código | Nome | Conduta |
|--------|------|---------|
| `critico` | Atenção imediata | 192 + procurar emergência agora |
| `alerta` | Avaliar em até 24h | UPA, posto ou consulta agendada |
| `monitoramento` | Observar e acompanhar | Orientar sinais de piora |

---

## 2. Estrutura de Dados (YAML)

```yaml
# sintomas_regras.yaml (proposta)
sintomas:
  - id: sangramento_excessivo
    titulo: "Sangramento excessivo"
    pergunta: "O sangramento está muito intenso (encharcando mais de 1 absorvente por hora)?"
    categoria: Hemorragia
    nivel_base: critico
    combinacoes_override: []  # opcional

  - id: cansaco_extremo
    titulo: "Cansaço extremo"
    pergunta: "Está se sentindo extremamente cansada, mesmo após descansar?"
    categoria: Normal
    nivel_base: monitoramento
    sinais_piora:
      - "Se surgir falta de ar, tontura forte ou desmaio, procure atendimento."

combinacoes:
  - sintomas: [sangramento_excessivo, febre_alta]
    nivel: critico
  - sintomas: [tristeza_intensa, pensamentos_preocupantes]
    nivel: critico  # Encaminhar CVV
```

---

## 3. Interface do Motor

```python
# decision_engine.evaluate(sintomas_positivos: List[str]) -> dict
{
    "nivel": "critico" | "alerta" | "monitoramento",
    "sintomas_avaliados": ["sangramento_excessivo", "febre_alta"],
    "regra_aplicada": "combinacao" | "individual",
    "conduta": {
        "tipo": "emergencia" | "atendimento_24h" | "monitorar",
        "texto": "...",
        "acoes": [{"tipo": "telefone", "numero": "192"}, {"tipo": "hospital"}]
    }
}
```

---

## 4. Mapeamento Sintoma → Nível (base)

| Sintoma (id) | Nível base |
|--------------|------------|
| dor_cabeca_forte, visao_embacada, dor_abdominal_intensa | critico |
| sangramento_excessivo, febre_alta, dificuldade_respirar | critico |
| dor_peito | critico |
| inchaco_face_maos, dor_perineal_intensa, secrecao_mal_cheiro | alerta |
| dor_mama_vermelha, tristeza_intensa | alerta |
| cansaco_extremo | monitoramento |

---

## 5. Templates de Resposta (exemplo)

```yaml
respostas:
  critico:
    titulo: "Procure atendimento de emergência"
    descricao: "Com base no que você relatou, recomenda-se avaliação médica imediata."
    acoes:
      - tipo: telefone
        numero: "192"
        texto: "Ligar SAMU (192)"
      - tipo: hospital
        texto: "Ver unidades próximas"
  alerta:
    titulo: "Recomenda-se avaliação em até 24 horas"
    descricao: "..."
  monitoramento:
    titulo: "Você pode observar em casa"
    descricao: "Se notar [sinais], procure avaliação."
    acoes: []
```

---

*Especificação para implementação pelo DEV em conformidade com BMAD-ORCHESTRATOR.*
