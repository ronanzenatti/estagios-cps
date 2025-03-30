# app/routes/admin_routes.py
"""
Rotas para área administrativa do sistema.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from . import admin_bp
from ..utils.decorators import admin_required
from ..controllers import admin as admin_controller
from ..controllers import auth as auth_controller
from ..models import User, Unidade, db

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard administrativo"""
    stats = admin_controller.get_statistics()
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/usuarios')
@login_required
@admin_required
def listar_usuarios():
    """Lista todos os usuários do sistema"""
    usuarios = User.query.order_by(User.role, User.email).all()
    return render_template('admin/usuarios/listar.html', usuarios=usuarios)

@admin_bp.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_usuario():
    """Cria um novo usuário administrador"""
    if request.method == 'POST':
        email = request.form.get('email')
        nome = request.form.get('nome')
        password = request.form.get('password')
        role = 'admin'  # Por esta rota, só é possível criar administradores
        
        if not email or not password:
            flash('Email e senha são obrigatórios.', 'danger')
            return render_template('admin/usuarios/novo.html')
        
        # Verifica se o email já está em uso
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Este email já está em uso.', 'danger')
            return render_template('admin/usuarios/novo.html')
        
        # Cria o novo usuário
        user = auth_controller.create_user(email, password, role, nome)
        
        if user:
            flash(f'Usuário {email} criado com sucesso!', 'success')
            return redirect(url_for('admin.listar_usuarios'))
        else:
            flash('Erro ao criar usuário.', 'danger')
    
    return render_template('admin/usuarios/novo.html')

@admin_bp.route('/usuarios/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_usuario(id):
    """Exclui um usuário"""
    # Não permite excluir o próprio usuário
    if id == current_user.id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('admin.listar_usuarios'))
    
    user = User.query.get_or_404(id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Usuário {user.email} excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir usuário: {str(e)}', 'danger')
    
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/usuarios/<int:id>/resetar-senha', methods=['POST'])
@login_required
@admin_required
def resetar_senha_usuario(id):
    """Reseta a senha de um usuário"""
    user = User.query.get_or_404(id)
    
    # Para diretores, define a senha como o número da unidade
    if user.is_diretor() and user.unidade_id:
        unidade = Unidade.query.get(user.unidade_id)
        if unidade:
            nova_senha = unidade.numero
            user.set_password(nova_senha)
            db.session.commit()
            flash(f'Senha do usuário {user.email} redefinida para o número da unidade.', 'success')
            return redirect(url_for('admin.listar_usuarios'))
    
    # Para outros usuários, gera uma senha aleatória
    success = auth_controller.reset_password(user.email)
    
    if success:
        flash(f'Um email com instruções para redefinir a senha foi enviado para {user.email}.', 'success')
    else:
        flash('Erro ao resetar senha.', 'danger')
    
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/unidades/resetar-todas-senhas', methods=['POST'])
@login_required
@admin_required
def resetar_todas_senhas_unidades():
    """Reseta as senhas de todos os diretores para o número de suas respectivas unidades"""
    
    # Busca todos os usuários que são diretores e que possuem unidade associada
    diretores = User.query.filter_by(role='diretor').filter(User.unidade_id.isnot(None)).all()
    
    count = 0
    for diretor in diretores:
        # Busca a unidade associada ao diretor
        unidade = Unidade.query.get(diretor.unidade_id)
        if unidade:
            # Define a senha como o número da unidade
            nova_senha = unidade.numero
            diretor.set_password(nova_senha)
            count += 1
    
    # Commit das alterações se houve alguma mudança
    if count > 0:
        try:
            db.session.commit()
            flash(f'Senhas de {count} diretores de unidades resetadas com sucesso para o número de suas respectivas unidades.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao resetar senhas: {str(e)}', 'danger')
    else:
        flash('Nenhum diretor com unidade associada foi encontrado.', 'info')
    
    return redirect(url_for('unidades.listar'))
