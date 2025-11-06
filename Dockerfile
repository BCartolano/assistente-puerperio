# Usa imagem Python oficial com SQLite incluído
FROM python:3.11-slim

# Instala dependências do sistema necessárias
# SQLite precisa de libsqlite3-dev para compilar o módulo Python
RUN apt-get update && apt-get install -y \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de requisitos
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto da aplicação
COPY . .

# Expõe a porta (Railway usa porta dinâmica, mas definimos 8080 como padrão)
EXPOSE 8080

# Torna o script executável
RUN chmod +x start.sh

# Comando para iniciar a aplicação (Railway fornece PORT via variável de ambiente)
CMD ["/bin/bash", "start.sh"]
