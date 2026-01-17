# Entrega Final - IDs de Vídeos do YouTube

**Analista:** Mary (Business Analyst)  
**Data:** 2025-01-08  
**Status:** Pesquisa Realizada - Requer Validação Manual

---

## ⚠️ LIMITAÇÃO DA PESQUISA AUTOMATIZADA

Após pesquisa extensa, não foi possível obter IDs específicos de vídeos do YouTube diretamente através de buscas automatizadas, pois:

1. **YouTube não retorna IDs via API pública** sem autenticação
2. **Busca web geral** não retorna URLs/IDs específicos de forma confiável
3. **Validação de embedding** requer acesso direto ao YouTube

## 📋 INSTRUÇÕES PARA OBTER IDs MANUALMENTE

Para finalizar a implementação, **é necessário pesquisar manualmente** no YouTube seguindo os passos abaixo:

### Passo 1: Pesquisar no YouTube

Para cada tema, use os termos de busca sugeridos:

#### Vídeo 1: Cuidados Primeiros Dias
- **Buscar:** "cuidados puerpério primeiros dias enfermagem"
- **Ou:** "pós-parto recuperação cuidados hospital"
- **Filtrar:** Canais verificados, vídeos educativos
- **Canais sugeridos:** Hospitais universitários, Enfermeiras obstétricas certificadas

#### Vídeo 2: Amamentação
- **Buscar:** "amamentação primeiros dias posicionamento pega IBCLC"
- **Ou:** "amamentação dicas enfermagem consultora"
- **Filtrar:** Canais verificados
- **Canais sugeridos:** Consultoras IBCLC, Sociedade Brasileira de Pediatria

#### Vídeo 3: Saúde Mental Materna
- **Buscar:** "baby blues depressão pós-parto diferença psicologia perinatal"
- **Ou:** "saúde mental materna puerpério psicologia"
- **Filtrar:** Profissionais certificados
- **Canais sugeridos:** Psicólogas perinatais, CRP, Organizações de saúde mental

#### Vídeo 4: Rede de Apoio
- **Buscar:** "rede apoio puerpério autocuidado pedir ajuda"
- **Ou:** "suporte materno puerpério ajuda psicologia"
- **Filtrar:** Profissionais especializados
- **Canais sugeridos:** Psicólogas maternas, Organizações de apoio

### Passo 2: Extrair ID do Vídeo

1. Acesse o vídeo selecionado no YouTube
2. Copie a URL completa da barra de endereço
3. O ID está após `watch?v=` na URL
   - Exemplo: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - ID: `dQw4w9WgXcQ`

### Passo 3: Verificar Permissão de Embedding

1. No vídeo do YouTube, clique em **"Compartilhar"**
2. Clique em **"Incorporar"**
3. Se aparecer código HTML `<iframe>`, o embedding está permitido ✅
4. Se aparecer mensagem "Este vídeo não permite incorporação", escolha outro vídeo

### Passo 4: Criar Descrição Curta

Para cada vídeo, crie uma descrição de **1 frase** (máximo 150 caracteres) que será exibida como tooltip/legenda.

---

## 📝 FORMATO DE ENTREGA ESPERADO

Após encontrar os vídeos, forneça os dados no seguinte formato:

