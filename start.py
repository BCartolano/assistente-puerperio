#!/usr/bin/env python3
"""
Script de inicialização do Assistente Puerpério
"""
import os
import sys
import subprocess
import platform

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("ERRO: Python 3.8 ou superior é necessário!")
        print(f"Versão atual: {sys.version}")
        return False
    print(f"OK: Python {sys.version.split()[0]} detectado")
    return True

def activate_virtual_env():
    """Ativa o ambiente virtual se existir"""
    venv_path = os.path.join(os.path.dirname(__file__), "backend", "venv")
    
    if os.path.exists(venv_path):
        print("OK: Ambiente virtual encontrado")
        
        # Determina o script de ativação baseado no sistema operacional
        if platform.system() == "Windows":
            activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
            python_executable = os.path.join(venv_path, "Scripts", "python.exe")
        else:
            activate_script = os.path.join(venv_path, "bin", "activate")
            python_executable = os.path.join(venv_path, "bin", "python")
        
        if os.path.exists(python_executable):
            print("OK: Usando Python do ambiente virtual")
            # Atualiza o sys.executable para usar o Python do venv
            sys.executable = python_executable
            return True
        else:
            print("ERRO: Python não encontrado no ambiente virtual")
            return False
    else:
        print("AVISO: Ambiente virtual não encontrado")
        print("Recomendado: python -m venv backend/venv && backend/venv/Scripts/activate (Windows)")
        return False

def check_virtual_env():
    """Verifica se estamos em um ambiente virtual"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("OK: Ambiente virtual ativo")
        return True
    else:
        print("AVISO: Ambiente virtual não detectado")
        return activate_virtual_env()

def install_dependencies():
    """Instala as dependências necessárias"""
    print("\nInstalando dependências...")
    try:
        # Usa o requirements.txt do diretório raiz
        requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        print("OK: Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERRO: Erro ao instalar dependências: {e}")
        return False

def check_env_file():
    """Verifica se o arquivo .env existe"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    env_template_path = os.path.join(os.path.dirname(__file__), "env_example.txt")
    
    if os.path.exists(env_path):
        print("OK: Arquivo .env encontrado")
        return True
    else:
        print("AVISO: Arquivo .env não encontrado")
        if os.path.exists(env_template_path):
            print("Copiando env_example.txt para .env...")
            try:
                import shutil
                shutil.copy(env_template_path, env_path)
                print("OK: Arquivo .env criado! Edite-o com suas configurações.")
            except Exception as e:
                print(f"ERRO: Erro ao criar .env: {e}")
                return False
        else:
            print("AVISO: Arquivo env_example.txt não encontrado")
        return True

def start_server():
    """Inicia o servidor Flask"""
    print("\nIniciando o Assistente Puerperio...")
    print("=" * 50)
    
    # Adiciona o diretório backend ao Python path
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    try:
        # Importa e executa o app
        from app import app  # type: ignore  # noqa
        print("Assistente Puerperio iniciado com sucesso!")
        print("Acesse: http://localhost:5000")
        print("Interface responsiva disponivel")
        print("Dica: Pressione Ctrl+C para parar o servidor")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"ERRO: Erro ao importar o aplicativo: {e}")
        print("Verifique se todas as dependências estão instaladas.")
        return False
    except Exception as e:
        print(f"ERRO: Erro ao iniciar o servidor: {e}")
        return False

def main():
    """Função principal"""
    print("Assistente Puerperio - Inicializador")
    print("=" * 50)
    
    # Verificações
    if not check_python_version():
        sys.exit(1)
    
    check_virtual_env()
    
    # Pergunta se deve instalar dependências se o venv não estiver ativo
    venv_path = os.path.join(os.path.dirname(__file__), "backend", "venv")
    if not os.path.exists(venv_path):
        response = input("\nAmbiente virtual nao encontrado. Deseja instalar as dependencias automaticamente? (s/n): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            if not install_dependencies():
                sys.exit(1)
    elif not check_virtual_env():
        response = input("\nDeseja instalar as dependencias automaticamente? (s/n): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            if not install_dependencies():
                sys.exit(1)
    
    check_env_file()
    
    # Inicia o servidor
    start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAssistente Puerperio encerrado pelo usuario.")
        print("Obrigado por usar nosso sistema!")
    except Exception as e:
        print(f"\nERRO: Erro inesperado: {e}")
        sys.exit(1)

