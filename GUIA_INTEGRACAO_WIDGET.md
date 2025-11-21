# Guia de Integração do Widget Sophia Chat

Este guia explica como usar o widget Sophia Chat no seu servidor Flask.

## ✅ Opção 1: Como Template (JÁ CONFIGURADO - RECOMENDADO)

### O que foi feito:
1. ✅ Arquivo copiado para `backend/templates/sophia_chat_embed.html`
2. ✅ Rota criada no Flask: `/chat-embed`

### Como usar:

**1. Acessar diretamente:**
```
http://localhost:5000/chat-embed
```
ou em produção:
```
https://seudominio.com/chat-embed
```

**2. Incorporar em outra página HTML:**
Você pode usar um iframe para incorporar o widget em qualquer página:

```html
<iframe 
    src="http://localhost:5000/chat-embed" 
    width="450" 
    height="600" 
    frameborder="0"
    style="position: fixed; bottom: 20px; right: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
</iframe>
```

**3. Incorporar em página do Flask:**
Adicione ao seu template (ex: `index.html`):

```html
<!-- Widget Sophia Chat -->
<iframe 
    src="{{ url_for('chat_embed') }}" 
    width="450" 
    height="600" 
    frameborder="0"
    style="position: fixed; bottom: 20px; right: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); z-index: 9999;">
</iframe>
```

---

## 📁 Opção 2: Como Arquivo Estático

Se preferir servir como arquivo estático (não recomendado para este caso, pois precisa de JavaScript dinâmico):

### Passos:

1. **Mover arquivo para pasta static:**
```bash
# No PowerShell (Windows)
Copy-Item sophia_chat_embed_completo.html backend\static\sophia_chat_embed.html
```

2. **Acessar diretamente:**
```
http://localhost:5000/static/sophia_chat_embed.html
```

⚠️ **Nota:** Esta opção não é recomendada porque o arquivo é um HTML completo e não funciona bem como arquivo estático sem processamento do Flask.

---

## 🔗 Opção 3: Incorporar em Página Existente

Você pode incorporar o widget diretamente na sua página principal (`index.html`):

### Passos:

1. **Abrir:** `backend/templates/index.html`

2. **Adicionar antes de `</body>`:**

```html
<!-- Widget Sophia Chat -->
<iframe 
    id="sophia-widget-iframe"
    src="{{ url_for('chat_embed') }}" 
    width="450" 
    height="600" 
    frameborder="0"
    style="position: fixed; bottom: 20px; right: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); z-index: 9999; display: none;">
</iframe>

<!-- Botão para mostrar/esconder widget -->
<button 
    id="toggle-sophia-widget" 
    style="position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; border-radius: 50%; background: #f4a6a6; color: white; border: none; cursor: pointer; z-index: 10000; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
    💛
</button>

<script>
    // Toggle widget
    const widgetBtn = document.getElementById('toggle-sophia-widget');
    const widgetIframe = document.getElementById('sophia-widget-iframe');
    
    widgetBtn.addEventListener('click', function() {
        if (widgetIframe.style.display === 'none') {
            widgetIframe.style.display = 'block';
            widgetBtn.style.display = 'none';
        } else {
            widgetIframe.style.display = 'none';
            widgetBtn.style.display = 'block';
        }
    });
</script>
```

---

## 🌐 Opção 4: Incorporar em Site Externo

Se você tem um site externo (não Flask) e quer incorporar o widget:

### 1. Certifique-se que o Flask está acessível publicamente
(use ngrok ou hospedagem em produção)

### 2. Adicione este código no seu site externo:

```html
<iframe 
    src="https://seudominio.com/chat-embed" 
    width="450" 
    height="600" 
    frameborder="0"
    style="position: fixed; bottom: 20px; right: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); z-index: 9999;">
</iframe>
```

**Importante:** O site externo precisa ter permissão CORS configurada no Flask (se necessário).

---

## 🎨 Personalização

### Ajustar tamanho do widget:

No código HTML do iframe, altere `width` e `height`:

```html
<iframe 
    src="{{ url_for('chat_embed') }}" 
    width="380"    <!-- Largura -->
    height="600"   <!-- Altura -->
    ...>
</iframe>
```

### Ajustar posição:

No `style`, altere `bottom` e `right`:

```html
style="position: fixed; bottom: 20px; right: 20px; ..."
```

Para mobile (canto inferior esquerdo):
```html
style="position: fixed; bottom: 20px; left: 20px; ..."
```

---

## ✅ Verificação

### Testar se está funcionando:

1. **Inicie o servidor Flask:**
```bash
cd backend
python app.py
```

2. **Acesse no navegador:**
```
http://localhost:5000/chat-embed
```

3. **Verifique:**
- ✅ Widget aparece corretamente
- ✅ Consegue enviar mensagens
- ✅ Recebe respostas da API
- ✅ Indicadores visuais funcionam

---

## 📝 Notas Importantes

1. **API Endpoint:** O widget já está configurado para usar `/api/chat` do Flask
2. **User ID:** O widget gera automaticamente um ID único por usuário (persistente)
3. **Segurança:** Todas as camadas de segurança já estão implementadas
4. **Responsivo:** O widget é responsivo e se adapta a mobile

---

## 🐛 Solução de Problemas

### Widget não aparece:
- Verifique se o arquivo está em `backend/templates/sophia_chat_embed.html`
- Verifique se a rota `/chat-embed` está funcionando

### API não responde:
- Verifique se o servidor Flask está rodando
- Verifique o console do navegador (F12) para erros
- Certifique-se que a rota `/api/chat` está funcionando

### CORS errors (em site externo):
Adicione no `app.py`:
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

---

## 📞 Suporte

Para mais informações, consulte:
- Arquivo principal: `sophia_chat_embed_completo.html`
- API endpoint: `backend/app.py` (linha 4341)
- Templates: `backend/templates/sophia_chat_embed.html`

