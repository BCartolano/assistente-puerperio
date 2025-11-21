# 🤱 Assistente Puerpério

Um chatbot **COMPLETO** especializado em oferecer apoio e informações sobre gestação, parto e puerpério, desenvolvido com foco na saúde materna e bem-estar das mães e bebês.

## ✨ Funcionalidades Principais

### 💬 Chat Inteligente
- **79 categorias** de perguntas e respostas sobre gestação, parto, puerpério, amamentação e cuidados com bebê
- Sistema de respostas baseado em IA (OpenAI) com fallback inteligente
- Detecção automática de alertas médicos
- Mensagens de apoio empáticas e acolhedoras
- **Telefones úteis incluídos automaticamente** nas respostas

### 📞 Telefones Úteis Integrados
- **CVV 188** - Prevenção do suicídio (24h/dia)
- **Emergências**: SAMU 192, Bombeiros 193, Polícia 190
- Disque Saúde, Disque Mãe, Disque Amamentação
- Informações sobre UPAs, Postos de Saúde e Maternidades
- **Aparecem automaticamente** quando relevante!

### 🩺 Guias Práticos
- **7 guias completos** com passos detalhados:
  - Como aliviar cólicas do bebê (7 técnicas)
  - Manobra de Heimlich em bebês
  - RCP (Reanimação cardiopulmonar)
  - Como ajudar o bebê a arrotar
  - Como dar banho de forma segura
  - Troca de fralda preventiva
  - Posições seguras para dormir

### 📅 Cuidados Personalizados
- **Gestação**: Cuidados por trimestres (1º, 2º, 3º)
- **Pós-parto**: Guias mensais (1º, 2º, 3º mês e meses 4-6)
- Desenvolvimento do bebê
- Exames necessários
- Sinais de alerta
- Orientação de amamentação

### 💉 Carteira de Vacinação
- **Vacinas da mãe**: Pré-natal e pós-parto
- **Vacinas do bebê**: Calendário completo 0-12 meses
- Quando e onde vacinar
- Efeitos colaterais comuns
- Baseado no Calendário Nacional de Imunizações

### 🎨 Interface Moderna
- Design responsivo e intuitivo
- Funciona perfeitamente em desktop e mobile
- Perguntas rápidas pré-definidas
- Histórico de conversas
- Modal de alertas médicos

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **IA**: OpenAI (obrigatório)
- **Estilização**: CSS customizado com gradientes e animações
- **Ícones**: Font Awesome

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd chatbot-puerperio
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**:
   ```bash
   # Copie o arquivo de template
   copy .env.template .env
   
   # Edite o arquivo .env e adicione sua chave do OpenAI (obrigatório)
   OPENAI_API_KEY=sua_chave_openai_aqui
   USE_AI=true
   ```

5. **Execute o aplicativo**:
   ```bash
   # Opção 1: Usando wsgi (recomendado para produção)
   python wsgi.py
   
   # Opção 2: Direto pelo backend (desenvolvimento)
   cd backend && python app.py
   ```

6. **Acesse no navegador**:
   ```
   http://localhost:5000
   ```

## 📁 Estrutura do Projeto

```
chatbot-puerperio/
├── backend/
│   ├── app.py                      # Aplicação Flask principal
│   ├── templates/
│   │   └── index.html              # Interface web
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css           # Estilos da interface
│   │   └── js/
│   │       └── chat.js             # Lógica do frontend
│   ├── base_conhecimento.json      # Base sincronizada
│   ├── mensagens_apoio.json        # Apoio sincronizado
│   ├── telefones_uteis.json        # Telefones sincronizado
│   ├── guias_praticos.json         # Guias sincronizado
│   └── outros JSONs sincronizados
├── dados/                           # Base de conhecimento
│   ├── base_conhecimento.json      # 79 perguntas e respostas
│   ├── mensagens_apoio.json        # 10 mensagens empáticas
│   ├── alertas.json                # Alertas médicos
│   ├── telefones_uteis.json        # Telefones úteis
│   ├── guias_praticos.json         # 7 guias práticos
│   ├── cuidados_gestacao.json      # Cuidados por trimestre
│   ├── cuidados_pos_parto.json     # Cuidados por período
│   ├── vacinas_mae.json            # Vacinas da mãe
│   └── vacinas_bebe.json           # Vacinas do bebê
├── wsgi.py                         # Entry point WSGI
├── Procfile                        # Config Heroku/Render
├── render.yaml                     # Config Render
├── runtime.txt                     # Python 3.11
├── requirements.txt                # Dependências
├── README.md                       # Este arquivo
└── README_DEPLOY.md                # Instruções de deploy
```

