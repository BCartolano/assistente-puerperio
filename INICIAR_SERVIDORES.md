# 🚀 Guia para Iniciar Servidores - Render e NGROK

## 📋 Status Atual

- ✅ **Flask Server**: Iniciado em background (porta 5000)
- ⚠️ **NGROK**: Não instalado (necessário instalar)
- ℹ️ **Render**: Configurado para deploy automático

---

## 🔵 NGROK (Túnel Público para Desenvolvimento)

### Status: ⚠️ **PRECISA INSTALAR**

O NGROK permite criar um túnel público para seu servidor local, permitindo acesso remoto.

### Instalação Rápida:

1. **Baixe o ngrok:**
   - Acesse: https://ngrok.com/download
   - Baixe a versão Windows
   - Extraia o `ngrok.exe`

2. **Coloque na pasta do projeto:**
   ```powershell
   # Copie o ngrok.exe para:
   C:\Users\Cartolano\Documents\chatbot-puerperio\ngrok.exe
   ```

3. **OU adicione ao PATH do sistema** (recomendado)

### Como Usar:

**Opção 1: Script Automático (Recomendado)**
```bash
# Após instalar o ngrok.exe na pasta do projeto:
iniciar-com-ngrok.bat
```

**Opção 2: Manual**
```powershell
# Terminal 1: Flask já está rodando

# Terminal 2: Inicie o ngrok
ngrok http 5000

# O ngrok vai mostrar um link como:
# Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

### Primeira Vez? Configure o Authtoken (Opcional mas Recomendado):

1. Crie conta gratuita: https://dashboard.ngrok.com/signup
2. Copie seu authtoken do dashboard
3. Execute:
   ```bash
   ngrok config add-authtoken SEU_TOKEN_AQUI
   ```

---

## 🌐 RENDER (Deploy na Nuvem)

### Status: ✅ **CONFIGURADO**

O Render está configurado para fazer deploy automático quando você faz push para o repositório Git conectado.

### Arquivos de Configuração:

- ✅ `render.yaml` - Configuração do serviço
- ✅ `Procfile` - Comando de inicialização
- ✅ `requirements.txt` - Dependências

### Como Fazer Deploy no Render:

**Opção 1: Deploy Automático (Recomendado)**
1. Conecte seu repositório Git ao Render
2. O Render fará deploy automaticamente a cada push
3. Acesse: https://dashboard.render.com

**Opção 2: Deploy Manual**
1. Acesse: https://dashboard.render.com
2. Clique em "New +" > "Web Service"
3. Conecte seu repositório Git
4. Render detectará automaticamente:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`

### Variáveis de Ambiente no Render:

Configure no dashboard do Render:
- `SECRET_KEY` - Chave secreta do Flask
- `OPENAI_API_KEY` - (Opcional) Chave da OpenAI
- `MAIL_*` - Configurações de email (opcional)

### Verificar Status do Deploy:

1. Acesse: https://dashboard.render.com
2. Vá em "Services" > "assistente-puerperio"
3. Veja os logs em tempo real

---

## 🔧 Comandos Úteis

### Verificar se Flask está rodando:
```powershell
netstat -ano | findstr :5000
```

### Parar o Flask:
```powershell
# Encontre o processo:
Get-Process python | Where-Object {$_.Path -like "*chatbot*"}

# Pare o processo:
Stop-Process -Id <ID_DO_PROCESSO>
```

### Iniciar Flask manualmente:
```powershell
cd C:\Users\Cartolano\Documents\chatbot-puerperio
python start.py
```

### Iniciar Flask com Gunicorn (produção):
```powershell
gunicorn wsgi:app
```

---

## 📝 Checklist

- [ ] NGROK instalado e configurado
- [ ] Flask rodando localmente (porta 5000)
- [ ] Repositório Git conectado ao Render
- [ ] Variáveis de ambiente configuradas no Render
- [ ] Deploy automático ativado no Render

---

## 🆘 Problemas Comuns

### "Porta 5000 já em uso"
```powershell
# Encontre o processo usando a porta:
netstat -ano | findstr :5000

# Pare o processo:
Stop-Process -Id <PID>
```

### "ngrok não encontrado"
- Verifique se `ngrok.exe` está na pasta do projeto
- OU adicione ao PATH do sistema
- Reinicie o terminal após adicionar ao PATH

### "Render não faz deploy"
- Verifique se o repositório está conectado
- Verifique os logs no dashboard do Render
- Verifique se `render.yaml` está no repositório

---

**Última atualização:** 2025-01-27
**Status do Flask:** ✅ Rodando em background
**Status do NGROK:** ⚠️ Precisa instalar
**Status do Render:** ✅ Configurado

