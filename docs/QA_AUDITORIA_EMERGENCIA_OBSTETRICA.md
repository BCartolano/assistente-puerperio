# Auditoria QA – Localização de Emergência Obstétrica

**Autor:** QA (Auditor de Segurança em Saúde)  
**Cenário de validação:** "Uma gestante está com descolamento de placenta (emergência gravíssima) e usa o nosso site."

---

## 1. O filtro remove "Hospitais Dia" ou "Clínicas de Estética" que por erro de cadastro tenham leitos, mas não tenham cirurgião 24h?

**Requisito:** A exigência do **Serviço 125 (Urgência em Obstetrícia) + Classificação 001 (Atendimento de Urgência)** foi implementada de forma rigorosa?

**Validação:**

- **Requisitos lógicos (Analyst):** Estabelecimento **DEVE** possuir Serviço 125 e Classificação 001 em `rl_estab_serv_class`; caso contrário, é **descartado**, mesmo que tenha nome "Hospital".
- **Pipeline (Dev):** O script `maternity_whitelist_pipeline.py`:
  - Filtra `rl_estab_serv_class` com `CO_SERVICO == "125"` e `CO_CLASSIFICACAO == "001"`.
  - Obtém o conjunto `emergency_capable_ids`.
  - A **Regra de Ouro** exige a **intersecção** com estabelecimentos que tenham **leito obstétrico (01 ou 02)** com quantidade > 0.
- **Conclusão:** Sim. Hospitais Dia e clínicas de estética que não possuem o serviço 125/001 cadastrado **não** entram em `emergency_capable_ids` e portanto **não** entram no JSON final. O filtro é rigoroso desde que os CSVs do CNES estejam corretos (Serviço 125/001 realmente indica habilitação para urgência obstétrica).

**Recomendação:** Manter a regra e documentar no front que "apenas estabelecimentos com Atendimento de Urgência em Obstetrícia (CNES) são exibidos". Se no futuro houver fonte oficial de "cirurgião 24h", incluir como critério adicional.

---

## 2. O sistema diferencia corretamente um hospital "Particular" de um "Público"? (Risco: usuária SUS guiada para hospital 100% privado)

**Requisito:** Se a usuária SUS for guiada para um hospital 100% privado em emergência, ela pode ser barrada ou receber conta impagável. Verificar a tabela `tb_atendimento_prestado`.

**Validação:**

- **Requisitos lógicos (Analyst):** Flags `accepts_sus` e `private_only` definidas a partir de `tb_atendimento_prestado`.
- **Pipeline (Dev):** O script:
  - Carrega `tb_atendimento_prestado` e monta `atend_flags` por CNES: `accepts_sus`, `private_only`.
  - Inclui no GeoJSON `properties.accepts_sus` e `properties.private_only`.
- **Front (UX):** O `EmergencyObstetricCard` exibe:
  - Badge verde "Atende SUS" quando `accepts_sus === true`.
  - Badge "Privado – Verifique plano" quando `private_only === true`.
  - Assim a usuária SUS pode **evitar** clicar em estabelecimentos apenas privados quando estiver filtrando por SUS.

**Ponto crítico:** A **fonte da verdade** é a tabela `tb_atendimento_prestado`. O pipeline deve mapear corretamente o código/tipo de atendimento que indica SUS (ex.: código 1 ou valor "SUS"/"PÚBLICO"). Se o CSV usar nomenclatura diferente, o `get_atendimento_flags` precisa ser ajustado para não marcar `accepts_sus = false` em hospitais públicos.

**Recomendação:**
- Validar em ambiente de homologação com amostra de CNES conhecidos (público x privado) se `accepts_sus` e `private_only` batem com a realidade.
- No front, para busca "SUS", **filtrar** resultados com `private_only === true` (não exibir ou exibir com aviso forte) para reduzir risco de direcionar usuária SUS para hospital 100% privado.

---

