# app/routes/diretor_routes.py
"""
Rotas específicas para diretores de unidades.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from . import diretor_bp
from ..utils.decorators import diretor_required
from ..controllers import diretor as diretor_controller
from ..models import Unidade, Curso, Envolvido, db

@diretor_bp.route('/dashboard')
@login_required
@diretor_required
def dashboard():
    """Dashboard do diretor"""
    # Obtém a unidade do diretor
    unidade = diretor_controller.get_unidade_by_diretor(current_user.id)
    if not unidade:
        flash('Não foi possível encontrar sua unidade. Entre em contato com o administrador.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Obtém estatísticas da unidade
    stats = diretor_controller.get_diretor_statistics(unidade.id)
    
    return render_template('diretor/dashboard.html', unidade=unidade, stats=stats)

@diretor_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@diretor_required
def perfil():
    """Visualiza e edita o perfil do diretor"""
    unidade = diretor_controller.get_unidade_by_diretor(current_user.id)
    if not unidade:
        flash('Não foi possível encontrar sua unidade. Entre em contato com o administrador.', 'danger')
        return redirect(url_for('auth.logout'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        
        if nome:
            # Atualiza as informações do diretor
            success = diretor_controller.update_diretor_info(unidade.id, nome, telefone)
            
            if success:
                flash('Informações atualizadas com sucesso!', 'success')
                return redirect(url_for('diretor.perfil'))
            else:
                flash('Erro ao atualizar informações.', 'danger')
    
    return render_template('diretor/perfil.html', unidade=unidade, user=current_user)

@diretor_bp.route('/reports/envolvidos')
@login_required
@diretor_required
def relatorio_envolvidos():
    """Relatório de envolvidos da unidade"""
    unidade = diretor_controller.get_unidade_by_diretor(current_user.id)
    if not unidade:
        flash('Não foi possível encontrar sua unidade. Entre em contato com o administrador.', 'danger')
        return redirect(url_for('diretor.dashboard'))
    
    # Obtém os envolvidos da unidade
    orientadores = Envolvido.query.filter_by(unidade_id=unidade.id, tipo='Orientador').all()
    facilitadores = Envolvido.query.filter_by(unidade_id=unidade.id, tipo='Facilitador').all()
    
    return render_template('diretor/reports/envolvidos.html', 
                          unidade=unidade, 
                          orientadores=orientadores, 
                          facilitadores=facilitadores)

@diretor_bp.route('/reports/cursos')
@login_required
@diretor_required
def relatorio_cursos():
    """Relatório de cursos da unidade"""
    unidade = diretor_controller.get_unidade_by_diretor(current_user.id)
    if not unidade:
        flash('Não foi possível encontrar sua unidade. Entre em contato com o administrador.', 'danger')
        return redirect(url_for('diretor.dashboard'))
    
    # Obtém os cursos da unidade
    cursos = Curso.query.filter_by(unidade_id=unidade.id).order_by(Curso.nome).all()
    
    # Para cada curso, obtém os orientadores associados
    cursos_orientadores = []
    for curso in cursos:
        orientadores = curso.orientadores
        cursos_orientadores.append((curso, orientadores))
    
    return render_template('diretor/reports/cursos.html', 
                          unidade=unidade, 
                          cursos_orientadores=cursos_orientadores)

@diretor_bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
@diretor_required
def alterar_senha():
    """Permite que o diretor altere sua senha"""
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if not all([senha_atual, nova_senha, confirmar_senha]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('diretor/alterar_senha.html')
        
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('diretor/alterar_senha.html')
        
        # Verifica se a senha atual está correta
        if not current_user.check_password(senha_atual):
            flash('Senha atual incorreta.', 'danger')
            return render_template('diretor/alterar_senha.html')
        
        # Atualiza a senha
        current_user.set_password(nova_senha)
        db.session.commit()
        
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('diretor.perfil'))
    
    return render_template('diretor/alterar_senha.html')
