# app/routes/cursos_routes.py
"""
Rotas para gerenciamento de cursos.
"""

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from . import cursos_bp
from ..utils.decorators import admin_required, diretor_required
from ..controllers import cursos as cursos_controller
from ..models import db, Curso, Unidade, Envolvido

@cursos_bp.route('/')
@login_required
def listar():
    """Lista todos os cursos (admin) ou apenas os cursos da unidade do diretor"""
    unidade_id = request.args.get('unidade_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('q', None)
    status = request.args.get('status', None)
    
    # Para diretores, força a visualização apenas da sua unidade
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    if unidade_id:
        # Verifica se a unidade existe
        unidade = Unidade.query.get_or_404(unidade_id)
        
        # Verifica permissão
        if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != unidade_id):
            flash('Você não tem permissão para visualizar cursos desta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Obtém os cursos da unidade com paginação
        pagination = cursos_controller.get_cursos_by_unidade_paginated(
            unidade_id, 
            page=page, 
            per_page=per_page,
            search=search,
            status=status
        )
        
        return render_template('cursos/listar.html', 
                              pagination=pagination, 
                              unidade=unidade,
                              search=search,
                              status=status)
    
    # Se não especificou unidade e é admin, mostra todos os cursos
    if current_user.is_admin():
        tipo_unidade = request.args.get('tipo_unidade', None)
        
        # Obtém os cursos com paginação
        pagination = cursos_controller.get_all_cursos_paginated(
            page=page, 
            per_page=per_page,
            search=search,
            status=status,
            tipo_unidade=tipo_unidade
        )
        
        unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
        
        return render_template('cursos/listar_todos.html', 
                              pagination=pagination,
                              unidades=unidades,
                              search=search,
                              status=status,
                              tipo_unidade=tipo_unidade)
    
    # Se chegou aqui é porque é diretor mas não tem unidade associada
    flash('Não foi possível encontrar sua unidade. Entre em contato com o administrador.', 'danger')
    return redirect(url_for('main.dashboard'))

@cursos_bp.route('/')
@login_required
def listar():
    """Lista todos os cursos (admin) ou apenas os cursos da unidade do diretor"""
    unidade_id = request.args.get('unidade_id', type=int)
    
    # Para diretores, força a visualização apenas da sua unidade
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    if unidade_id:
        # Verifica se a unidade existe
        unidade = Unidade.query.get_or_404(unidade_id)
        
        # Verifica permissão
        if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != unidade_id):
            flash('Você não tem permissão para visualizar cursos desta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Obtém os cursos da unidade
        cursos = cursos_controller.get_cursos_by_unidade(unidade_id)
        
        return render_template('cursos/listar.html', 
                              cursos=cursos, 
                              unidade=unidade)
    
    # Se não especificou unidade e é admin, mostra todos os cursos
    if current_user.is_admin():
        cursos = cursos_controller.get_all_cursos()
        unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
        
        return render_template('cursos/listar_todos.html', 
                              cursos=cursos,
                              unidades=unidades)
    
    # Se chegou aqui é porque é diretor mas não tem unidade associada
    flash('Não foi possível encontrar sua unidade. Entre em contato com o administrador.', 'danger')
    return redirect(url_for('main.dashboard'))

@cursos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cria um novo curso"""
    unidade_id = request.args.get('unidade_id', type=int)
    
    # Para diretores, força a unidade atual
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    # Verifica se a unidade existe e se o usuário tem acesso
    if unidade_id:
        unidade = Unidade.query.get_or_404(unidade_id)
        
        # Verifica permissão
        if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != unidade_id):
            flash('Você não tem permissão para adicionar cursos a esta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
    else:
        # Se não foi especificada uma unidade e o usuário é admin, mostra formulário com seleção
        if current_user.is_admin():
            unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
            return render_template('cursos/novo.html', unidades=unidades)
        else:
            flash('Unidade não especificada.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        codigo = request.form.get('codigo')
        descricao = request.form.get('descricao')
        
        # Se o usuário é admin, pode mudar a unidade
        if current_user.is_admin():
            unidade_id = request.form.get('unidade_id', type=int)
            if not unidade_id:
                flash('Selecione uma unidade.', 'danger')
                unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
                return render_template('cursos/novo.html', unidades=unidades)
            
            unidade = Unidade.query.get_or_404(unidade_id)
        
        # Validações básicas
        if not nome:
            flash('O nome do curso é obrigatório.', 'danger')
            return render_template('cursos/novo.html', unidade=unidade)
        
        # Cria o curso
        curso = cursos_controller.create_curso(
            nome=nome,
            unidade_id=unidade_id,
            codigo=codigo,
            descricao=descricao
        )
        
        if curso:
            flash(f'Curso "{curso.nome}" criado com sucesso!', 'success')
            return redirect(url_for('cursos.listar', unidade_id=unidade_id))
        else:
            flash('Erro ao criar curso. Verifique se já existe um curso com o mesmo nome na unidade.', 'danger')
    
    return render_template('cursos/novo.html', unidade=unidade)

@cursos_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualiza detalhes de um curso"""
    curso = Curso.query.get_or_404(id)
    
    # Verifica permissão
    if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != curso.unidade_id):
        flash('Você não tem permissão para visualizar este curso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtém a lista de orientadores associados ao curso
    orientadores = curso.orientadores
    
    return render_template('cursos/visualizar.html', 
                          curso=curso, 
                          orientadores=orientadores)

@cursos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita um curso existente"""
    curso = Curso.query.get_or_404(id)
    
    # Verifica permissão
    if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != curso.unidade_id):
        flash('Você não tem permissão para editar este curso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        codigo = request.form.get('codigo')
        descricao = request.form.get('descricao')
        ativo = 'ativo' in request.form
        
        # Validações básicas
        if not nome:
            flash('O nome do curso é obrigatório.', 'danger')
            return render_template('cursos/editar.html', curso=curso)
        
        # Atualiza o curso
        success = cursos_controller.update_curso(
            curso_id=id,
            nome=nome,
            codigo=codigo,
            descricao=descricao,
            ativo=ativo
        )
        
        if success:
            flash(f'Curso "{nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('cursos.visualizar', id=id))
        else:
            flash('Erro ao atualizar curso. Verifique se já existe outro curso com o mesmo nome na unidade.', 'danger')
    
    return render_template('cursos/editar.html', curso=curso)

@cursos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Exclui um curso"""
    curso = Curso.query.get_or_404(id)
    
    # Verifica permissão
    if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != curso.unidade_id):
        flash('Você não tem permissão para excluir este curso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    unidade_id = curso.unidade_id
    nome = curso.nome
    
    # Exclui o curso
    success = cursos_controller.delete_curso(id)
    
    if success:
        flash(f'Curso "{nome}" excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir curso.', 'danger')
    
    return redirect(url_for('cursos.listar', unidade_id=unidade_id))

@cursos_bp.route('/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(id):
    """Ativa ou desativa um curso"""
    curso = Curso.query.get_or_404(id)
    
    # Verifica permissão
    if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != curso.unidade_id):
        flash('Você não tem permissão para alterar o status deste curso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Altera o status
    success = cursos_controller.toggle_curso_status(id)
    
    if success:
        status = "ativado" if curso.ativo else "desativado"
        flash(f'Curso "{curso.nome}" {status} com sucesso!', 'success')
    else:
        flash('Erro ao alterar status do curso.', 'danger')
    
    return redirect(url_for('cursos.visualizar', id=id))
