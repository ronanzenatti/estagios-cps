# app/utils/decorators.py
"""
Decoradores personalizados para controle de acesso e outras funcionalidades.
"""

from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def admin_required(f):
    """
    Decorador para restringir acesso apenas a administradores.
    Deve ser usado após o decorador @login_required.
    
    Usage:
        @app.route('/admin')
        @login_required
        @admin_required
        def admin_dashboard():
            return render_template('admin/dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Acesso restrito. Você precisa ser administrador para acessar esta página.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def diretor_required(f):
    """
    Decorador para restringir acesso apenas a diretores.
    Deve ser usado após o decorador @login_required.
    
    Usage:
        @app.route('/diretor')
        @login_required
        @diretor_required
        def diretor_dashboard():
            return render_template('diretor/dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_diretor():
            flash('Acesso restrito. Você precisa ser diretor para acessar esta página.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def check_unidade_access(f):
    """
    Decorador para verificar se o usuário tem acesso à unidade especificada na URL.
    Espera que um parâmetro 'unidade_id' esteja presente na URL.
    Deve ser usado após o decorador @login_required.
    
    Usage:
        @app.route('/unidades/<int:unidade_id>/cursos')
        @login_required
        @check_unidade_access
        def listar_cursos(unidade_id):
            # ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        unidade_id = kwargs.get('unidade_id')
        if unidade_id is None:
            abort(400)  # Bad Request
        
        if current_user.is_admin():
            return f(*args, **kwargs)
        
        if current_user.is_diretor() and current_user.unidade_id == unidade_id:
            return f(*args, **kwargs)
        
        flash('Você não tem permissão para acessar esta unidade.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return decorated_function


def has_role(*roles):
    """
    Decorador para verificar se o usuário tem pelo menos um dos papéis especificados.
    Deve ser usado após o decorador @login_required.
    
    Usage:
        @app.route('/gerenciar')
        @login_required
        @has_role('admin', 'diretor')
        def gerenciar():
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for role in roles:
                if getattr(current_user, f'is_{role}')():
                    return f(*args, **kwargs)
            
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return decorated_function
    
    return decorator
