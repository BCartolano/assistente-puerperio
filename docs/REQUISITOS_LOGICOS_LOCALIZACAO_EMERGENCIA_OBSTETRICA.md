# Requisitos Lógicos – Localização de Emergência Obstétrica

**Autor:** Analyst (Regras de Negócio Críticas)  
**Objetivo:** Filtrar o banco CNES e identificar **apenas** estabelecimentos que garantam atendimento ao parto e emergência obstétrica.  
**Princípio:** Segurança do paciente acima da quantidade de resultados. *É melhor não mostrar um hospital do que mostrar um que não tem capacidade comprovada.*

---

## 1. Critério de Exclusão Absoluta

**Regra:** Se o estabelecimento **não** possuir o serviço de **"Atendimento de Urgência em Obstetrícia"** (Serviço **125**, Classificação **001** no CNES) **ou** "Atendimento de Urgência Neonatal", ele **DEVE** ser descartado, **mesmo que** tenha a palavra "Hospital" no nome.

- **Fonte:** Tabela `rl_estab_serv_class` (ou equivalente: serviços especializados e classificações).
- **Lógica If/Else:**
  - `IF` (Serviço = 125 AND Classificação = 001) **OR** (Serviço de Urgência Neonatal conforme código CNES)  
    `THEN` manter candidato.  
  - `ELSE` descartar — **não exibir**.
- **Motivo:** Hospitais Dia, clínicas de estética ou unidades sem habilitação formal podem ter leitos cadastrados por erro; a exigência 125/001 comprova habilitação para urgência obstétrica.

---

## 2. Critério de Capacidade Instalada

**Regra:** O estabelecimento deve ter registro **positivo** (quantidade > 0) na tabela de Leitos (`rl_estab_leito`) para:
- **Obstetrícia Clínica** (código **01**) **ou**
- **Obstetrícia Cirúrgica** (código **02**).

- **Fonte:** Tabela `rl_estab_leito` (colunas: identificador do estabelecimento, código do leito, quantidade existente).
- **Lógica If/Else:**
  - `IF` existe linha com `cod_leito` IN (01, 02) e `qt_existente` > 0  
    `THEN` possui capacidade instalada obstétrica.  
  - `ELSE` descartar — sem leito obstétrico não há garantia de atendimento ao parto.

---

## 3. Critério de Risco (Neonatal) – has_nicu

**Regra:** É **obrigatório** classificar o estabelecimento com a flag `has_nicu` (UTI Neonatal) **se** houver leitos do tipo:
- **10** (UTI Neonatal) **ou**
- **46** (Neonatologia).

- **Fonte:** Tabela `rl_estab_leito` (códigos de tipo de leito).
- **Lógica If/Else:**
  - `IF` existe registro com `cod_leito` IN (10, 46) e `qt_existente` > 0  
    `THEN` `has_nicu` = true.  
  - `ELSE` `has_nicu` = false.
- **Motivo:** Vital para mães de prematuros; o front deve destacar essa informação.

---

## 4. Critério Financeiro – accepts_sus e private_only

**Regra:** Definir flags claras a partir da tabela de atendimentos prestados (`tb_atendimento_prestado`):

- **`accepts_sus`** (atende Sistema Único de Saúde):  
  `IF` existe vínculo/atendimento SUS para o estabelecimento `THEN` true, `ELSE` false.

- **`private_only`** (apenas convênio/particular):  
  `IF` estabelecimento **não** consta com atendimento SUS e consta apenas como privado/convênio `THEN` true, `ELSE` false.

- **Motivo:** Evitar que usuária SUS seja direcionada a hospital 100% privado (risco de barreira ou cobrança indevida). Nunca afirmar aceitação de convênio específico (ex.: Unimed) sem API da operadora.

---

## 5. Regra de Ouro (Intersecção)

**O estabelecimento SÓ entra na lista final (White List) se:**

1. Está no conjunto dos que possuem **Serviço 125 + Classificação 001** (ou Urgência Neonatal), **e**
2. Está no conjunto dos que possuem **leitos obstétricos** (01 ou 02) com quantidade > 0.

**Lógica:**  
`WHITELIST_IDS = emergency_capable_ids ∩ establishment_ids_with_obstetric_beds`

Qualquer estabelecimento fora dessa intersecção deve ser **descartado** para a busca de emergência obstétrica/parto.

---

## 6. Geolocalização

- **Se** Lat/Long estiverem zerados ou inválidos (fora do Brasil):  
  **descartar** o registro **ou** marcar para revisão (não guiar usuária para local inválido).

---

## Resumo para o Architect

- **Exclusão absoluta:** Serviço 125 + Classificação 001 (ou Urgência Neonatal) obrigatório.
- **Capacidade:** Leitos 01 ou 02 com qt > 0 obrigatório.
- **Enriquecimento:** `has_nicu` (leitos 10 ou 46), `accepts_sus`, `private_only`.
- **Intersecção:** Só entra no JSON final quem satisfaz **ambos** (serviço de urgência **e** leitos obstétricos).
- **Geo:** Descartar ou sinalizar coordenadas zeradas/inválidas.
