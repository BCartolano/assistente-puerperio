#!/usr/bin/env python3
"""
Script para configurar email no arquivo .env
"""
import os
import sys

def criar_arquivo_env():
    """Cria ou atualiza o arquivo .env com configurações de email"""
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_example_path = os.path.join(os.path.dirname(__file__), 'env_example.txt')
    
    # Carrega configurações existentes se o arquivo já existe
    configs_existentes = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    configs_existentes[key.strip()] = value.strip()
    
    print("=" * 60)
    print("📧 CONFIGURAÇÃO DE EMAIL PARA VALIDAÇÃO DE CONTAS")
    print("=" * 60)
    print()
    
    # Solicita informações de email
    print("Escolha o provedor de email:")
    print("1. Gmail (recomendado)")
    print("2. Outlook/Hotmail")
    print("3. Yahoo Mail")
    print("4. Outro")
    
    opcao = input("\nEscolha uma opção (1-4): ").strip()
    
    if opcao == '1':
        mail_server = 'smtp.gmail.com'
        mail_port = '587'
        mail_use_tls = 'True'
        print("\n✅ Gmail selecionado")
        print("\n⚠️ IMPORTANTE: Para Gmail, você precisa:")
        print("   1. Ter Verificação em Duas Etapas ativada")
        print("   2. Ter gerado uma Senha de App")
        print("   (https://myaccount.google.com/apppasswords)")
        print()
    elif opcao == '2':
        mail_server = 'smtp-mail.outlook.com'
        mail_port = '587'
        mail_use_tls = 'True'
        print("\n✅ Outlook/Hotmail selecionado")
    elif opcao == '3':
        mail_server = 'smtp.mail.yahoo.com'
        mail_port = '587'
        mail_use_tls = 'True'
        print("\n✅ Yahoo Mail selecionado")
    elif opcao == '4':
        mail_server = input("Servidor SMTP (ex: smtp.exemplo.com): ").strip()
        mail_port = input("Porta SMTP (geralmente 587 ou 465): ").strip() or '587'
        mail_use_tls = input("Usar TLS? (True/False): ").strip() or 'True'
    else:
        print("❌ Opção inválida!")
        return False
    
    mail_username = input("\nEmail (ex: seu_email@gmail.com): ").strip()
    mail_password = input("Senha (ou Senha de App para Gmail): ").strip()
    mail_sender = input(f"Email remetente (Enter para usar {mail_username}): ").strip() or mail_username
    
    # Verifica se já existe arquivo .env
    if os.path.exists(env_path):
        resposta = input(f"\n⚠️ Arquivo .env já existe. Deseja atualizar apenas as configurações de email? (s/n): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("Operação cancelada.")
            return False
    
    # Lê conteúdo existente se houver
    linhas_existentes = []
    outras_configs = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith('#'):
                    if '=' in line_stripped:
                        key = line_stripped.split('=')[0].strip()
                        if key.startswith('MAIL_'):
                            continue  # Remove configurações antigas de email
                linhas_existentes.append(line.rstrip())
    
    # Se não existe, usa template
    if not os.path.exists(env_path) and os.path.exists(env_example_path):
        with open(env_example_path, 'r', encoding='utf-8') as f:
            linhas_existentes = f.read().splitlines()
    
    # Escreve novo arquivo .env
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            # Mantém configurações existentes que não são de email
            for line in linhas_existentes:
                if line.strip() and not line.strip().startswith('#') and '=' in line.strip():
                    key = line.strip().split('=')[0].strip()
                    if key.startswith('MAIL_'):
                        continue  # Pula configurações antigas
                f.write(line + '\n')
            
            # Adiciona seção de email
            f.write('\n# Configurações de Email (Configurado automaticamente)\n')
            f.write(f'MAIL_SERVER={mail_server}\n')
            f.write(f'MAIL_PORT={mail_port}\n')
            f.write(f'MAIL_USE_TLS={mail_use_tls}\n')
            f.write(f'MAIL_USERNAME={mail_username}\n')
            f.write(f'MAIL_PASSWORD={mail_password}\n')
            f.write(f'MAIL_DEFAULT_SENDER={mail_sender}\n')
        
        print("\n✅ Arquivo .env criado/atualizado com sucesso!")
        print(f"   📁 Localização: {os.path.abspath(env_path)}")
        print("\n⚠️ IMPORTANTE:")
        print("   1. Reinicie o servidor Flask para carregar as novas configurações")
        print("   2. Teste criando uma nova conta para verificar se o email é enviado")
        print("   3. Verifique a pasta de SPAM se não receber o email")
        print()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao criar arquivo .env: {e}")
        return False

def testar_configuracao():
    """Testa a configuração de email carregando do .env"""
    import os
    from dotenv import load_dotenv
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print("❌ Arquivo .env não encontrado!")
        return False
    
    load_dotenv(env_path)
    
    mail_username = os.getenv('MAIL_USERNAME', '')
    mail_password = os.getenv('MAIL_PASSWORD', '')
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = os.getenv('MAIL_PORT', '587')
    
    print("\n" + "=" * 60)
    print("🧪 TESTE DE CONFIGURAÇÃO DE EMAIL")
    print("=" * 60)
    print(f"Servidor: {mail_server}")
    print(f"Porta: {mail_port}")
    print(f"Username: {mail_username}")
    print(f"Password: {'✅ Configurado' if mail_password else '❌ Não configurado'}")
    print()
    
    if not mail_username or not mail_password:
        print("❌ Configuração incompleta!")
        print("   Configure MAIL_USERNAME e MAIL_PASSWORD no arquivo .env")
        return False
    
    print("✅ Configuração parece correta!")
    print("\nPara testar o envio real, crie uma nova conta no sistema.")
    print("Os logs do servidor mostrarão se o email foi enviado com sucesso.")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        testar_configuracao()
    else:
        criar_arquivo_env()
        print("\n" + "=" * 60)
        resposta = input("\nDeseja testar a configuração agora? (s/n): ").strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            testar_configuracao()