## 🔧 Configuração da API OpenAI (Obrigatório)

O chatbot utiliza a API da OpenAI para fornecer respostas inteligentes e humanizadas. Para configurar:

1. **Acesse [OpenAI Platform](https://platform.openai.com/api-keys)**
2. **Crie uma conta OpenAI** (se necessário) e adicione créditos
3. **Gere uma chave de API**
4. **Adicione no arquivo `.env`**:
   ```
   OPENAI_API_KEY=sua_chave_openai_aqui
   USE_AI=true
   ```

**Nota:** O `OPENAI_ASSISTANT_ID` é **opcional**. Se não for configurado, o sistema criará automaticamente um assistente chamado "Sophia" na primeira execução. Se você já tiver um assistente criado, pode adicionar o ID no `.env` para reutilizá-lo:
```
OPENAI_ASSISTANT_ID=asst_xxxxx
```

## 📊 Base de Conhecimento

O sistema inclui informações sobre:

- **Identidade**: Mudanças emocionais no puerpério
- **Alimentação**: Nutrição adequada pós-parto
- **Baby Blues**: Depressão pós-parto leve
- **Puerpério**: Conceitos gerais sobre o período

### Adicionando Conteúdo

Para expandir a base de conhecimento, edite o arquivo `dados/base_conhecimento.json`:

```json
{
  "nova_categoria": {
    "pergunta": "Sua pergunta aqui?",
    "resposta": "Resposta detalhada aqui."
  }
}
```

## 🚨 Sistema de Alertas

O sistema detecta automaticamente palavras que indicam necessidade de atenção médica:

- Sangramento
- Febre
- Dor
- Inchaço
- Tristeza
- Depressão
- Emergência

Quando detectadas, o sistema exibe alertas e oferece opções para contato médico.

## 🎨 Personalização

### Cores e Tema

Edite o arquivo `backend/static/css/style.css` para personalizar:

- Cores principais
- Gradientes
- Tipografia
- Animações

### Mensagens de Apoio

Modifique `dados/mensagens_apoio.json` para adicionar novas mensagens empáticas.

## 🔒 Segurança

- Chaves de API são carregadas de variáveis de ambiente
- Validação de entrada no backend
- Sanitização de mensagens
- Histórico local (não persistente)

## 🚀 Deploy

### Render.com (✅ RECOMENDADO - Já Configurado!)

O projeto está **totalmente configurado** para deploy automático no Render:

1. Acesse [https://render.com](https://render.com)
2. Conecte seu repositório GitHub
3. Render detectará automaticamente o `render.yaml`
4. Deploy automático iniciará em instantes!
5. URL: `https://assistente-puerperio.onrender.com`

**Variáveis de Ambiente (no Render):**
```env
OPENAI_API_KEY=sua_chave_openai (obrigatório)
USE_AI=true
PORT=5000 (automático)
```

Veja instruções completas em: **`README_DEPLOY.md`**

### Outras Opções de Deploy

- **Railway.app**: Conecte GitHub, deploy automático
- **Fly.io**: Instale CLI, `fly launch`
- **Heroku**: Usa Procfile (método antigo)
- **PythonAnywhere**: Upload manual

Veja mais detalhes em: **`DEPLOY.md`**

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:

1. Verifique a documentação
2. Consulte as issues existentes
3. Crie uma nova issue com detalhes do problema

## 🙏 Agradecimentos

- Comunidade Python/Flask
- OpenAI pela API
- Font Awesome pelos ícones
- Todas as mães que contribuíram com feedback

---

**⚠️ Aviso Importante**: Este chatbot é uma ferramenta de apoio e não substitui o acompanhamento médico profissional. Sempre consulte profissionais de saúde para questões médicas específicas.