## 3. O que acontece se o CNES estiver desatualizado? O sistema tem algum alerta para a usuária ligar antes?

**Requisito:** CNES pode estar desatualizado (estabelecimento fechado, mudou serviços, etc.). A usuária deve ser orientada a **confirmar por telefone**.

**Validação:**

- **Arquitetura (Architect):** Metadata do GeoJSON inclui `data_version` (mês/ano da base) e `disclaimer`: "Dados do Cadastro Nacional (CNES). Confirme atendimento telefonicamente."
- **Pipeline (Dev):** O GeoJSON gerado contém:
  - `metadata.data_version`
  - `metadata.disclaimer` com o texto acima.
- **Front (UX):** O `EmergencyObstetricCard` exibe, no rodapé do card, o texto: **"Dados do Cadastro Nacional (CNES). Confirme atendimento telefonicamente."** (`showDisclaimer = true` por padrão).

**Conclusão:** Sim. O sistema já possui:
1. Disclaimer em todo card: "Confirme atendimento telefonicamente."
2. Campo `data_version` disponível para o front exibir, por exemplo: "Dados de base CNES de [YYYY-MM]. Confirme por telefone antes de se deslocar."

**Recomendação:** Na tela de resultados (lista ou mapa), exibir uma vez o aviso: "Os dados vêm do Cadastro Nacional (CNES). Recomendamos ligar antes para confirmar atendimento e vagas." E manter o disclaimer em cada card.

---

## 4. Validação final: o JSON contém apenas locais com capacidade cirúrgica e de urgência comprovada nos dados?

**Critério:** Apenas estabelecimentos que:
- possuem **Serviço 125 + Classificação 001** (ou equivalente Urgência Neonatal), **e**
- possuem **leito obstétrico (01 ou 02)** com quantidade > 0, **e**
- possuem coordenadas válidas (dentro do Brasil, não zeradas)

devem constar no JSON final.

**Validação:**

- O pipeline aplica:
  1. `emergency_capable_ids` = filtro em `rl_estab_serv_class` (125 + 001).
  2. `ids_with_obstetric` = filtro em `rl_estab_leito` (cod_leito 01 ou 02, qt > 0).
  3. `whitelist_ids = emergency_capable_ids ∩ ids_with_obstetric`.
  4. Merge com `tb_estabelecimento`; descarte de registros sem coordenadas válidas.
- Nenhum estabelecimento entra no GeoJSON sem estar em `whitelist_ids` e sem passar na validação de coordenadas.

**Conclusão:** O JSON final contém **apenas** locais que, segundo os dados CNES carregados, têm **ambos**: habilitação de Atendimento de Urgência em Obstetrícia (125/001) **e** capacidade instalada de leito obstétrico. Isso atende ao objetivo de não mostrar hospitais sem capacidade comprovada nos dados.

---

## Resumo dos blocadores de deploy (conforme health_data_audit do QA)

| Cenário        | Status atual                                                                 | Ação |
|----------------|-------------------------------------------------------------------------------|------|
| Hospital Dia / Clínica com leito por erro | Bloqueado pelo filtro 125/001 + leito obstétrico                             | Manter e documentar |
| Falso SUS (particular como público)       | Depende do mapeamento em `tb_atendimento_prestado`; front exibe badges       | Validar mapeamento SUS em homologação; filtrar `private_only` na busca SUS |
| UPA indicada para parto                   | Bloqueado: só entram quem tem Serviço 125/001 **e** leito obstétrico         | Nenhuma alteração necessária |
| CNES desatualizado                       | Disclaimer em todo card + `data_version` disponível                           | Reforçar aviso na tela de resultados |

**Decisão:** As regras implementadas (Analyst → Architect → Dev → UX) atendem aos critérios de segurança para o cenário "gestante com descolamento de placenta". Recomenda-se validação em homologação dos flags SUS/privado com amostra real do CNES antes do deploy em produção.
