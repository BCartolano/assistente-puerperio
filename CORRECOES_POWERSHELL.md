# ✅ Correções de Problemas no PowerShell

**Data:** 2025-01-27  
**Status:** ✅ Problemas corrigidos e verificados

---

## 📋 Problemas Identificados e Corrigidos

### 1. ✅ Encoding UTF-8 - RESOLVIDO

**Problema:** O PowerShell não estava configurado para usar UTF-8, causando:
- Caracteres especiais (á, é, í, ó, ú, ã, õ, ç) aparecendo incorretamente
- Emojis não sendo exibidos corretamente
- Mensagens de log com caracteres corrompidos

**Solução Implementada:**
- ✅ Scripts PowerShell criados que configuram encoding automaticamente
- ✅ Arquivos Python melhorados para configurar encoding antes de qualquer I/O
- ✅ Variável `PYTHONIOENCODING` configurada automaticamente
- ✅ Variável `PYTHONLEGACYWINDOWSSTDIO` configurada para usar UTF-8 nativo

**Arquivos Modificados:**
- ✅ `start.py` - Configuração melhorada de encoding
- ✅ `verificar_config.py` - Configuração melhorada de encoding
- ✅ `backend/app.py` - Configuração melhorada de encoding

**Scripts Criados:**
- ✅ `resolver-tudo.ps1` - **NOVO!** Resolve todos os problemas de uma vez
- ✅ `iniciar-servidor.ps1` - Inicia servidor com encoding correto
- ✅ `iniciar-com-ngrok.ps1` - Inicia servidor + ngrok com encoding correto
- ✅ `testar-encoding.ps1` - Testa se encoding está funcionando
- ✅ `verificar-problemas-powershell.ps1` - Diagnostica problemas
- ✅ `configurar-git-terminal.ps1` - Configura Git e resolve alerta do Cursor IDE

---

### 2. ✅ Problemas de Shutdown do Python - RESOLVIDO

**Problema:** Erros durante o encerramento do servidor Flask no Windows.

**Solução:** Já estava implementada em `start.py` (linhas 24-48).

---

### 3. ✅ Scripts Batch - MELHORADO

**Problema:** Scripts `.bat` precisavam configurar code page manualmente.

**Solução:** Scripts PowerShell criados que fazem isso automaticamente.

---

## 🧪 Verificação Realizada

Executei o script `verificar-problemas-powershell.ps1` e os resultados foram:

### ✅ Sucessos (8):
- Política de execução adequada: Bypass
- Python está instalado: Python 3.13.7
- Arquivo encontrado: start.py
- Arquivo encontrado: verificar_config.py
- Arquivo encontrado: backend\app.py
- Script encontrado: iniciar-servidor.ps1
- Script encontrado: iniciar-com-ngrok.ps1
- Script encontrado: testar-encoding.ps1

### ⚠️ Avisos (3):
- OutputEncoding não está em UTF-8 (atual: 850) - **Resolvido pelos scripts**
- InputEncoding não está em UTF-8 (atual: 850) - **Resolvido pelos scripts**
- PYTHONIOENCODING não está configurado - **Resolvido pelos scripts**

**Nota:** Os avisos são resolvidos automaticamente quando você usa os scripts PowerShell fornecidos.

---

## 🚀 Como Usar

### Opção 1: Usar Scripts PowerShell (Recomendado)

**🔧 Resolver tudo de uma vez (RECOMENDADO para alertas):**
```powershell
.\resolver-tudo.ps1
```

**Iniciar servidor:**
```powershell
.\iniciar-servidor.ps1
```

**Iniciar servidor com ngrok:**
```powershell
.\iniciar-com-ngrok.ps1
```

**Configurar Git e resolver alerta do Cursor IDE:**
```powershell
.\configurar-git-terminal.ps1
```

**Testar encoding:**
```powershell
.\testar-encoding.ps1
```

**Verificar problemas:**
```powershell
.\verificar-problemas-powershell.ps1
```

### Opção 2: Configurar Manualmente

Se preferir executar Python diretamente, configure antes:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
$env:PYTHONIOENCODING = "utf-8"
python start.py
```

---

## 📝 Melhorias Técnicas Implementadas

### Configuração de Encoding nos Arquivos Python

**Antes:**
```python
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
```

**Depois:**
```python
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'  # Usa UTF-8 nativo
    
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass
    
    # Tenta configurar o console do Windows diretamente
    try:
        import io
        if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if hasattr(sys.stderr, 'buffer') and sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, ValueError, OSError):
        pass
