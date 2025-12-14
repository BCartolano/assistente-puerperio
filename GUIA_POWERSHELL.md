# 🔧 Guia de Uso - Scripts PowerShell

Este guia explica como usar os scripts PowerShell criados para resolver problemas de encoding e facilitar o uso do projeto no Windows.

## 📋 Scripts Disponíveis

### 1. `iniciar-servidor.ps1`
Inicia o servidor Flask com encoding UTF-8 configurado corretamente.

**Uso:**
```powershell
.\iniciar-servidor.ps1
```

**O que faz:**
- Configura encoding UTF-8 no PowerShell
- Verifica se Python está instalado
- Inicia o servidor Flask
- Garante que caracteres especiais e emojis apareçam corretamente

---

### 2. `iniciar-com-ngrok.ps1`
Inicia o servidor Flask e o ngrok com encoding UTF-8 configurado.

**Uso:**
```powershell
.\iniciar-com-ngrok.ps1
```

**O que faz:**
- Configura encoding UTF-8 no PowerShell
- Verifica se Python e ngrok estão disponíveis
- Inicia o servidor Flask em uma janela separada
- Inicia o ngrok para criar um túnel público
- Mostra o link público do ngrok

---

### 3. `testar-encoding.ps1`
Testa se o encoding UTF-8 está funcionando corretamente.

**Uso:**
```powershell
.\testar-encoding.ps1
```

**O que faz:**
- Testa encoding do PowerShell
- Testa exibição de caracteres especiais
- Testa exibição de emojis
- Testa encoding do Python
- Executa `verificar_config.py` para verificar a configuração

---

### 4. `verificar-problemas-powershell.ps1`
Verifica e diagnostica problemas comuns no PowerShell.

**Uso:**
```powershell
.\verificar-problemas-powershell.ps1
```

**O que verifica:**
- Política de execução do PowerShell
- Configuração de encoding UTF-8
- Instalação do Python
- Variáveis de ambiente do Python
- Arquivos necessários do projeto
- Scripts PowerShell disponíveis
- Exibição de caracteres especiais

---

## 🚀 Primeiro Uso

### Passo 1: Verificar Política de Execução

Se você receber um erro sobre política de execução, execute:

```powershell
# Como Administrador (se necessário)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Ou apenas para a sessão atual:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### Passo 2: Verificar Problemas

Execute o script de verificação:

```powershell
.\verificar-problemas-powershell.ps1
```

Este script irá:
- Verificar se tudo está configurado corretamente
- Mostrar problemas encontrados
- Sugerir soluções

### Passo 3: Testar Encoding

Execute o script de teste:

```powershell
.\testar-encoding.ps1
```

Verifique se:
- ✅ Caracteres especiais aparecem corretamente (á, é, í, ó, ú, ã, õ, ç)
- ✅ Emojis aparecem corretamente (✅, ❌, ⚠️, etc.)
- ✅ Python está configurado com UTF-8

### Passo 4: Iniciar o Servidor

**Opção A: Sem ngrok (apenas local)**
```powershell
.\iniciar-servidor.ps1
```

**Opção B: Com ngrok (acesso público)**
```powershell
.\iniciar-com-ngrok.ps1
```

---

## 🔍 Problemas Comuns e Soluções

### Problema 1: "Script não pode ser executado"

**Erro:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solução:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Problema 2: Caracteres especiais não aparecem

**Sintoma:** Caracteres como `á`, `é`, `ç` aparecem como `?` ou caracteres estranhos.

**Solução:**
Os scripts PowerShell já configuram o encoding automaticamente. Se ainda houver problemas:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
$env:PYTHONIOENCODING = "utf-8"
```

---

### Problema 3: Emojis não aparecem

**Sintoma:** Emojis aparecem como `?` ou caracteres estranhos.

**Solução:**
1. Use os scripts PowerShell fornecidos (eles configuram o encoding)
2. Certifique-se de que a fonte do terminal suporta emojis
3. Use PowerShell Core (7+) se possível (melhor suporte a UTF-8)

---

### Problema 4: Python não encontrado

**Erro:**
```
Python não encontrado
```

**Solução:**
1. Instale Python 3.8 ou superior
2. Durante a instalação, marque "Add Python to PATH"
3. Ou adicione manualmente ao PATH:
   - Encontre onde Python foi instalado (geralmente `C:\Python3x\` ou `C:\Users\SeuUsuario\AppData\Local\Programs\Python\Python3x\`)
   - Adicione ao PATH nas variáveis de ambiente do Windows

---

### Problema 5: ngrok não encontrado

**Erro:**
```
ngrok não encontrado
```

**Solução:**
1. Baixe o ngrok de: https://ngrok.com/download
2. Extraia o `ngrok.exe`
3. Coloque na pasta do projeto OU adicione ao PATH
4. Veja `COMO_INSTALAR_NGROK.md` para mais detalhes

---

## 📝 Melhorias Implementadas

### Encoding UTF-8
- ✅ Scripts PowerShell configuram encoding automaticamente
- ✅ Arquivos Python configuram encoding antes de qualquer I/O
- ✅ Variável `PYTHONIOENCODING` configurada automaticamente
- ✅ Variável `PYTHONLEGACYWINDOWSSTDIO` configurada para usar UTF-8 nativo

### Arquivos Modificados
- ✅ `start.py` - Configuração melhorada de encoding
- ✅ `verificar_config.py` - Configuração melhorada de encoding
- ✅ `backend/app.py` - Configuração melhorada de encoding

### Scripts Criados
- ✅ `iniciar-servidor.ps1` - Inicia servidor com encoding correto
- ✅ `iniciar-com-ngrok.ps1` - Inicia servidor + ngrok com encoding correto
- ✅ `testar-encoding.ps1` - Testa se encoding está funcionando
- ✅ `verificar-problemas-powershell.ps1` - Diagnostica problemas

---

## 🎯 Recomendações

1. **Use PowerShell Core (7+)** se possível - tem melhor suporte a UTF-8 nativo
2. **Use os scripts PowerShell** em vez de executar Python diretamente - eles garantem encoding correto
3. **Execute `verificar-problemas-powershell.ps1`** antes de começar a trabalhar no projeto
4. **Execute `testar-encoding.ps1`** se tiver dúvidas sobre encoding

---

## 📚 Referências

- [Documentação PowerShell - Encoding](https://docs.microsoft.com/powershell/module/microsoft.powershell.core/about/about_character_encoding)
- [Python - Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
- [UTF-8 no Windows](https://docs.microsoft.com/windows/console/console-virtual-terminal-sequences)

---

**Última atualização:** 2025-01-27  
**Status:** Scripts criados e testados  
**Compatibilidade:** Windows 10/11, PowerShell 5.1+ e PowerShell Core 7+
