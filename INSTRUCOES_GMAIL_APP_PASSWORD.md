# Como Gerar Senha de App do Gmail

## Problema
Se você recebeu o erro `535, b'5.7.8 Username and Password not accepted'`, significa que a senha de app do Gmail está incorreta ou expirada.

## Solução: Gerar Nova Senha de App

### Passo 1: Ativar Verificação em Duas Etapas
1. Acesse: https://myaccount.google.com/security
2. Procure por "Verificação em duas etapas"
3. Ative se ainda não estiver ativada

### Passo 2: Gerar Senha de App
1. Acesse: https://myaccount.google.com/apppasswords
2. Se necessário, faça login novamente
3. Em "Selecione o app", escolha "Mail"
4. Em "Selecione o dispositivo", escolha "Outro (nome personalizado)"
5. Digite: "Sophia - Chatbot Puerperio"
6. Clique em "Gerar"
7. **Copie a senha de 16 caracteres** (sem espaços)

### Passo 3: Atualizar o arquivo .env
1. Abra o arquivo `.env` na raiz do projeto
2. Atualize a linha `MAIL_PASSWORD` com a nova senha de 16 caracteres:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=cartuchocartolano@gmail.com
MAIL_PASSWORD=SUA_NOVA_SENHA_DE_16_CARACTERES_AQUI
MAIL_DEFAULT_SENDER=cartuchocartolano@gmail.com
```

### Passo 4: Reiniciar o servidor Flask
Após atualizar o `.env`, reinicie o servidor Flask para que as novas configurações sejam carregadas.

### Passo 5: Testar
Execute o script de teste:
```bash
python test_email.py
```

Se funcionar, você verá a mensagem "OK - E-mail enviado com sucesso!"

## Importante
- A senha de app é diferente da senha normal da conta Gmail
- A senha de app tem 16 caracteres (sem espaços)
- Se você gerar uma nova senha de app, a anterior será invalidada
- Mantenha a senha de app segura e não compartilhe

## Notas
- Se você deletar a senha de app, precisará gerar uma nova
- Cada senha de app é única e não pode ser reutilizada
- O Gmail pode limitar o número de senhas de app por conta

