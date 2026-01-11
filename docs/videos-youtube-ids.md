# IDs de Vídeos do YouTube - Sophia Chatbot

**Analista:** Mary (Business Analyst)  
**Data:** 2025-01-08  
**Status:** IDs de exemplo fornecidos - Requer validação manual de embedding

---

## ⚠️ IMPORTANTE - VALIDAÇÃO NECESSÁRIA

Os IDs abaixo são **exemplos** baseados em termos de busca comuns. **É necessário:**

1. Pesquisar manualmente no YouTube para encontrar vídeos reais
2. Verificar se cada vídeo permite embedding (reprodução fora do YouTube)
3. Confirmar que o conteúdo é adequado e acolhedor
4. Testar cada embed antes de usar em produção

---

## 📹 VÍDEOS SELECIONADOS

### Vídeo 1: Cuidados Essenciais nos Primeiros Dias

**ID sugerido:** `[REQUER PESQUISA MANUAL]`  
**Título sugerido:** "Primeiros Dias do Puerpério: Guia Completo de Cuidados"  
**Descrição curta:** "Orientações essenciais sobre recuperação física, cuidados com a episiotomia/cesárea, higiene, alimentação e descanso nos primeiros dias após o parto."

**Como encontrar:**
- Buscar no YouTube: "cuidados puerpério primeiros dias enfermagem"
- Buscar no YouTube: "pós-parto cuidados recuperação hospital"
- Verificar canais como: Hospitais universitários, Enfermeiras obstétricas

**Formato de URL:** `https://www.youtube.com/watch?v=ID_AQUI`

---

### Vídeo 2: Amamentação nos Primeiros Dias

**ID sugerido:** `[REQUER PESQUISA MANUAL]`  
**Título sugerido:** "Amamentação nos Primeiros Dias: Dicas Práticas e Acolhimento"  
**Descrição curta:** "Dicas práticas sobre posicionamento correto, pega adequada, sinais de fome e cuidados com as mamas para uma amamentação bem-sucedida."

**Como encontrar:**
- Buscar no YouTube: "amamentação primeiros dias posicionamento pega"
- Buscar no YouTube: "amamentação dicas enfermagem IBCLC"
- Verificar canais como: Consultoras IBCLC, Sociedade Brasileira de Pediatria

**Formato de URL:** `https://www.youtube.com/watch?v=ID_AQUI`

---

### Vídeo 3: Saúde Mental Materna - Baby Blues

**ID sugerido:** `[REQUER PESQUISA MANUAL]`  
**Título sugerido:** "Saúde Mental Materna: Entendendo o Baby Blues e Cuidando de Você"  
**Descrição curta:** "Entenda a diferença entre baby blues e depressão pós-parto, reconheça sinais de alerta e aprenda estratégias de autocuidado emocional."

**Como encontrar:**
- Buscar no YouTube: "baby blues depressão pós-parto diferença psicologia"
- Buscar no YouTube: "saúde mental materna puerpério psicologia perinatal"
- Verificar canais como: Psicólogas perinatais, CRP, Organizações de saúde mental

**Formato de URL:** `https://www.youtube.com/watch?v=ID_AQUI`

---

### Vídeo 4: Rede de Apoio e Autocuidado

**ID sugerido:** `[REQUER PESQUISA MANUAL]`  
**Título sugerido:** "Rede de Apoio no Puerpério: Você Não Precisa Fazer Tudo Sozinha"  
**Descrição curta:** "Aprenda a construir sua rede de apoio, pedir ajuda sem culpa e entender que cuidar de si mesma é essencial para cuidar do bebê."

**Como encontrar:**
- Buscar no YouTube: "rede apoio puerpério autocuidado mãe"
- Buscar no YouTube: "pedir ajuda puerpério rede apoio psicologia"
- Verificar canais como: Psicólogas maternas, Organizações de apoio

**Formato de URL:** `https://www.youtube.com/watch?v=ID_AQUI`

---

## 📋 INSTRUÇÕES PARA SUBSTITUIÇÃO

### Passo 1: Pesquisar Vídeos
1. Acesse YouTube.com
2. Use os termos de busca sugeridos acima
3. Filtre por "Canais verificados" quando disponível
4. Priorize vídeos recentes (últimos 2-3 anos)

### Passo 2: Extrair ID do Vídeo
1. Clique no vídeo selecionado
2. Copie a URL da barra de endereço
3. Extraia o ID que vem depois de `watch?v=`
   - Exemplo: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - ID seria: `dQw4w9WgXcQ`

### Passo 3: Verificar Embedding
1. No vídeo do YouTube, clique em "Compartilhar"
2. Clique em "Incorporar"
3. Se aparecer código HTML, o embedding está permitido
4. Se aparecer mensagem de restrição, escolha outro vídeo

### Passo 4: Atualizar JavaScript
1. Abra `backend/static/js/sidebar-content.js`
2. Localize o array `videos` (linha ~70)
3. Substitua `VIDEO_ID_1`, `VIDEO_ID_2`, etc. pelos IDs reais
4. Salve o arquivo

---

## ✅ CHECKLIST DE VALIDAÇÃO

Para cada vídeo, confirmar:

- [ ] ID extraído corretamente da URL
- [ ] Embedding permitido (testado no YouTube)
- [ ] Conteúdo apropriado e acolhedor
- [ ] Duração entre 5-15 minutos
- [ ] Canal confiável (instituição ou profissional certificado)
- [ ] Descrição curta revisada
- [ ] ID atualizado no JavaScript

---

**Próximo Passo:** Após obter IDs reais, atualizar `backend/static/js/sidebar-content.js`
