"""
Script de teste para verificar se o envio de email está funcionando.

Uso:
    python test_email.py

Certifique-se de ter no arquivo .env:
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=cartolanobruno32@gmail.com
MAIL_PASSWORD=sua_senha_de_app_aqui
"""

from flask import Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

app = Flask(__name__)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Verifica se as configurações foram carregadas
print("\n" + "="*60)
print("CONFIGURAÇÕES CARREGADAS:")
print("="*60)
print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME'] or '(NÃO CONFIGURADO)'}")
print(f"MAIL_PASSWORD: {'***' if app.config['MAIL_PASSWORD'] else '(NÃO CONFIGURADO)'}")
print("="*60 + "\n")

if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
    print("ERRO: MAIL_USERNAME ou MAIL_PASSWORD nao estao configurados!")
    print("\nConfigure no arquivo .env:")
    print("MAIL_USERNAME=cartolanobruno32@gmail.com")
    print("MAIL_PASSWORD=sua_senha_de_app_aqui")
    exit(1)

mail = Mail(app)

print("Enviando email de teste...\n")

try:
    with app.app_context():
        msg = Message(
            subject="Teste de envio – Sophia",
            sender=app.config['MAIL_USERNAME'],
            recipients=["cartolanobruno32@gmail.com"],
            body="Ola Bruno! Este e um e-mail de teste da Sophia. Tudo funcionando!"
        )
        mail.send(msg)
        print("OK - E-mail enviado com sucesso!")
        print("\nVerifique a caixa de entrada de: cartolanobruno32@gmail.com")
        print("   (Nao esqueca de verificar a pasta de spam/lixo eletronico)")
        
except Exception as e:
    error_msg = str(e)
    print(f"\nERRO ao enviar email: {error_msg}\n")
    
    # Mensagens de erro específicas
    if "authentication failed" in error_msg.lower() or "535" in error_msg or "535-5.7.8" in error_msg:
        print("AVISO: Erro de autenticacao!")
        print("   - Verifique se o email e senha estao corretos")
        if "@gmail.com" in str(app.config['MAIL_USERNAME']).lower():
            print("   - IMPORTANTE: Para Gmail, use SENHA DE APP (nao a senha normal)")
            print("     1. Ative Verificacao em Duas Etapas: https://myaccount.google.com/security")
            print("     2. Gere Senha de App: https://myaccount.google.com/apppasswords")
            print("     3. Use essa senha no MAIL_PASSWORD do arquivo .env")
    elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
        print("AVISO: Erro de conexao!")
        print(f"   - Verifique se o servidor SMTP esta correto: {app.config['MAIL_SERVER']}")
        print(f"   - Verifique se a porta esta correta: {app.config['MAIL_PORT']}")
    elif "ssl" in error_msg.lower() or "tls" in error_msg.lower():
        print("AVISO: Erro de SSL/TLS!")
        print("   - Tente mudar MAIL_USE_TLS para False e usar porta 465")
    
    import traceback
    traceback.print_exc()
    exit(1)

