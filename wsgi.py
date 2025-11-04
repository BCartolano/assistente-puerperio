"""
WSGI entry point for the chatbot application

Este arquivo é usado pelo Gunicorn para servir a aplicação Flask.
O Gunicorn não precisa ser importado aqui - ele é executado via linha de comando:
    gunicorn wsgi:app

O Gunicorn está listado em requirements.txt e será instalado automaticamente.
"""
import os
import sys

# Obter o caminho absoluto do backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')

# Adiciona backend ao Python path
sys.path.insert(0, backend_path)

# Importa o app do backend
try:
    from app import app  # pyright: ignore[reportMissingImports]  # noqa: F401
    print("✅ App Flask carregado com sucesso")
except Exception as e:
    print(f"❌ Erro ao carregar app: {e}")
    raise

if __name__ == "__main__":
    # Para desenvolvimento local (não usa gunicorn)
    app.run(debug=True, host='0.0.0.0', port=5000)

