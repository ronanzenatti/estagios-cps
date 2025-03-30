# app/routes/unidades_routes.py
"""
Rotas para gerenciamento de unidades.
"""

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from . import unidades_bp
from ..utils.decorators import admin_required, check_unidade_access
from ..controllers import unidades as unidades_controller
from ..models import Unidade, User, Curso, Envolvido, db

@unidades_bp.route('/')
@login_required
def listar():
    """Lista todas as unidades (admin) ou apenas a unidade do diretor"""
    if current_user.is_admin():
        unidades = unidades_controller.get_all_unidades()
        return render_template('unidades/listar.html', unidades=unidades)
    
    # Se for diretor, redireciona para a página da sua unidade
    if current_user.is_diretor():
        return redirect(url_for('unidades.visualizar', id=current_user.unidade_id))
    
    abort(403)  # Acesso negado

@unidades_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo():
    """Cria uma nova unidade (apenas admin)"""
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        numero = request.form.get('numero')
        nome = request.form.get('nome')
        cidade = request.form.get('cidade')
        telefone = request.form.get('telefone')
        nome_diretor = request.form.get('nome_diretor')
        email_diretor = request.form.get('email_diretor')
        
        # Validações básicas
        if not all([tipo, numero, nome, cidade, telefone, nome_diretor, email_diretor]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('unidades/novo.html')
        
        # Cria a unidade
        unidade = unidades_controller.create_unidade(
            tipo=tipo,
            numero=numero,
            nome=nome,
            cidade=cidade,
            telefone=telefone,
            nome_diretor=nome_diretor,
            email_diretor=email_diretor
        )
        
        if unidade:
            flash(f'Unidade {unidade.nome} criada com sucesso!', 'success')
            return redirect(url_for('unidades.listar'))
        else:
            flash('Erro ao criar unidade. Verifique se já existe uma unidade com o mesmo tipo e número.', 'danger')
    
    return render_template('unidades/novo.html')

@unidades_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualiza detalhes de uma unidade"""
    unidade = Unidade.query.get_or_404(id)
    
    # Verifica permissão
    if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != id):
        flash('Você não tem permissão para visualizar esta unidade.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtém dados relacionados
    cursos = Curso.query.filter_by(unidade_id=id).order_by(Curso.nome).all()
    
    # Busca os envolvidos por tipo
    orientadores = Envolvido.query.filter_by(unidade_id=id, tipo='Orientador').all()
    coordenadores = Envolvido.query.filter_by(unidade_id=id, tipo='Coordenador').all()
    atas = Envolvido.query.filter_by(unidade_id=id, tipo='ATA').all()
    facilitadores = Envolvido.query.filter_by(unidade_id=id, tipo='Facilitador').all()
    apoio = Envolvido.query.filter_by(unidade_id=id, tipo='Apoio').all()
    
    return render_template('unidades/visualizar.html', 
                          unidade=unidade, 
                          cursos=cursos, 
                          orientadores=orientadores,
                          coordenadores=coordenadores,
                          atas=atas,
                          facilitadores=facilitadores,
                          apoio=apoio)

@unidades_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    """Edita uma unidade existente (apenas admin)"""
    unidade = Unidade.query.get_or_404(id)
    
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        numero = request.form.get('numero')
        nome = request.form.get('nome')
        cidade = request.form.get('cidade')
        telefone = request.form.get('telefone')
        nome_diretor = request.form.get('nome_diretor')
        email_diretor = request.form.get('email_diretor')
        
        # Validações básicas
        if not all([tipo, numero, nome, cidade, telefone, nome_diretor, email_diretor]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('unidades/editar.html', unidade=unidade)
        
        # Atualiza a unidade
        success = unidades_controller.update_unidade(
            unidade_id=id,
            tipo=tipo,
            numero=numero,
            nome=nome,
            cidade=cidade,
            telefone=telefone,
            nome_diretor=nome_diretor,
            email_diretor=email_diretor
        )
        
        if success:
            flash(f'Unidade {nome} atualizada com sucesso!', 'success')
            return redirect(url_for('unidades.visualizar', id=id))
        else:
            flash('Erro ao atualizar unidade. Verifique se já existe outra unidade com o mesmo tipo e número.', 'danger')
    
    return render_template('unidades/editar.html', unidade=unidade)

@unidades_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir(id):
    """Exclui uma unidade (apenas admin)"""
    unidade = Unidade.query.get_or_404(id)
    nome = unidade.nome
    
    success = unidades_controller.delete_unidade(id)
    
    if success:
        flash(f'Unidade {nome} excluída com sucesso!', 'success')
    else:
        flash('Erro ao excluir unidade.', 'danger')
    
    return redirect(url_for('unidades.listar'))

@unidades_bp.route('/por-tipo/<tipo>')
@login_required
@admin_required
def listar_por_tipo(tipo):
    """Lista unidades por tipo (Fatec ou Etec)"""
    if tipo not in ['Fatec', 'Etec']:
        abort(404)
    
    unidades = unidades_controller.get_unidades_by_tipo(tipo)
    return render_template('unidades/listar.html', 
                          unidades=unidades, 
                          filtro_tipo=tipo)

@unidades_bp.route('/por-cidade/<cidade>')
@login_required
@admin_required
def listar_por_cidade(cidade):
    """Lista unidades por cidade"""
    unidades = unidades_controller.get_unidades_by_cidade(cidade)
    
    if not unidades:
        flash(f'Nenhuma unidade encontrada na cidade {cidade}.', 'info')
        return redirect(url_for('unidades.listar'))
    
    return render_template('unidades/listar.html', 
                          unidades=unidades, 
                          filtro_cidade=cidade)
