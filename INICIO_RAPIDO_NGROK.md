# 🚀 Início Rápido - Apenas NGROK

Guia rápido para usar o projeto **apenas com NGROK** (sem Railway/Render).

## ✅ Checklist Rápido

- [ ] NGROK instalado
- [ ] Arquivo `.env` criado
- [ ] Dependências instaladas
- [ ] Pronto para iniciar!

---

## 📥 Passo 1: Instalar NGROK (2 minutos)

1. **Baixe o NGROK:**
   - Acesse: https://ngrok.com/download
   - Clique em "Download for Windows"
   - O arquivo `ngrok.zip` será baixado

2. **Extraia e coloque na pasta:**
   - Extraia o `ngrok.zip`
   - Copie o `ngrok.exe` para: `C:\Users\Cartolano\Documents\chatbot-puerperio\`
   - Ou coloque em `C:\ngrok\` e adicione ao PATH

**Pronto!** ✅

---

## 📝 Passo 2: Verificar Arquivo .env (1 minuto)

O projeto procura o arquivo `.env` nesta ordem:
1. **Raiz do projeto** (prioridade - será usado primeiro) ✅
2. Pasta `backend` (só se não houver na raiz)

### Se você JÁ TEM .env:
- ✅ **Verifique se está na raiz** - será usado automaticamente
- ✅ **Verifique se tem `GEMINI_API_KEY`** configurada
- ✅ Se tiver na raiz E na backend, o da **raiz será usado**

### Se NÃO TEM .env:
1. **Na raiz do projeto**, crie um arquivo chamado `.env`

2. **Copie este conteúdo:**
   ```env
   GEMINI_API_KEY=sua_chave_gemini_aqui
   SECRET_KEY=693166ce48966b81757ce56c8c2043ed2ca7cf38f90fe7846de729aa7d8f169c
   FLASK_ENV=development
   PORT=5000
   ```

3. **Substitua** `sua_chave_gemini_aqui` pela sua chave real:
   - Obtenha em: https://makersuite.google.com/app/apikey

**Pronto!** ✅

---

## 📦 Passo 3: Instalar Dependências (2 minutos)

1. **Abra o PowerShell** na pasta do projeto

2. **Ative o ambiente virtual:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   Se der erro, use:
   ```powershell
   venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```powershell
   pip install -r requirements.txt
   ```

**Pronto!** ✅

---

## 🚀 Passo 4: Iniciar (30 segundos)

**Opção A: Script Automático (Mais Fácil)**
```powershell
.\iniciar-com-ngrok.bat
```

**Opção B: Manual**
```powershell
# Terminal 1 - Iniciar Flask
cd backend
python app.py

# Terminal 2 - Iniciar NGROK
ngrok http 5000
```

---

## 🌐 Passo 5: Acessar

Após iniciar, você verá algo como:

```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:5000
```

**Esse link funciona de QUALQUER LUGAR na internet!** 🎉

---

## 📱 Testar no Celular

1. Copie o link do NGROK (ex: `https://abc123.ngrok-free.app`)
2. Abra no navegador do celular
3. **Funciona mesmo fora de casa!** ✅

---

## ⚠️ Importante

- O link do NGROK **expira** após algumas horas
- Cada vez que reiniciar, o link pode mudar
- Para link fixo, precisa de conta paga no NGROK

---

## 🛑 Parar o Servidor

1. No terminal do NGROK: Pressione `Ctrl+C`
2. Feche a janela do Flask Server

---

## ❓ Problemas Comuns

### "ngrok não encontrado"
- Verifique se `ngrok.exe` está na pasta do projeto
- Ou adicione ao PATH do Windows

### "Porta 5000 já em uso"
- Feche outros programas usando a porta 5000
- Ou mude a porta no `.env` e no comando do NGROK

### "GEMINI_API_KEY não encontrado"
- Verifique se o arquivo `.env` existe
- Verifique se a chave está correta
- Sem espaços antes ou depois do `=`

---

## ✅ Pronto!

Agora você está usando **apenas NGROK**! 

Não precisa de Railway ou Render. Tudo roda localmente e o NGROK cria o túnel público para acesso de qualquer lugar! 🚀
