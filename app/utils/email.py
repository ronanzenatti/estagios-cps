# app/utils/email.py
"""
Funções para envio de emails na aplicação.
Usa Flask-Mail para gerenciar o envio de emails.
"""

from flask import current_app, render_template
from flask_mail import Message
from threading import Thread


def enviar_email_async(app, msg):
    """
    Envia um email de forma assíncrona.
    
    Args:
        app: Aplicação Flask
        msg: Objeto de mensagem do Flask-Mail
    """
    with app.app_context():
        try:
            from app import mail  # Importação correta do objeto mail
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar email: {str(e)}")


def enviar_email(assunto, destinatarios, texto_corpo, html_corpo=None, remetente=None, anexos=None):
    """
    Configura e envia um email.
    
    Args:
        assunto (str): Assunto do email
        destinatarios (list): Lista de endereços de email dos destinatários
        texto_corpo (str): Corpo do email em texto simples
        html_corpo (str, optional): Corpo do email em HTML
        remetente (str, optional): Email do remetente (usa o padrão se não informado)
        anexos (list, optional): Lista de anexos no formato (nome_arquivo, tipo_mime, dados)
        
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    try:
        app = current_app._get_current_object()
        from app import mail
        
        if remetente is None:
            remetente = current_app.config['MAIL_DEFAULT_SENDER']
        
        msg = Message(
            subject=assunto,
            recipients=destinatarios,
            body=texto_corpo,
            html=html_corpo,
            sender=remetente
        )
        
        # Adiciona anexos, se houver
        if anexos:
            for nome_arquivo, tipo_mime, dados in anexos:
                msg.attach(
                    filename=nome_arquivo,
                    content_type=tipo_mime,
                    data=dados
                )
        
        # Envia o email em uma thread separada para não bloquear a requisição
        Thread(target=enviar_email_async, args=(app, msg)).start()
        return True
    
    except Exception as e:
        current_app.logger.error(f"Erro ao configurar email: {str(e)}")
        return False


def enviar_email_resetar_senha(user, token):
    """
    Envia um email com instruções para resetar a senha.
    
    Args:
        user (User): Objeto do usuário
        token (str): Token de resetar senha
        
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    from flask import url_for
    
    link_resetar = url_for('main.reset_password_confirm', token=token, _external=True)
    
    return enviar_email(
        assunto='[Estágio CPS] Recuperação de Senha',
        destinatarios=[user.email],
        texto_corpo=render_template('email/reset_password.txt', 
                                   user=user, 
                                   link_resetar=link_resetar),
        html_corpo=render_template('email/reset_password.html', 
                                  user=user, 
                                  link_resetar=link_resetar)
    )


def enviar_email_boas_vindas(user, senha_temporaria=None):
    """
    Envia um email de boas-vindas a um novo usuário.
    
    Args:
        user (User): Objeto do usuário
        senha_temporaria (str, optional): Senha temporária para o primeiro acesso
        
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    return enviar_email(
        assunto='[Estágio CPS] Bem-vindo ao Sistema de Gestão de Estágio',
        destinatarios=[user.email],
        texto_corpo=render_template('email/boas_vindas.txt', 
                                   user=user, 
                                   senha_temporaria=senha_temporaria),
        html_corpo=render_template('email/boas_vindas.html', 
                                  user=user, 
                                  senha_temporaria=senha_temporaria)
    )