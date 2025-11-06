# 🧪 Como Testar a Configuração de Email

## 📋 Problema

Você já configurou:
- ✅ Verificação em Duas Etapas no Gmail
- ✅ Senha de App criada

Mas os emails ainda não estão sendo enviados.

## ✅ Solução: Criar arquivo `.env`

### Opção 1: Usar Script Automático (Recomendado)

Execute o script que criei:

```bash
python configurar_email.py
```

O script vai:
1. Perguntar qual provedor de email usar
2. Solicitar suas credenciais
3. Criar o arquivo `.env` automaticamente
4. Testar a configuração

### Opção 2: Criar Manualmente

1. **Crie um arquivo `.env` na raiz do projeto** (mesma pasta que `start.py`)

2. **Adicione as seguintes linhas:**

```env
# Configurações de Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=suasenhaapp16caracteres
MAIL_DEFAULT_SENDER=seu_email@gmail.com

# Outras configurações (se necessário)
BASE_URL=http://localhost:5000
```

**IMPORTANTE:**
- `MAIL_USERNAME`: Seu email Gmail completo
- `MAIL_PASSWORD`: A **Senha de App** de 16 caracteres (NÃO a senha normal)
- `MAIL_DEFAULT_SENDER`: Mesmo email do MAIL_USERNAME

## 🔄 Após Configurar

### 1. Reinicie o Servidor Flask

```bash
# Pare o servidor (Ctrl+C)
# Depois inicie novamente
python start.py
```

### 2. Verifique os Logs

Quando criar uma nova conta, você deve ver nos logs:

**Se funcionar:**
```
[EMAIL] ✅ Enviado com sucesso de: seu_email@gmail.com | Para: novo_usuario@email.com
```

**Se houver erro:**
```
[EMAIL] ❌ Erro ao enviar email: [mensagem de erro]
[EMAIL] ⚠️ Erro de autenticação! (ou outro erro específico)
```

## 🧪 Testar Configuração

Para testar se a configuração está correta:

```bash
python configurar_email.py test
```

## ⚠️ Problemas Comuns

### 1. "Authentication failed" / "535"

**Causa:** Senha incorreta ou não é Senha de App

**Solução:**
- Verifique se está usando a **Senha de App** (16 caracteres sem espaços)
- Não use a senha normal da conta Gmail
- Gere uma nova Senha de App: https://myaccount.google.com/apppasswords

### 2. "Connection timeout"

**Causa:** Servidor SMTP ou porta incorretos

**Solução:**
- Verifique se `MAIL_SERVER=smtp.gmail.com`
- Verifique se `MAIL_PORT=587`
- Tente usar porta 465 com `MAIL_USE_TLS=False` e `MAIL_USE_SSL=True`

### 3. Email não aparece mesmo após sucesso

**Causa:** Email pode estar na pasta de SPAM

**Solução:**
- Verifique a pasta de SPAM/Lixo Eletrônico
- Marque como "Não é spam" se encontrar
- Peça ao usuário para verificar também

### 4. Arquivo .env não é carregado

**Causa:** Servidor não foi reiniciado após criar .env

**Solução:**
- **Sempre reinicie o servidor** após modificar o arquivo `.env`
- Verifique se o arquivo está na raiz do projeto (mesma pasta que `start.py`)

## 📝 Verificar Configuração Atual

Para ver quais configurações estão sendo usadas:

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print('MAIL_SERVER:', os.getenv('MAIL_SERVER')); print('MAIL_PORT:', os.getenv('MAIL_PORT')); print('MAIL_USERNAME:', os.getenv('MAIL_USERNAME')); print('MAIL_PASSWORD:', 'CONFIGURADO' if os.getenv('MAIL_PASSWORD') else 'NÃO CONFIGURADO')"
```

## 🎯 Próximos Passos

1. ✅ Crie o arquivo `.env` com suas credenciais
2. ✅ Reinicie o servidor Flask
3. ✅ Teste criando uma nova conta
4. ✅ Verifique os logs do servidor
5. ✅ Verifique a caixa de entrada (e SPAM) do novo usuário

---

**Lembre-se:** O arquivo `.env` NÃO está no Git (está no `.gitignore`), então você precisa criá-lo manualmente em cada ambiente!

