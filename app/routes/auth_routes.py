# app/routes/auth_routes.py
"""
Rotas para autenticação de usuários.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime

from . import auth_bp
from ..controllers import auth as auth_controller
from ..models import User, db

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login no sistema"""
    # Redireciona se o usuário já estiver autenticado
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validação básica
        if not email or not password:
            flash('Por favor, preencha todos os campos.', 'warning')
            return render_template('auth/login.html')
        
        # Autentica o usuário
        user = auth_controller.authenticate_user(email, password)
        
        if user:
            login_user(user)
            
            # Redireciona para a página solicitada ou dashboard
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            
            flash(f'Bem-vindo, {user.nome or user.email}!', 'success')
            return redirect(next_page)
        
        flash('Email ou senha inválidos.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Rota para logout do sistema"""
    logout_user()
    flash('Você saiu do sistema com sucesso.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    """Rota para solicitar recuperação de senha"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if email:
            success = auth_controller.reset_password(email)
            # Mostra a mesma mensagem de sucesso independente se o email existe ou não
            # Isso evita vazamento de informação sobre emails cadastrados
            flash('Se esse email estiver registrado, você receberá instruções para redefinir sua senha.', 'info')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/recuperar_senha.html')

@auth_bp.route('/nova-senha/<token>', methods=['GET', 'POST'])
def nova_senha(token):
    """Rota para definir nova senha após solicitação de recuperação"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Em uma implementação real, verificaria o token
    # Para este exemplo, consideramos o token válido
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Por favor, preencha todos os campos.', 'warning')
            return render_template('auth/nova_senha.html', token=token)
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/nova_senha.html', token=token)
        
        # Em uma implementação real, definiria a nova senha do usuário associado ao token
        flash('Sua senha foi redefinida com sucesso! Agora você pode fazer login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/nova_senha.html', token=token)

@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Rota para o usuário autenticado alterar sua própria senha"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            flash('Por favor, preencha todos os campos.', 'warning')
            return render_template('auth/alterar_senha.html')
        
        if new_password != confirm_password:
            flash('As novas senhas não coincidem.', 'danger')
            return render_template('auth/alterar_senha.html')
        
        # Altera a senha
        success = auth_controller.change_password(current_user.id, current_password, new_password)
        
        if success:
            flash('Sua senha foi alterada com sucesso!', 'success')
            return redirect(url_for('auth.logout'))
        else:
            flash('Senha atual incorreta.', 'danger')
    
    return render_template('auth/alterar_senha.html')
