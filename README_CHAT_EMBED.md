# Sophia Chat Embed - Integração Completa

Este diretório contém 3 versões do widget de chat Sophia para integração em sites:

## 📁 Arquivos Disponíveis

### 1. `openai_chat_embed.html` 
Versão para integração com OpenAI Chat Web Embed (se disponível publicamente).

**Características:**
- Configurado para widget do OpenAI
- Todas as camadas de segurança implementadas
- Tema light e idioma pt-BR

### 2. `sophia_chat_embed_completo.html`
Versão completa e standalone do chat widget.

**Características:**
- Widget completo e funcional
- Interface moderna e responsiva
- Sistema de filtro de segurança robusto
- Pronto para integração com sua API

### 3. `snippet_chat_sophia.html`
Snippet simplificado para colar diretamente em qualquer página HTML.

**Características:**
- Código compacto e autocontido
- Pode ser colado antes de `</body>` em qualquer página
- Todas as funcionalidades de segurança incluídas

## ⚙️ Configurações Implementadas

✅ **Título:** "Sophia – Assistente para Mães"  
✅ **Tema:** light  
✅ **Idioma:** pt-BR  
✅ **Mensagem inicial acolhedora** explicando limitações  
✅ **Camadas de segurança:**
- ✅ Bloquear diagnósticos
- ✅ Bloquear sugestões de medicamentos
- ✅ Bloquear conselhos médicos específicos
- ✅ Bloquear prescrições
- ✅ Bloquear tratamentos específicos
- ✅ Sempre recomendar consultar profissional

## 🚀 Como Usar

### Opção 1: Snippet Simples (Recomendado)
1. Abra `snippet_chat_sophia.html`
2. Copie todo o conteúdo
3. Cole antes de `</body>` na sua página HTML
4. Pronto! O chat aparecerá no canto inferior direito

### Opção 2: Widget Completo
1. Use `sophia_chat_embed_completo.html` como base
2. Integre com sua API substituindo a função `getBotResponse()`
3. Personalize os estilos conforme necessário

### Opção 3: OpenAI Embed (Se disponível)
1. Use `openai_chat_embed.html` como referência
2. Adapte conforme a documentação oficial do OpenAI Chat Web Embed

## 🔒 Segurança

Todos os arquivos incluem:

1. **Filtro de Conteúdo Perigoso:**
   - Detecta padrões de diagnóstico
   - Bloqueia sugestões de medicamentos
   - Previne conselhos médicos específicos

2. **Avisos Automáticos:**
   - Adiciona aviso de segurança em todas as respostas
   - Mensagem de limitação médica na mensagem inicial

3. **Sistema de Bloqueio:**
   - Intercepta e bloqueia conteúdo perigoso
   - Substitui por mensagem de segurança apropriada

## 📱 Responsividade

Todos os widgets são totalmente responsivos:
- Desktop: Widget flutuante no canto inferior direito
- Mobile: Widget em tela cheia para melhor experiência

## 🔧 Personalização

Para integrar com sua API:

1. Localize a função `getBotResponse()` ou `processMessage()`
2. Substitua pela chamada à sua API
3. Mantenha o sistema de filtro de segurança ativo

Exemplo:
```javascript
async function getBotResponse(message) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });
    const data = await response.json();
    return SafetyFilter.addSafetyWarning(data.response);
}
```

## ⚠️ Importante

- Todos os widgets incluem avisos médicos obrigatórios
- O sistema de filtro de segurança deve permanecer ativo
- Sempre recomende consultar profissionais de saúde
- Nunca permita diagnósticos ou prescrições médicas

## 📝 Licença

Use livremente em seus projetos, mantendo os avisos de segurança.

