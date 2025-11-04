# 📥 Como Instalar o ngrok no Windows

## 🚀 Método 1: Download Direto (Mais Rápido - RECOMENDADO)

### Passo 1: Baixar o ngrok
1. Acesse: https://ngrok.com/download
2. Clique em **"Download for Windows"**
3. O arquivo `ngrok.zip` será baixado na sua pasta Downloads

### Passo 2: Extrair o ngrok
1. Vá para a pasta **Downloads** (`C:\Users\SeuUsuario\Downloads`)
2. Clique com o botão direito em `ngrok.zip` > **"Extrair Tudo..."**
3. Ou extraia para uma pasta de fácil acesso (ex: `C:\ngrok\`)

### Passo 3: Adicionar ao PATH (Opcional mas Recomendado)
Para usar o ngrok de qualquer lugar:

1. **Copie o arquivo `ngrok.exe`** para uma pasta fixa:
   - Crie uma pasta: `C:\ngrok\`
   - Cole o `ngrok.exe` lá

2. **Adicione ao PATH do Windows**:
   - Pressione `Win + R`
   - Digite: `sysdm.cpl` e pressione Enter
   - Vá na aba **"Avançado"**
   - Clique em **"Variáveis de Ambiente"**
   - Em **"Variáveis do sistema"**, encontre `Path` e clique em **"Editar"**
   - Clique em **"Novo"** e adicione: `C:\ngrok\`
   - Clique em **"OK"** em todas as janelas

3. **Reinicie o PowerShell** ou Terminal

### Passo 4: Verificar Instalação
Abra um novo PowerShell e digite:
```powershell
ngrok version
```

Se aparecer a versão, está funcionando! ✅

---

## 🎯 Método 2: Usar o Script Automático (Mais Fácil)

Se você não quiser adicionar ao PATH, você pode:

1. **Baixe o ngrok** como no Passo 1 e 2 acima
2. **Coloque o `ngrok.exe` na pasta do projeto** (`C:\Users\Cartolano\Documents\chatbot-puerperio\`)
3. **Use o script `iniciar-com-ngrok.bat`** que já criamos - ele vai funcionar automaticamente!

---

## ⚡ Uso Rápido

Depois de instalar, você pode:

### Opção A: Usar o Script Automático
```bash
# Clique duas vezes no arquivo:
iniciar-com-ngrok.bat
```

### Opção B: Usar Manualmente
1. Abra um PowerShell na pasta do projeto
2. Inicie o Flask:
   ```bash
   python start.py
   ```
3. Em **outro PowerShell**, execute:
   ```bash
   ngrok http 5000
   ```
4. O ngrok vai mostrar um link tipo: `https://abc123.ngrok.io`
5. **Copie esse link** e compartilhe com seu chefe! 🎉

---

## 🔐 Primeira Vez? Crie uma Conta (Opcional mas Gratuita)

1. Acesse: https://dashboard.ngrok.com/signup
2. Crie uma conta gratuita
3. No dashboard, copie seu **authtoken**
4. No PowerShell, execute:
   ```bash
   ngrok config add-authtoken SEU_TOKEN_AQUI
   ```

Isso remove o limite de tempo e melhora a conexão!

---

## ❓ Problemas Comuns

### "ngrok não é reconhecido como comando"
- Certifique-se de ter adicionado ao PATH ou coloque o `ngrok.exe` na pasta do projeto
- Reinicie o PowerShell após adicionar ao PATH

### "Porta 5000 já em uso"
- Verifique se o Flask está rodando
- Ou mude a porta no script: `ngrok http 8080` (e ajuste o Flask para porta 8080)

---

✅ **Pronto!** Depois de instalar, você pode usar o script `iniciar-com-ngrok.bat` para iniciar tudo automaticamente!
