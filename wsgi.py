"""
WSGI entry point for the chatbot application

Este arquivo é usado pelo Gunicorn para servir a aplicação Flask.
O Gunicorn não precisa ser importado aqui - ele é executado via linha de comando:
    gunicorn wsgi:app

O Gunicorn está listado em requirements.txt e será instalado automaticamente.
"""
import os
import sys
import traceback

# Obter o caminho absoluto do backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')

# Adiciona backend ao Python path
sys.path.insert(0, backend_path)

# Importa o app do backend
try:
    print("=" * 50)
    print("🚀 Iniciando aplicação Flask...")
    print(f"📁 Diretório atual: {current_dir}")
    print(f"📁 Backend path: {backend_path}")
    print(f"🐍 Python path: {sys.path[:3]}")
    print("=" * 50)
    
    from app import app  # pyright: ignore[reportMissingImports]  # noqa: F401
    print("✅ App Flask carregado com sucesso")
    print("=" * 50)
except Exception as e:
    print("=" * 50)
    print("❌ ERRO CRÍTICO ao carregar app:")
    print(f"❌ {str(e)}")
    print("=" * 50)
    print("📋 Traceback completo:")
    traceback.print_exc()
    print("=" * 50)
    raise

if __name__ == "__main__":
    # Para desenvolvimento local (não usa gunicorn)
    app.run(debug=True, host='0.0.0.0', port=5000)

