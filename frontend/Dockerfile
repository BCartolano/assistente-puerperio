FROM node:18-alpine

WORKDIR /app

# Copiar package files
COPY frontend/package*.json ./

# Instalar dependências
RUN npm install

# Copiar código do frontend
COPY frontend/ ./

# Expor porta
EXPOSE 3000

# Comando padrão (pode ser sobrescrito no docker-compose)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