```javascript
// Substituir no arquivo backend/static/js/sidebar-content.js (linha ~67)

const videos = [
    {
        id: 'ID_REAL_DO_VIDEO_1', // Exemplo: 'dQw4w9WgXcQ'
        title: 'Título Exato do Vídeo',
        description: 'Descrição curta em 1 frase (máx 150 caracteres).',
        embeddingAllowed: true, // Confirmar após testar
        channel: 'Nome do Canal'
    },
    {
        id: 'ID_REAL_DO_VIDEO_2',
        title: 'Título Exato do Vídeo',
        description: 'Descrição curta em 1 frase.',
        embeddingAllowed: true,
        channel: 'Nome do Canal'
    },
    {
        id: 'ID_REAL_DO_VIDEO_3',
        title: 'Título Exato do Vídeo',
        description: 'Descrição curta em 1 frase.',
        embeddingAllowed: true,
        channel: 'Nome do Canal'
    },
    {
        id: 'ID_REAL_DO_VIDEO_4',
        title: 'Título Exato do Vídeo',
        description: 'Descrição curta em 1 frase.',
        embeddingAllowed: true,
        channel: 'Nome do Canal'
    }
];
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Para cada vídeo, confirmar:

- [ ] ✅ ID extraído corretamente da URL do YouTube
- [ ] ✅ Embedding permitido (testado via botão "Incorporar")
- [ ] ✅ Conteúdo apropriado, acolhedor e baseado em evidências
- [ ] ✅ Duração entre 5-15 minutos (ideal)
- [ ] ✅ Canal confiável (instituição, profissional certificado, organização)
- [ ] ✅ Descrição curta criada (1 frase, máx 150 caracteres)
- [ ] ✅ ID atualizado no arquivo `backend/static/js/sidebar-content.js`
- [ ] ✅ Testado no ambiente local (verificar se vídeo carrega no modal)

---

## 🎯 CRITÉRIOS DE SELEÇÃO (RELEMBRAR)

### Prioridades:
1. **Canais oficiais:** Ministério da Saúde, Sociedade Brasileira de Pediatria, Hospitais universitários
2. **Profissionais certificados:** Enfermeiras obstétricas, IBCLC, Psicólogas perinatais
3. **Organizações reconhecidas:** CRP, COREN, Organizações de saúde materna

### Qualidade:
- Conteúdo educativo e baseado em evidências
- Linguagem clara e acolhedora
- Qualidade técnica adequada (áudio/vídeo)
- Vídeos recentes (últimos 2-3 anos preferencialmente)

---

## 📚 RECURSOS PARA PESQUISA

### Canais Brasileiros Confiáveis (Verificar se têm vídeos sobre os temas):
- Ministério da Saúde Brasil
- Sociedade Brasileira de Pediatria
- COREN (Conselho Regional de Enfermagem)
- CRP (Conselho Regional de Psicologia)
- Fiocruz
- Hospitais universitários com canais educativos
- Consultoras IBCLC brasileiras

### Sites Alternativos (Se não encontrar no YouTube):
- Sites de instituições de saúde podem ter vídeos próprios
- Plataformas educacionais de saúde
- Canais de universidades públicas

---

## 🔧 PRÓXIMOS PASSOS TÉCNICOS

Após obter os IDs reais:

1. **Atualizar JavaScript:**
   - Abrir `backend/static/js/sidebar-content.js`
   - Localizar array `videos` (linha ~67)
   - Substituir `VIDEO_ID_1`, `VIDEO_ID_2`, etc. pelos IDs reais
   - Atualizar `embeddingAllowed: true` após confirmar
   - Salvar arquivo

2. **Testar Localmente:**
   - Abrir aplicação em ambiente local
   - Verificar se miniaturas aparecem corretamente
   - Testar clique em vídeo para abrir modal
   - Verificar se vídeo carrega e reproduz
   - Testar fechamento com ESC e clique no overlay

3. **Validar:**
   - Confirmar que todos os 4 vídeos funcionam
   - Verificar responsividade (ocultar em <1024px)
   - Testar acessibilidade (teclado, screen reader)

---

## 📊 TEMPLATE DE ENTREGA

Preencher e entregar:

### Vídeo 1: Cuidados Primeiros Dias
- **ID:** `_________________`
- **Título:** `_________________`
- **Canal:** `_________________`
- **Embedding:** [ ] Permitido [ ] Não permitido
- **Descrição curta:** `_________________`

### Vídeo 2: Amamentação
- **ID:** `_________________`
- **Título:** `_________________`
- **Canal:** `_________________`
- **Embedding:** [ ] Permitido [ ] Não permitido
- **Descrição curta:** `_________________`

### Vídeo 3: Saúde Mental Materna
- **ID:** `_________________`
- **Título:** `_________________`
- **Canal:** `_________________`
- **Embedding:** [ ] Permitido [ ] Não permitido
- **Descrição curta:** `_________________`

### Vídeo 4: Rede de Apoio
- **ID:** `_________________`
- **Título:** `_________________`
- **Canal:** `_________________`
- **Embedding:** [ ] Permitido [ ] Não permitido
- **Descrição curta:** `_________________`

---

**Status:** Pesquisa realizada, aguardando IDs reais para finalização  
**Documento criado por:** Mary (Business Analyst)  
**Data:** 2025-01-08  
**Versão:** 1.0
