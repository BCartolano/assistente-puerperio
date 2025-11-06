# 📧 Guia de Configuração de Email para Validação de Contas

## 🔍 Problema Identificado

Os novos usuários não estão recebendo emails de validação porque **as credenciais de email não estão configuradas** no arquivo `.env`.

## ✅ Solução: Configurar Email

### Passo 1: Criar arquivo `.env`

Na raiz do projeto, crie um arquivo chamado `.env` (se ainda não existir).

### Passo 2: Escolher Provedor de Email

Você tem 3 opções principais:

---

## 📮 OPÇÃO 1: Gmail (Recomendado)

### Requisitos:
- Conta Gmail
- Verificação em Duas Etapas ativada
- Senha de App gerada

### Configuração:

1. **Ative a Verificação em Duas Etapas:**
   - Acesse: https://myaccount.google.com/security
   - Ative "Verificação em duas etapas"

2. **Gere uma Senha de App:**
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "App" → "Mail" → "Outro (Nome personalizado)"
   - Digite: "Chatbot Puerpério"
   - Clique em "Gerar"
   - **Copie a senha de 16 caracteres** (sem espaços)

3. **Configure no `.env`:**
   ```env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=seu_email@gmail.com
   MAIL_PASSWORD=suasenhaapp16caracteres
   MAIL_DEFAULT_SENDER=seu_email@gmail.com
   ```

---

## 📮 OPÇÃO 2: Outlook/Hotmail (Mais Simples)

### Requisitos:
- Conta Outlook/Hotmail
- Senha normal (não precisa de Senha de App)

### Configuração:

1. **Configure no `.env`:**
   ```env
   MAIL_SERVER=smtp-mail.outlook.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=seu_email@outlook.com
   MAIL_PASSWORD=sua_senha_normal
   MAIL_DEFAULT_SENDER=seu_email@outlook.com
   ```

---

## 📮 OPÇÃO 3: Yahoo Mail

### Requisitos:
- Conta Yahoo
- Senha normal ou Senha de App (recomendado)

### Configuração:

1. **Configure no `.env`:**
   ```env
   MAIL_SERVER=smtp.mail.yahoo.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=seu_email@yahoo.com
   MAIL_PASSWORD=sua_senha
   MAIL_DEFAULT_SENDER=seu_email@yahoo.com
   ```

---

## 📝 Exemplo Completo do Arquivo `.env`

```env
# Configurações do Chatbot Puerpério
OPENAI_API_KEY=your_openai_api_key_here

# Configurações do Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=sua-chave-secreta-super-segura-mude-isso-em-producao

# Porta do servidor
PORT=5000

# URL base do aplicativo (para links de email)
BASE_URL=http://localhost:5000

# Configurações de Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=suasenhaapp16caracteres
MAIL_DEFAULT_SENDER=seu_email@gmail.com
```

---

## 🔄 Reiniciar o Servidor

Após configurar o `.env`, **reinicie o servidor Flask** para que as novas configurações sejam carregadas:

```bash
# Pare o servidor (Ctrl+C)
# Depois inicie novamente
python start.py
```

---

## ✅ Como Verificar se Está Funcionando

1. **Verifique os logs do servidor:**
   - Ao registrar um novo usuário, você deve ver:
     ```
     [EMAIL] ✅ Enviado com sucesso de: seu_email@gmail.com | Para: novo_usuario@email.com
     ```

2. **Teste criando uma nova conta:**
   - Registre um novo usuário
   - Verifique a caixa de entrada do email
   - **Não esqueça de verificar a pasta de SPAM/Lixo Eletrônico**

3. **Verifique os logs do servidor:**
   - Se não estiver configurado, verá:
     ```
     [REGISTER] ⚠️ EMAIL NÃO CONFIGURADO - conta marcada como verificada automaticamente
     ```

---

## ⚠️ Problemas Comuns

### 1. "Erro ao enviar email" / "Authentication failed"

**Solução:**
- Gmail: Verifique se está usando uma **Senha de App** (não a senha normal)
- Outlook: Tente usar a senha normal
- Verifique se o email e senha estão corretos no `.env`

### 2. Emails vão para SPAM

**Solução:**
- Normal em desenvolvimento (localhost)
- Em produção, configure SPF/DKIM no domínio
- Peça aos usuários para verificar a pasta de SPAM

### 3. "Connection timeout"

**Solução:**
- Verifique se sua rede/firewall permite conexões SMTP
- Tente usar outra porta (465 com SSL ao invés de 587 com TLS)

### 4. Gmail bloqueia o acesso

**Solução:**
- Ative "Acesso a apps menos seguros" (não recomendado)
- **Melhor:** Use Senha de App (recomendado)

---

## 🔒 Segurança

### ⚠️ IMPORTANTE:

1. **NUNCA** commite o arquivo `.env` no Git
2. O arquivo `.env` já está no `.gitignore`
3. Use **Senha de App** ao invés de senha normal quando possível
4. Em produção, use variáveis de ambiente do servidor ao invés de arquivo `.env`

---

## 📊 Status Atual

Para verificar se o email está configurado:

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print('MAIL_USERNAME:', os.getenv('MAIL_USERNAME', 'NÃO CONFIGURADO')); print('MAIL_PASSWORD:', 'CONFIGURADO' if os.getenv('MAIL_PASSWORD') else 'NÃO CONFIGURADO')"
```

---

## 🎯 Próximos Passos

1. ✅ Configure o `.env` com suas credenciais de email
2. ✅ Reinicie o servidor Flask
3. ✅ Teste criando uma nova conta
4. ✅ Verifique se o email de validação foi recebido
5. ✅ Clique no link de verificação no email

---

## 📞 Ajuda Adicional

Se ainda tiver problemas:
1. Verifique os logs do servidor para mensagens de erro
2. Teste as credenciais em outro cliente de email (Thunderbird, Outlook)
3. Verifique se o provedor de email permite SMTP (alguns bloqueiam)

---

**Última atualização:** Agora o sistema mostra avisos claros quando o email não está configurado! 🎉

