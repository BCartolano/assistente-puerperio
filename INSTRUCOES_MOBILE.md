# 📱 Como Acessar no Celular

## ✅ Passo a Passo

### 1. Certifique-se que o servidor está rodando
```bash
cd backend
python app.py
```

### 2. Verifique que está na mesma rede WiFi
- Seu computador e celular devem estar conectados na **MESMA rede WiFi**

### 3. Descubra o IP do seu computador
Quando iniciar o servidor, ele mostrará automaticamente o IP, por exemplo:
```
📱 Acesse no CELULAR (mesma rede WiFi):
   http://192.168.0.10:5000
```

### 4. No celular, abra o navegador e acesse:
```
http://192.168.0.10:5000
```
*(Substitua 192.168.0.10 pelo IP mostrado na tela do servidor)*

## 🔥 Se não funcionar - Verificar Firewall

### Windows:
1. Abra "Firewall do Windows Defender"
2. Clique em "Permitir um aplicativo pelo Firewall"
3. Clique em "Alterar configurações"
4. Procure "Python" e marque as opções "Privado" e "Público"
5. Se não encontrar, clique em "Permitir outro aplicativo" e adicione Python

### Ou desative temporariamente o firewall para testar:
1. Abra "Firewall do Windows Defender"
2. Clique em "Ativar ou desativar o Firewall do Windows Defender"
3. Desative temporariamente para testar

## ⚠️ Problemas Comuns

### ❌ "Não é possível acessar este site"
- Verifique se o servidor está rodando no computador
- Verifique se o IP está correto
- Verifique se estão na mesma rede WiFi

### ❌ "Erro ao fazer login"
- Certifique-se que está usando o mesmo email e senha do computador
- Tente limpar o cache do navegador do celular
- Verifique se o email foi verificado (use o script `verify_user.py`)

### ❌ Porta bloqueada
- Verifique o firewall do Windows
- Tente usar outra porta: `PORT=8080` no `.env`

## 🛠️ Scripts Úteis

### Verificar status de um usuário:
```bash
python backend/check_user.py seu_email@exemplo.com
```

### Verificar email manualmente:
```bash
python backend/verify_user.py
# Digite seu email quando pedir
```