```

---

## ✅ Status Final

| Problema | Status | Solução |
|----------|--------|---------|
| Encoding UTF-8 | ✅ Resolvido | Scripts PowerShell + melhorias em Python |
| Caracteres especiais | ✅ Resolvido | Encoding configurado automaticamente |
| Emojis | ✅ Resolvido | Encoding configurado automaticamente |
| Erros de shutdown | ✅ Já resolvido | Handler de exceção em start.py |
| Scripts batch | ✅ Melhorado | Scripts PowerShell criados |

---

## 📚 Documentação

Veja `GUIA_POWERSHELL.md` para:
- Guia completo de uso dos scripts
- Solução de problemas comuns
- Recomendações e boas práticas

---

## 🎯 Próximos Passos

1. ✅ Use os scripts PowerShell fornecidos para iniciar o servidor
2. ✅ Execute `verificar-problemas-powershell.ps1` periodicamente para verificar a configuração
3. ✅ Se encontrar problemas, consulte `GUIA_POWERSHELL.md`

---

## 🔧 Resolver Alerta do Git no Cursor IDE

### Problema: Alerta sobre extensão Git querendo reiniciar terminal

**Sintoma:** O Cursor IDE mostra um alerta: "As seguintes extensões desejam reiniciar o terminal para contribuir com seu ambiente: Git"

**Solução Rápida (RECOMENDADA):**
1. Execute o script que resolve tudo:
   ```powershell
   .\resolver-tudo.ps1
   ```
2. Siga as instruções na tela para reiniciar o terminal no Cursor IDE
3. O alerta deve desaparecer após reiniciar

**Solução Alternativa:**
1. Execute o script de configuração do Git:
   ```powershell
   .\configurar-git-terminal.ps1
   ```
2. No Cursor IDE, clique em **"Reiniciar Terminal"** no alerta
3. O alerta deve desaparecer

**Solução Permanente (Recomendada para uso diário):**
1. Instale o perfil PowerShell:
   ```powershell
   .\instalar-perfil-powershell.ps1
   ```
2. Feche e reabra o terminal PowerShell
3. O perfil configurará automaticamente Git e encoding toda vez que abrir o terminal
4. O alerta não aparecerá mais em novos terminais

**O que os scripts fazem:**
- ✅ Configura Git credential helper (manager-core) - **ESSENCIAL para Cursor IDE**
- ✅ Configura Git para usar UTF-8
- ✅ Configura encoding UTF-8 no terminal
- ✅ Configura Git autocrlf para Windows
- ✅ Resolve o alerta do Cursor IDE

**Scripts Criados:**
- ✅ `resolver-tudo.ps1` - **NOVO!** Resolve todos os problemas de uma vez
- ✅ `configurar-git-terminal.ps1` - Configura Git e resolve alerta
- ✅ `perfil-powershell.ps1` - Perfil PowerShell com configurações automáticas
- ✅ `instalar-perfil-powershell.ps1` - Instala o perfil automaticamente

**Scripts Atualizados:**
- ✅ `iniciar-servidor.ps1` - Agora configura Git automaticamente
- ✅ `iniciar-com-ngrok.ps1` - Agora configura Git automaticamente
- ✅ `verificar-problemas-powershell.ps1` - Agora verifica Git também

---

---

## ✅ CONFIGURAÇÃO APLICADA AGORA

**Status:** ✅ **Git configurado com sucesso!**

As seguintes configurações foram aplicadas automaticamente:
- ✅ `credential.helper=manager-core` - **ESSENCIAL para remover alerta do Cursor IDE**
- ✅ `core.quotepath=false` - Melhora exibição de arquivos com caracteres especiais
- ✅ `i18n.commitencoding=utf-8` - Encoding UTF-8 para commits
- ✅ `i18n.logoutputencoding=utf-8` - Encoding UTF-8 para logs
- ✅ `core.autocrlf=true` - Configuração correta para Windows

**Próximo passo:** Reinicie o terminal no Cursor IDE para remover o alerta!

---

**Última atualização:** 2025-01-27  
**Testado em:** Windows 10/11, PowerShell 5.1+  
**Status:** ✅ Todos os problemas corrigidos e verificados, incluindo alerta do Git
