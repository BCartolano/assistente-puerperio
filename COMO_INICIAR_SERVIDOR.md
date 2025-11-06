# 🚀 Como Iniciar o Servidor Flask

## ⚠️ Erro Comum

Se você tentar executar:
```bash
python app.py
```

Você receberá o erro:
```
can't open file 'app.py': [Errno 2] No such file or directory
```

**Por quê?** O arquivo `app.py` está em `backend/app.py`, não na raiz do projeto.

---

## ✅ Formas Corretas de Iniciar o Servidor

### **Opção 1: Usar `start.py` (Recomendado)** ⭐

Na raiz do projeto, execute:

```bash
python start.py
```

Este script:
- ✅ Verifica a versão do Python
- ✅ Ativa o ambiente virtual automaticamente
- ✅ Configura os caminhos corretos
- ✅ Inicia o servidor Flask na porta 5000

---

### **Opção 2: Entrar na pasta backend**

```bash
cd backend
python app.py
```

Ou em uma linha:
```bash
cd backend && python app.py
```

---

### **Opção 3: Usar Flask diretamente**

Na raiz do projeto:
```bash
cd backend
python -m flask run --host=0.0.0.0 --port=5000
```

---

### **Opção 4: Usar o ambiente virtual diretamente**

```bash
# Windows
backend\venv\Scripts\python.exe backend\app.py

# Linux/Mac
backend/venv/bin/python backend/app.py
```

---

## 📁 Estrutura do Projeto

```
chatbot-puerperio/
├── start.py          ← Use este para iniciar (recomendado)
├── backend/
│   ├── app.py        ← Arquivo principal do Flask
│   ├── templates/
│   ├── static/
│   └── venv/         ← Ambiente virtual
└── ...
```

---

## 🎯 Recomendação

**Use sempre `python start.py` na raiz do projeto!**

Este é o método mais simples e confiável, pois:
- ✅ Funciona em qualquer sistema
- ✅ Configura tudo automaticamente
- ✅ Verifica dependências
- ✅ Ativa o ambiente virtual
- ✅ Usa os caminhos corretos

---

## 🔧 Solução de Problemas

### Erro: "No module named 'flask'"

**Solução:** Ative o ambiente virtual primeiro:
```bash
# Windows
backend\venv\Scripts\activate

# Linux/Mac
source backend/venv/bin/activate
```

Depois execute:
```bash
python start.py
```

### Erro: "Port 5000 is already in use"

**Solução:** Pare o processo que está usando a porta 5000 ou use outra porta:
```bash
# No backend/app.py, altere a última linha para:
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## 📝 Notas Importantes

1. **Sempre use `start.py`** - É a forma mais segura
2. **Não execute `python app.py` na raiz** - O arquivo não está lá
3. **O servidor inicia em:** `http://localhost:5000`
4. **Para parar:** Pressione `Ctrl+C` no terminal

---

## ✅ Comandos Rápidos

```bash
# Iniciar servidor (recomendado)
python start.py

# Verificar estrutura
ls backend/app.py    # Linux/Mac
dir backend\app.py   # Windows

# Entrar na pasta backend
cd backend
python app.py
```

