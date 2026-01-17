# 🤱 Sophia - Sua Companheira no Puerpério

<div align="center">

![Sophia Logo](https://img.shields.io/badge/Sophia-IA%20Acolhedora-pink?style=for-the-badge&logo=heart)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask)
![Gemini API](https://img.shields.io/badge/Gemini-AI-orange?style=for-the-badge&logo=google)

**Dashboard de saúde materna com inteligência artificial acolhedora**

[Features](#-recursos-premium) • [Instalação](#-instalação) • [Compliance](#-compliance-médico) • [Tecnologias](#-tecnologias)

</div>

---

## 📋 Visão Geral

**Sophia - Sua Companheira no Puerpério** é uma plataforma digital completa desenvolvida para oferecer suporte emocional, informativo e educativo durante o período puerperal (pós-parto). A plataforma combina uma interface moderna com design **Glassmorphism**, inteligência artificial baseada na **API do Gemini (Google)**, e recursos premium de saúde materna.

### Características Principais

- 🤖 **IA Acolhedora (Sophia)**: Assistente virtual com personalidade empática, treinada especificamente para acolher mães no puerpério
- 📱 **Interface Responsiva**: Design premium adaptado para desktop e mobile com efeitos visuais modernos
- 🎯 **Recursos Premium**: Calendário de vacinação, timeline de cuidados, gerador de PDF e hub de mídia educativa
- 🔒 **Compliance Médico**: Conformidade rigorosa com a Lei do Ato Médico e diretrizes do CFM
- 💾 **Persistência Local**: Armazenamento de preferências e histórico usando LocalStorage

---

## 🛠 Tecnologias

### Backend
- **Python 3.10+**: Linguagem principal
- **Flask 2.0+**: Framework web minimalista e flexível
- **Google Generative AI (Gemini)**: Motor de IA para a assistente Sophia
- **Bcrypt**: Hash seguro de senhas
- **Flask-Mail**: Sistema de verificação de e-mail e recuperação de senha
- **SQLite**: Banco de dados para autenticação e persistência de usuários
- **NLTK (Natural Language Toolkit)**: Processamento de linguagem natural para análise de sentimento

### Frontend
- **HTML5 / CSS3**: Estrutura e estilização
- **JavaScript (ES6+)**: Interatividade e lógica de interface
- **Glassmorphism UI**: Design moderno com efeitos de vidro fosco
- **FontAwesome**: Biblioteca de ícones
- **LocalStorage API**: Persistência de dados do usuário no navegador

### Design System
- **Paleta de Cores**: Tons de rosa acolhedores (#f4a6a6, #e8b4b8, #d63384)
- **Tipografia**: Nunito (Google Fonts) para legibilidade e empatia
- **Layout**: Grid System responsivo com breakpoints para múltiplas resoluções
- **Efeitos Visuais**: Backdrop-filter blur, gradientes suaves, transições fluidas

---

## ✨ Recursos Premium

### 📅 Calendário de Vacinação

Calendário interativo do **Programa Nacional de Imunizações (PNI)** do Brasil, com visualização alternada entre:
- **Gestante/Puérpera**: Vacinas essenciais (dTpa, Hepatite B, Influenza)
- **Bebê (0-2 anos)**: Cronograma completo de vacinação infantil

**Características**:
- Tabelas responsivas com informações detalhadas
- Alertas de compliance médico integrados
- Interface Glassmorphism premium
- Atualização baseada em fontes oficiais (Ministério da Saúde)

### ⏱ Timeline de Cuidados

Linha do tempo interativa com marcos biológicos e cuidados preventivos organizados por:

1. **Gestação** (0-40 semanas)
   - Ícones semânticos por marco (fa-seedling, fa-heartbeat, fa-baby, fa-stethoscope)
   - Cuidados preventivos, exames recomendados, sintomas comuns
   - Alertas para sintomas críticos

2. **Parto** (fases)
   - Pré-parto, Trabalho de Parto, Nascimento
   - Sinais e cuidados específicos de cada fase

3. **Pós-Parto** (semanas críticas)
   - Recuperação física e emocional
   - Marcos de amamentação e adaptação
   - Suporte para saúde mental

**Características**:
- Stepper horizontal com scroll suave (iOS/Android)
- Navegação por semanas/fases com atualização dinâmica de conteúdo
- Widget "Minha Semana" na sidebar para acesso rápido
- Visual premium com ícones coloridos e gradientes

### 📄 Gerador de PDF de Saúde

Sistema completo de geração de documentos para impressão/salvamento:

- **Guia de Autoexame de Mama**: 6 passos ilustrados com checklist
- **Dicas de Amamentação**: Informações essenciais
- **Playlist de Vídeos Educativos**: Links para conteúdo oficial (Fiocruz, USP, Ministério da Saúde)
- **Aviso Legal**: Disclaimer de compliance médico

**Características**:
- Layout otimizado para impressão (`@media print`)
- Formatação profissional e legível
- Integração com `window.print()` do navegador
- Skeleton screen durante carregamento

### 🎬 Hub de Mídia Educativa

Player de vídeos integrado com:

- **Playlist Lateral**: Navegação entre vídeos sem fechar o modal
- **Fontes Confiáveis**: Conteúdo curado de Fiocruz, USP e Ministério da Saúde
- **Interface Elegante**: Design Glassmorphism com controles intuitivos
- **Responsivo**: Adaptado para desktop e mobile

### 🩺 Guia Visual de Autoexame

Carrossel interativo com 6 passos detalhados:

- Ilustrações de alta qualidade (placeholders)
- Checklists de verificação
- Dicas práticas de prevenção
- Navegação por setas e indicadores
- Integração com gerador de PDF

### 📱 Sidebar de Controle (ToggleBar)

Painel lateral expansível com:

- **Diário de Sintomas**: Acesso rápido ao chat com contexto de acolhimento
- **Biblioteca de Mídia**: Link direto para vídeos educativos
- **Rede de Apoio Local**: Campos para cadastro de contatos (Obstetra, Pediatra)
- **Botões de Emergência**: 
  - SAMU 192 com `tel:192` para chamada imediata
  - Botão "Ligar para Obstetra" com validação de telefone
  - Áreas de toque mínimas de 48x48px (acessibilidade mobile)
- **Widget "Minha Semana"**: Exibição da semana atual da gestação/puerpério
- **Atalhos Rápidos**: Links diretos para Calendário de Vacinas e Timeline

### 🏥 Localizador de Hospitais

Sistema inteligente de busca e localização de hospitais especializados em atendimento obstétrico/maternidade:

#### O que o Localizador Busca

- **Especialização**: Prioriza hospitais com capacidade para atendimento obstétrico (maternidade)
- **Filtragem de Segurança**: 
  - **Filtro Duplo Obrigatório**: Validação em duas camadas
    1. **Tipo de Estabelecimento**: Apenas hospitais reais (exclui UBS, UPAs, Clínicas, Postos de Saúde)
    2. **Infraestrutura**: Aceita hospitais gerais e hospitais com maternidade explícita; bloqueia hospitais especializados que não atendem parto (lista negra)
  - Exclui hospitais especializados sem atendimento obstétrico (ex: psiquiátricos, ortopedia)
  - Validação por tags OSM (`healthcare:speciality`, `healthcare`) e análise de nomes

#### Como Funciona

- **API**: Utiliza Overpass API (OpenStreetMap) para buscar estabelecimentos de saúde
- **Multi-Server**: Sistema de fallback automático entre múltiplos servidores Overpass para garantir disponibilidade
- **Busca por Localização**: Requisição de geolocalização do usuário (GPS) ou entrada manual de endereço
- **Raio de Busca**: Padrão de 50km, configurável
- **Priorização**: 
  - Hospitais com palavras-chave de maternidade/obstetrícia no nome (score maior)
  - Hospitais com confirmação explícita de atendimento obstétrico (tags OSM)
  - Ordenação final por distância (mais próximo primeiro)

#### O que Mostra nos Cards

Cada hospital exibe um card completo com:

- **Nome Completo do Hospital**
- **Endereço Detalhado**: 
  - Rua e número (quando disponível)
  - Bairro, Cidade e Estado
- **Telefone de Contato**: Para confirmação de plantão
- **Distância**: Em metros/quilômetros da localização do usuário
- **Identificação Público/Privado**: 
  - Tag "Provável SUS/Público" para: UBS, UPA, Municipal, Estadual, Federal, Santa Casa
  - Tag "Provável Privado" para demais
- **Badge de Ala de Maternidade**: Indicação visual quando o hospital possui maternidade confirmada
- **Aviso de Segurança**: Texto destacado em amarelo/laranja: *"Recomendamos ligar para confirmar se há plantão obstétrico disponível no momento"*
- **Ações Rápidas**:
  - **Botão "Ver no Mapa"**: Abre Google Maps com busca pelo nome + endereço completo (evita erros de coordenadas)
  - **Botão "Ligar"**: Destaque especial com `tel:` para chamada direta
  - **Botão "Copiar Endereço"**: Copia endereço completo para área de transferência

#### Dados Exibidos

- Apenas hospitais com **dados completos**: Nome, endereço, telefone e coordenadas válidas
- Remoção automática de duplicatas
- Filtragem de qualidade para garantir informações confiáveis

### 🩺 Conteúdos Educativos sobre Câncer de Mama e Doação de Leite

Cards interativos no dashboard com recursos educativos oficiais:

#### 1. Saúde Preventiva - Câncer de Mama

- **Card no Dashboard**: Visual com ícone SVG e descrição
- **Link Oficial**: Redirecionamento para página do Ministério da Saúde sobre câncer de mama
- **Guia Visual de Autoexame de Mama**: 
  - Carrossel interativo com 6 passos detalhados
  - Instruções ilustradas para observação e palpação
  - Checklists de verificação por etapa
  - Dicas práticas de prevenção
  - **Geração de PDF**: Botão "Salvar Resumo de Saúde" para imprimir/salvar o guia completo
  - **Cláusula Ética**: Avisos de que o autoexame não substitui consulta médica e mamografia
- **Conteúdo Educacional**: Informações baseadas em diretrizes do Ministério da Saúde

#### 2. Rede de Apoio - Doação de Leite

- **Card no Dashboard**: Visual com ícone SVG e descrição
- **Link Oficial**: Redirecionamento para Rede Brasileira de Bancos de Leite Humano (Fiocruz)
- **Informações sobre Doação**:
  - Importância da doação de leite humano
  - Benefícios para bebês prematuros e de baixo peso
  - Requisitos para ser doadora
  - Processo de doação
  - Contribuição para saúde pública
- **Conteúdo Baseado em Evidências**: Referências da Fiocruz e Ministério da Saúde

**Localização**: Ambos os cards aparecem no carrossel de conteúdos educativos da tela principal do dashboard.

### ⚠️ Sinais de Alerta (Triagem de Sintomas)

Sistema inteligente de detecção e triagem de sintomas do puerpério que o usuário está sentindo:

#### Como Funciona

- **Detecção Automática**: Analisa mensagens do usuário durante a conversa com a Sophia
- **Palavras-chave Críticas**: Sistema identifica menções a sintomas relacionados ao puerpério
- **Contexto Inteligente**: Filtra falsos positivos usando análise de contexto (ex: "criador" não aciona alerta, mas "estou com sangramento" sim)

#### Sintomas Monitorados

##### Criticidade CRÍTICA (Atendimento Imediato - Vá ao Hospital AGORA)

1. **Dor de cabeça forte** - Possível pré-eclâmpsia pós-parto
2. **Visão embaçada ou pontos brilhantes** - Pré-eclâmpsia
3. **Dor abdominal intensa** - Infecção ou hemorragia interna
4. **Sangramento excessivo** (>1 absorvente por hora) - Hemorragia pós-parto
5. **Febre alta** (>38°C) - Infecção (endometrite, infecção cirúrgica)
6. **Dificuldade para respirar** - Possível embolia pulmonar
7. **Dor no peito** - Problemas cardíacos ou embolia

**Ações Automáticas**: Redirecionamento para "Hospitais Próximos" com prioridade SUS/Maternidade + Botão "Ligar SAMU (192)"

##### Criticidade MÉDIA (Procure Atendimento Médico)

1. **Inchaço no rosto ou mãos** - Possível pré-eclâmpsia
2. **Dor intensa no períneo** - Infecção ou hematoma
3. **Secreção com mau cheiro** - Infecção vaginal
4. **Mama vermelha, quente e dolorida** - Mastite
5. **Tristeza ou ansiedade intensa** - Baby blues ou depressão pós-parto

**Ações Automáticas**: Redirecionamento para "Hospitais Próximos" ou "Ligar CVV (188)" (para saúde mental)

##### Criticidade BAIXA (Monitore em Casa)

- **Cansaço extremo** - Comum no puerpério, orientação de autocuidado

#### Recursos da Triagem

- **Categorização**: Sintomas organizados por categoria (Pré-eclâmpsia, Infecção, Hemorragia, Saúde Mental, etc.)
- **Descrições Educativas**: Explicação sobre cada sintoma e sua possível causa
- **Ações Recomendadas**: Botões de ação rápida baseados na gravidade
- **Integração com Localizador**: Redirecionamento automático para hospitais próximos quando necessário
- **Sistema de Alertas**: Interface visual destacada para sintomas críticos

#### Fonte de Dados

Baseado no arquivo `backend/static/data/sintomas_puerperio.json` com 13 sintomas catalogados, suas gravidades e ações recomendadas, seguindo diretrizes médicas oficiais.

---

## ⚖️ Compliance Médico

O projeto **Sophia - Sua Companheira no Puerpério** está rigorosamente alinhado com as diretrizes éticas e legais brasileiras para software de saúde:

### Conformidade Legal

- ✅ **Lei do Ato Médico (Lei 12.842/2013)**: O sistema não realiza diagnóstico, prescrição ou tratamento médico
- ✅ **Código de Ética Médica (CFM)**: Respeita os limites de atuação de software informativo
- ✅ **ANVISA RDC 657/2022**: Conformidade com regulamentações de software médico (se aplicável)

### Princípios de Compliance Implementados

1. **Proibição de Diagnóstico**
   - Sophia nunca diagnostica doenças ou condições
   - Todas as respostas são informativas e educacionais
   - Linguagem reforçada: "Este conteúdo é informativo e não substitui consulta médica"

2. **Cláusulas de Barreira para Emergências**
   - Alertas imediatos para sintomas críticos (sangramento intenso, febre alta, dor severa)
   - Redirecionamento automático para SAMU 192
   - Mensagens claras: "Procure atendimento médico imediato"

3. **Fontes Oficiais**
   - Todo conteúdo médico é referenciado (Ministério da Saúde, Fiocruz, FEBRASGO)
   - Informações baseadas em guidelines oficiais
   - Atualização periódica de dados

4. **Evitação de Exercício Ilegal da Medicina**
   - Linguagem cuidadosa: "Apoio Informativo" ou "Educação em Saúde"
   - Nenhuma promessa de cura ou garantia de saúde
   - Disclaimers visíveis em todos os recursos críticos

5. **Transparência**
   - Rodapé permanente com informações de compliance
   - Nome oficial do projeto: "Sophia - Sua Companheira no Puerpério"
   - Referência explícita às normas éticas seguidas

### Rodapé de Compliance

O site inclui um rodapé permanente com:
- Nome oficial do projeto
- Declaração de natureza informativa
- Referência à Lei do Ato Médico e CFM
- Informações de emergência (SAMU 192)

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonar o repositório)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd chatbot-puerperio
   ```

2. **Crie um ambiente virtual (recomendado)**
   ```bash
   python -m venv backend/venv
   ```

3. **Ative o ambiente virtual**

   **Windows:**
   ```bash
   backend\venv\Scripts\activate
   ```

   **Linux/Mac:**
   ```bash
   source backend/venv/bin/activate
   ```

4. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

   **Nota importante**: Se você encontrar erros relacionados ao `bcrypt` ou outras dependências que requerem compilação:
   - **Windows**: Certifique-se de ter o Visual C++ Build Tools instalado
   - **Linux**: Instale `python3-dev` e `build-essential`
   - **Mac**: Instale Xcode Command Line Tools

5. **Configure as variáveis de ambiente**

   Copie o arquivo de exemplo:
   ```bash
   cp env_example.txt .env
   ```

   Edite o arquivo `.env` e configure:
   - `GEMINI_API_KEY`: Sua chave da API do Google Gemini
   - `AI_PROVIDER=gemini`: Define o provedor de IA
   - `USE_AI=true`: Habilita a IA
   - Configurações de e-mail (opcional, para recuperação de senha)

6. **Inicie o servidor**

   **Opção 1: Script PowerShell (Windows)**
   ```powershell
   .\iniciar-servidor.ps1
   ```

   **Opção 2: Script Batch (Windows)**
   ```batch
   python-start.bat
   ```

   **Opção 3: Python direto**
   ```bash
   python start.py
   ```

   **Opção 4: Flask direto**
   ```bash
   cd backend
   python app.py
   ```

7. **Acesse a aplicação**

   Abra seu navegador em: `http://localhost:5000`

### Troubleshooting

#### Erro: "No module named 'bcrypt'"
```bash
pip install bcrypt
```

#### Erro: "NLTK data not found"
O código baixa automaticamente os recursos necessários. Se persistir:
```python
import nltk
nltk.download('rslp')
nltk.download('punkt')
```

#### Erro: "GEMINI_API_KEY not found"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Confirme que a chave está correta e completa
- Certifique-se de que não há espaços extras na chave

#### Erro: "Port 5000 already in use"
- Altere a porta no arquivo `start.py` ou `backend/app.py`
- Ou encerre o processo que está usando a porta 5000

---

## 📁 Estrutura do Projeto

```
chatbot-puerperio/
├── backend/
│   ├── app.py                 # Aplicação Flask principal
│   ├── loader.py              # Carregamento de system prompt e persona
│   ├── check_login.py         # Funções de autenticação
│   ├── users.db               # Banco de dados SQLite (gerado automaticamente)
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Estilos Glassmorphism
│   │   ├── js/
│   │   │   └── chat.js        # Lógica de interface e interações
│   │   └── data/
│   │       ├── calendario_vacinacao.json
│   │       ├── timeline_cuidados.json
│   │       ├── guia_autoexame.json
│   │       └── videos_playlist.json
│   ├── system/
│   │   └── system_prompt.md   # Instruções da IA Sophia
│   └── templates/
│       └── index.html         # Interface principal
├── .env                       # Variáveis de ambiente (criar manualmente)
├── requirements.txt           # Dependências Python
├── start.py                   # Script de inicialização
├── README.md                  # Este arquivo
└── env_example.txt            # Exemplo de configuração
```

---

## 🎯 Uso

### Primeira Execução

1. Acesse `http://localhost:5000`
2. Crie uma conta ou faça login
3. Explore o dashboard e converse com a Sophia
4. Configure seus contatos de emergência na sidebar
5. Explore os recursos premium (Calendário, Timeline, Vídeos)

### Funcionalidades Principais

- **Chat com Sophia**: Converse naturalmente sobre cuidados no puerpério
- **Calendário de Vacinas**: Acompanhe vacinas para mãe e bebê
- **Timeline de Cuidados**: Navegue por semanas de gestação e pós-parto
- **Guia de Autoexame**: Aprenda os passos de prevenção ao câncer de mama
- **Vídeos Educativos**: Assista conteúdo curado de fontes confiáveis
- **Gerador de PDF**: Salve informações essenciais para consulta offline

---

## 🎨 Design e UX

### Glassmorphism

A interface utiliza o conceito de **Glassmorphism** (vidro fosco), caracterizado por:
- Efeitos de blur (`backdrop-filter: blur()`)
- Transparências sutis
- Bordas delicadas
- Sombras suaves para profundidade

### Responsividade

- **Desktop**: Layout amplo com grid de recursos
- **Tablet**: Adaptação fluida de colunas
- **Mobile**: Interface otimizada com áreas de toque de 48x48px
- **Ultrawide**: Containers com `max-width` inteligente

### Acessibilidade

- Áreas de toque mínimas (48x48px) em botões críticos
- Contrastes adequados para leitura
- Navegação por teclado
- Labels ARIA para leitores de tela

---

## 🔒 Segurança

- **Senhas**: Hash com bcrypt (sal automático)
- **Sessões**: Gerenciamento seguro com Flask
- **SQL Injection**: Prevenção com queries parametrizadas
- **XSS**: Sanitização de entrada HTML
- **HTTPS**: Recomendado para produção (use um proxy reverso como Nginx)

---

## 📊 Tecnologias de IA

### Google Gemini API

A Sophia utiliza a **API do Gemini (Google Generative AI)** para gerar respostas contextuais e empáticas. O sistema inclui:

- **System Instruction**: Prompt detalhado definindo a personalidade e limites da Sophia
- **Contexto de Conversa**: Histórico de mensagens para continuidade
- **Fallback de Erros**: Tratamento robusto de falhas de API
- **Rate Limiting**: Gerenciamento de limites de uso

### Personalidade da Sophia

A IA é configurada para:
- Ser empática e acolhedora
- Fornecer informações educacionais (nunca diagnóstico)
- Orientar para fontes oficiais
- Alertar para emergências médicas
- Conhecer todos os recursos da plataforma

---

## 🌟 Recursos Futuros (Roadmap)

- [ ] Integração com APIs de agendamento médico
- [ ] Suporte a múltiplos idiomas
- [ ] Modo offline completo
- [ ] App mobile nativo (React Native)
- [ ] Dashboard de estatísticas de uso
- [ ] Integração com wearables (monitoramento de saúde)
- [ ] Comunidade de apoio (fórum)

---

## 📝 Licença

Este projeto foi desenvolvido como portfólio técnico e social. Consulte o arquivo `LICENSE` para mais detalhes.

---

## 👥 Contribuindo

Este é um projeto de portfólio. Sugestões e feedbacks são bem-vindos através de issues ou pull requests.

---

## 📧 Contato

Para questões sobre o projeto, abra uma issue no repositório.

---

## 🙏 Agradecimentos

- **Ministério da Saúde do Brasil**: Dados oficiais de vacinação e cuidados
- **Fiocruz e USP**: Conteúdo educativo de referência
- **FEBRASGO**: Diretrizes de cuidado materno-infantil
- **Google Gemini**: Tecnologia de IA generativa

---

<div align="center">

**Desenvolvido com ❤️ para mães no puerpério**

*"Sua jornada materna, nosso apoio constante."*

</div>
