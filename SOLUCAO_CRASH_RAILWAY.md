# 🚨 Solução para Crash no Railway

## Problemas Comuns e Soluções

### 1. Erro: "libsqlite3.so.0: cannot open shared object file"

**Solução:**
- O `nixpacks.toml` já está configurado para instalar SQLite
- O `Dockerfile` também está configurado com `libsqlite3-dev`
- Se ainda ocorrer, force o Railway a usar o Dockerfile:
  1. Vá em **Settings** → **Deploy**
  2. Selecione **"Dockerfile"** como método de build
  3. Faça um novo deploy

### 2. Variáveis de Ambiente Faltando

**OBRIGATÓRIAS no Railway:**
```
SECRET_KEY=sua-chave-secreta-aqui
GEMINI_API_KEY=sua-chave-gemini-aqui
FLASK_ENV=production
```

**OPCIONAIS (mas recomendadas):**
```
PORT=8080
BASE_URL=https://seu-projeto.up.railway.app
```

**Para configurar:**
1. No Railway, vá em **Variables**
2. Adicione cada variável clicando em **New Variable**
3. Após adicionar, o Railway fará redeploy automático

### 3. Verificar Logs do Railway

**Como ver os logs:**
1. No projeto do Railway, clique na aba **Deployments**
2. Clique no deployment mais recente
3. Veja os logs para identificar o erro exato

**Logs importantes a procurar:**
- ✅ `✅ App Flask carregado com sucesso`
- ❌ `❌ ERRO CRÍTICO ao carregar app:`
- ❌ `libsqlite3.so.0: cannot open`
- ❌ `ModuleNotFoundError`
- ❌ `ImportError`

### 4. Forçar Redeploy

Se o problema persistir:
1. Vá em **Deployments**
2. Clique nos três pontos (⋯) do deployment mais recente
3. Selecione **"Redeploy"**
4. Aguarde o build completar

### 5. Verificar Configuração do Serviço

**No Railway:**
1. Vá em **Settings** → **Deploy**
2. Verifique:
   - **Build Command**: Deve estar vazio (usa o `nixpacks.toml` ou `Dockerfile`)
   - **Start Command**: Deve estar vazio (usa o `Procfile` ou `nixpacks.toml`)
   - Ou configure manualmente:
     - Build: `pip install -r requirements.txt`
     - Start: `gunicorn wsgi:app --bind 0.0.0.0:$PORT`

### 6. Checklist de Verificação

Antes de fazer deploy, verifique:

- [ ] Variável `SECRET_KEY` configurada no Railway
- [ ] Variável `GEMINI_API_KEY` configurada no Railway
- [ ] Variável `FLASK_ENV=production` configurada no Railway
- [ ] Arquivo `nixpacks.toml` existe na raiz do projeto
- [ ] Arquivo `Dockerfile` existe na raiz do projeto
- [ ] Arquivo `wsgi.py` existe na raiz do projeto
- [ ] Arquivo `Procfile` existe na raiz do projeto
- [ ] Repositório está sincronizado com GitHub

### 7. Se Nada Funcionar

**Opção 1: Usar Dockerfile explicitamente**
1. No Railway, **Settings** → **Deploy**
2. Selecione **"Dockerfile"** como builder
3. Faça redeploy

**Opção 2: Limpar e recriar**
1. Delete o projeto no Railway
2. Crie um novo projeto
3. Conecte ao mesmo repositório GitHub
4. Configure as variáveis de ambiente novamente

## 📞 Precisa de Ajuda?

Se ainda estiver com problemas:
1. Copie os logs completos do Railway
2. Verifique quais erros aparecem
3. Verifique se todas as variáveis de ambiente estão configuradas
