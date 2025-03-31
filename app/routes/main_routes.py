# app/routes/main_routes.py
"""
Rotas principais da aplicação.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from . import main_bp
from ..controllers import auth as auth_controller
from ..controllers import admin as admin_controller
from ..controllers import diretor as diretor_controller
from ..models import User, Unidade, Curso, Envolvido

@main_bp.route('/')
def index():
    """Página inicial do sistema"""
    # Se o usuário já estiver autenticado, redireciona para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard do sistema. 
    Redireciona para o dashboard específico com base no papel do usuário.
    """
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    
    if current_user.is_diretor():
        return redirect(url_for('diretor.dashboard'))
    
    # Se chegou aqui, o usuário não tem um papel reconhecido
    flash('Seu perfil de usuário não tem um dashboard associado.', 'warning')
    return redirect(url_for('auth.logout'))

@main_bp.route('/perfil')
@login_required
def perfil():
    """Exibe o perfil do usuário"""
    if current_user.is_diretor():
        return redirect(url_for('diretor.perfil'))
    
    # Para administradores, exibe informações básicas de perfil
    return render_template('admin/usuarios/perfil.html', user=current_user)

@main_bp.route('/sobre')
def sobre():
    """Página 'Sobre' do sistema"""
    return render_template('sobre.html')

@main_bp.route('/contato')
def contato():
    """Página de contato"""
    return render_template('contato.html')

@main_bp.route('/ajuda')
def ajuda():
    """Página de ajuda do sistema"""
    return render_template('ajuda.html')

@main_bp.route('/termos')
def termos():
    """Termos de uso do sistema"""
    return render_template('termos.html')

@main_bp.route('/privacidade')
def privacidade():
    """Política de privacidade"""
    return render_template('privacidade.html')

@main_bp.route('/not-found')
def not_found():
    """Página personalizada para erro 404"""
    return render_template('errors/404.html'), 404

@main_bp.route('/acesso-negado')
def acesso_negado():
    """Página personalizada para erro 403"""
    return render_template('errors/403.html'), 403

@main_bp.route('/erro-servidor')
def erro_servidor():
    """Página personalizada para erro 500"""
    return render_template('errors/500.html'), 500

@main_bp.errorhandler(404)
def page_not_found(e):
    """Manipulador de erro 404"""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(403)
def forbidden(e):
    """Manipulador de erro 403"""
    return render_template('errors/403.html'), 403

@main_bp.errorhandler(500)
def internal_server_error(e):
    """Manipulador de erro 500"""
    return render_template('errors/500.html'), 500

@main_bp.route('/admin')
@login_required
def admin_redirect():
    """Redireciona para o dashboard do administrador"""
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    flash('Você não tem permissão para acessar a área administrativa.', 'danger')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/diretor')
@login_required
def diretor_redirect():
    """Redireciona para o dashboard do diretor"""
    if current_user.is_diretor():
        return redirect(url_for('diretor.dashboard'))
    flash('Você não tem permissão para acessar a área de diretor.', 'danger')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/test-db')
def test_db_connection():
    """Rota temporária para testar a conexão com o banco de dados"""
    try:
        # Tentativa de consulta simples
        from ..models import User
        user_count = User.query.count()
        return f"Conexão com o banco de dados bem-sucedida! Número de usuários: {user_count}"
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return f"Erro ao conectar com o banco de dados: {str(e)}<br><pre>{error_trace}</pre>", 500

def handle_error_404():
    """Manipulador personalizado para erro 404 (Página não encontrada)"""
    return render_template('errors/404.html'), 404

def handle_error_403():
    """Manipulador personalizado para erro 403 (Acesso proibido)"""
    return render_template('errors/403.html'), 403

def handle_error_500(e):
    """Manipulador personalizado para erro 500 (Erro interno do servidor)"""
    return render_template('errors/500.html'), 500