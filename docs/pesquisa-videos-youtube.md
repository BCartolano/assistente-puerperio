# Pesquisa de Vídeos do YouTube - Sophia Chatbot

**Analista:** Mary (Business Analyst)  
**Data:** 2025-01-08  
**Objetivo:** Pesquisar e fornecer IDs reais do YouTube para os 4 temas de vídeos

---

## 📋 INSTRUÇÕES PARA PESQUISA

### Critérios de Seleção
1. **Canais Confiáveis:** Priorizar canais de:
   - Instituições de saúde (hospitais, universidades)
   - Enfermeiras obstétricas certificadas
   - Psicólogas especializadas em saúde mental materna/perinatal
   - Consultoras em amamentação certificadas (IBCLC)
   - Organizações de saúde materna reconhecidas

2. **Qualidade do Conteúdo:**
   - Vídeos educativos e baseados em evidências
   - Linguagem clara e acolhedora
   - Duração: 5-15 minutos (ideal)
   - Áudio e vídeo de boa qualidade

3. **Verificação de Embedding:**
   - Verificar se o vídeo permite incorporação (embedding)
   - Alguns vídeos podem ter restrições de embedding
   - Testar o embed antes de incluir

---

## 🎥 VÍDEOS A PESQUISAR

### Vídeo 1: Cuidados Essenciais nos Primeiros Dias
**Tema:** Primeiros dias do puerpério - cuidados físicos e emocionais  
**Conteúdo esperado:**
- Recuperação física pós-parto
- Cuidados com episiotomia/cesárea
- Higiene pessoal
- Alimentação adequada
- Importância do descanso

**Canais sugeridos para pesquisa:**
- Canais de enfermagem obstétrica
- Hospitais com conteúdo educativo
- Universidades de medicina/enfermagem

**ID atual:** `VIDEO_ID_1` (substituir)  
**Descrição curta:** "Orientações essenciais sobre recuperação física, cuidados com a episiotomia/cesárea, higiene, alimentação e descanso nos primeiros dias após o parto."

---

### Vídeo 2: Amamentação nos Primeiros Dias
**Tema:** Início da amamentação e cuidados com o bebê  
**Conteúdo esperado:**
- Posicionamento correto para amamentar
- Pega adequada do bebê
- Sinais de fome do bebê
- Cuidados com as mamas
- Dificuldades comuns e soluções

**Canais sugeridos para pesquisa:**
- Consultoras em amamentação (IBCLC)
- Canais de enfermagem especializados
- Organizações de apoio à amamentação

**ID atual:** `VIDEO_ID_2` (substituir)  
**Descrição curta:** "Dicas práticas sobre posicionamento correto, pega adequada, sinais de fome e cuidados com as mamas para uma amamentação bem-sucedida."

---

### Vídeo 3: Saúde Mental Materna - Baby Blues
**Tema:** Saúde mental materna e baby blues  
**Conteúdo esperado:**
- Diferença entre baby blues e depressão pós-parto
- Sinais de alerta para buscar ajuda
- Estratégias de autocuidado emocional
- Normalização das emoções no puerpério
- Quando procurar ajuda profissional

**Canais sugeridos para pesquisa:**
- Psicólogas especializadas em saúde mental materna/perinatal
- Canais de psicologia perinatal
- Organizações de apoio à saúde mental materna

**ID atual:** `VIDEO_ID_3` (substituir)  
**Descrição curta:** "Entenda a diferença entre baby blues e depressão pós-parto, reconheça sinais de alerta e aprenda estratégias de autocuidado emocional."

---

### Vídeo 4: Rede de Apoio e Autocuidado
**Tema:** Importância da rede de apoio e autocuidado no puerpério  
**Conteúdo esperado:**
- Como pedir ajuda sem culpa
- Construir e fortalecer rede de apoio
- Importância do descanso e autocuidado
- Dividir responsabilidades
- Cuidar de si mesma não é egoísmo

**Canais sugeridos para pesquisa:**
- Canais de apoio materno
- Psicólogas especializadas em maternidade
- Organizações de apoio a mães

**ID atual:** `VIDEO_ID_4` (substituir)  
**Descrição curta:** "Aprenda a construir sua rede de apoio, pedir ajuda sem culpa e entender que cuidar de si mesma é essencial para cuidar do bebê."

---

## ✅ CHECKLIST DE VERIFICAÇÃO

Para cada vídeo encontrado, verificar:

- [ ] **ID do YouTube obtido** (extraído da URL: `youtube.com/watch?v=ID_AQUI`)
- [ ] **Canal é confiável** (instituição, profissional certificado, organização reconhecida)
- [ ] **Conteúdo é educativo e baseado em evidências**
- [ ] **Embedding permitido** (testar se o vídeo pode ser incorporado)
- [ ] **Duração adequada** (5-15 minutos ideal)
- [ ] **Qualidade de áudio/vídeo** (boa qualidade técnica)
- [ ] **Linguagem acolhedora** (não alarmista, mas informativa)
- [ ] **Descrição curta criada** (1 frase para tooltip/legenda)

---

## 📝 FORMATO DE ENTREGA

Para cada vídeo, fornecer:

```javascript
{
    id: 'ID_DO_YOUTUBE_AQUI',
    title: 'Título do Vídeo',
    description: 'Descrição curta (1 frase)',
    channel: 'Nome do Canal',
    duration: 'X minutos',
    embeddingAllowed: true/false,
    verified: true/false // Se foi testado
}
```

---

## 🔒 CONSIDERAÇÕES DE PRIVACIDADE

**Importante:** 
- O código JavaScript já está configurado para usar `youtube-nocookie.com` (modo de privacidade aprimorada)
- Isso impede que o YouTube armazene cookies até que o usuário interaja com o vídeo
- Mesmo assim, informar usuários sobre conteúdo externo pode ser necessário (verificar requisitos de privacidade)

---

## 📚 RECURSOS ÚTEIS PARA PESQUISA

### Canais Brasileiros Sugeridos:
- Ministério da Saúde (se tiver conteúdo sobre puerpério)
- Hospitais universitários com canais educativos
- Conselhos profissionais (COREN, CRP)
- Organizações de apoio à amamentação
- Canais de enfermeiras obstétricas certificadas

### Termos de Busca Sugeridos:
- "puerpério cuidados primeiros dias"
- "amamentação primeiros dias posicionamento"
- "baby blues depressão pós-parto diferença"
- "rede apoio puerpério autocuidado"
- "saúde mental materna puerpério"

---

**Status:** Aguardando pesquisa e IDs reais  
**Próximo passo:** Após obter IDs, atualizar `backend/static/js/sidebar-content.js` com os IDs reais
