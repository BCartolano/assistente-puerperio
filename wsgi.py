"""
WSGI entry point for the chatbot application
"""
import os
import sys

# Obter o caminho absoluto do backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')

# Adiciona backend ao Python path
sys.path.insert(0, backend_path)

# Importa o app do backend
from app import app

if __name__ == "__main__":
    app.run()

