# Fluxo de Cadastro e Recuperação de Senha (pelo site e email)

Tudo é feito **pelo site** e **por email** — o usuário não precisa de código nem de scripts.

---

## 1. Cadastro (criar conta)

1. Usuário acessa o site e clica em **Cadastrar**.
2. Preenche **Nome**, **E-mail**, **Senha** e opcionalmente **Nome do bebê**.
3. Clica em **Criar Conta**.
4. O sistema:
   - Cria a conta no banco (SQLite).
   - Se o **email estiver configurado** no servidor (`MAIL_USERNAME` e `MAIL_PASSWORD` no `.env`):
     - Envia um **email de verificação** com um link.
     - A mensagem diz para a usuária **clicar no link** para ativar a conta.
   - Se o email **não** estiver configurado (desenvolvimento):
     - A conta é ativada automaticamente e a mensagem informa que já pode fazer login.

5. **Quando o email está configurado:** a usuária abre o email, clica no link e é levada à página **"E-mail Confirmado!"**. Depois pode fazer login no site.

**Link do email de verificação:**  
`https://seu-dominio.com/api/verify-email?token=...`  
→ Abre a página de confirmação e ativa a conta.

---

## 2. Esqueci minha senha

1. Usuário clica em **Esqueci minha senha** (na tela de login) ou acessa `/forgot-password`.
2. Informa o **e-mail cadastrado** e clica em **Clique para Recuperar**.
3. O sistema:
   - Se o **email estiver configurado** no servidor:
     - Gera um token e salva no banco.
     - Envia um **email** com um link para **redefinir a senha**.
   - Se o email **não** estiver configurado:
     - Responde com erro **503** e a mensagem: *"O servidor não está configurado para enviar emails. Entre em contato com o administrador do site."*

4. **Quando o email está configurado:** a usuária abre o email e clica no link. Ela é levada à **página de redefinição de senha** no site (`/reset-password?token=...`).
5. Nessa página ela digita a **nova senha** e **confirma**, depois clica em **Redefinir Senha**.
6. O sistema atualiza a senha e redireciona para a tela de login. Ela entra com o **novo** e-mail e a **nova senha**.

**Link do email de recuperação:**  
`https://seu-dominio.com/reset-password?token=...`  
→ Abre a página do site onde ela define a nova senha (só pelo site, não por código).

---

## Configuração do servidor para envio de emails

Para que os usuários **recebam** os emails (verificação e recuperação de senha), o servidor precisa ter email configurado no `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=senha_de_app_do_gmail
```

- **Gmail:** use [Senha de App](https://myaccount.google.com/apppasswords), não a senha normal da conta.
- Sem `MAIL_USERNAME` e `MAIL_PASSWORD`:
  - **Cadastro:** a conta é criada e ativada automaticamente (modo desenvolvimento).
  - **Esqueci minha senha:** a API retorna 503 e a mensagem para contatar o administrador; nenhum link é enviado.

---

## Resumo

| Ação | Onde | Email | Página após o link |
|------|------|--------|---------------------|
| **Cadastro** | Site (Cadastrar → Criar Conta) | Link de verificação | `/api/verify-email?token=...` → "E-mail Confirmado!" |
| **Esqueci minha senha** | Site (Esqueci minha senha → Clique para Recuperar) | Link de recuperação | `/reset-password?token=...` → formulário "Nova senha" |

Tudo é feito **pelo site** e **por email**; o usuário não precisa executar código nem scripts.
