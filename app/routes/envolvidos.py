# app/routes/envolvidos_routes.py
"""
Rotas para gerenciamento de envolvidos (orientadores e facilitadores).
"""

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from . import envolvidos_bp
from ..utils.decorators import admin_required, diretor_required, check_unidade_access
from ..controllers import envolvidos as envolvidos_controller
from ..models import db, Envolvido, Unidade, Curso

@envolvidos_bp.route('/')
@login_required
def listar():
    """Lista todos os envolvidos (admin) ou apenas os envolvidos da unidade do diretor"""
    unidade_id = request.args.get('unidade_id', type=int)
    tipo = request.args.get('tipo')
    
    # Para diretores, força a visualização apenas da sua unidade
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    if unidade_id:
        # Verifica se a unidade existe
        unidade = Unidade.query.get_or_404(unidade_id)
        
        # Verifica permissão
        if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != unidade_id):
            flash('Você não tem permissão para visualizar envolvidos desta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Obtém os envolvidos da unidade, filtrando por tipo se especificado
        envolvidos = envolvidos_controller.get_envolvidos_by_unidade(unidade_id, tipo)
        
        return render_template('envolvidos/listar.html', 
                              envolvidos=envolvidos, 
                              unidade=unidade,
                              tipo_filtro=tipo)
    
    # Se não especificou unidade e é admin, mostra todos os envolvidos
    if current_user.is_admin():
        envolvidos = envolvidos_controller.get_all_envolvidos()
        unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
        
        return render_template('envolvidos/listar_todos.html', 
                              envolvidos=envolvidos,
                              unidades=unidades)
    
    # Se chegou aqui é porque é diretor mas não tem unidade associada
    flash('Não foi possível encontrar sua unidade. Entre em contato com o administrador.', 'danger')
    return redirect(url_for('main.dashboard'))

@envolvidos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cria um novo envolvido"""
    unidade_id = request.args.get('unidade_id', type=int)
    
    # Para diretores, força a unidade atual
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    # Verifica se a unidade existe e se o usuário tem acesso
    if unidade_id:
        unidade = Unidade.query.get_or_404(unidade_id)
        
        # Verifica permissão
        if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != unidade_id):
            flash('Você não tem permissão para adicionar envolvidos a esta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Busca os cursos da unidade para associar a orientadores
        cursos = Curso.query.filter_by(unidade_id=unidade_id, ativo=True).all()
    else:
        # Se não foi especificada uma unidade e o usuário é admin, mostra formulário com seleção
        if current_user.is_admin():
            unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
            return render_template('envolvidos/novo.html', unidades=unidades)
        else:
            flash('Unidade não especificada.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        cargo = request.form.get('cargo')
        tipo = request.form.get('tipo')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        
        # Se o usuário é admin, pode mudar a unidade
        if current_user.is_admin():
            unidade_id = request.form.get('unidade_id', type=int)
            if not unidade_id:
                flash('Selecione uma unidade.', 'danger')
                unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
                return render_template('envolvidos/novo.html', unidades=unidades)
            
            # Recarrega a unidade e os cursos
            unidade = Unidade.query.get_or_404(unidade_id)
            cursos = Curso.query.filter_by(unidade_id=unidade_id, ativo=True).all()
        
        # Validações básicas
        if not all([nome, cpf, cargo, tipo]):
            flash('Nome, CPF, Cargo e Tipo são obrigatórios.', 'danger')
            return render_template('envolvidos/novo.html', unidade=unidade, cursos=cursos)
        
        # Para orientadores, deve selecionar ao menos um curso
        cursos_ids = request.form.getlist('cursos_ids', type=int)
        if tipo == 'Orientador' and not cursos_ids:
            flash('Orientadores devem estar associados a pelo menos um curso.', 'danger')
            return render_template('envolvidos/novo.html', unidade=unidade, cursos=cursos)
        
        # Cria o envolvido
        envolvido = envolvidos_controller.create_envolvido(
            nome=nome,
            cpf=cpf,
            cargo=cargo,
            tipo=tipo,
            unidade_id=unidade_id,
            cursos_ids=cursos_ids if tipo == 'Orientador' else None,
            telefone=telefone,
            email=email
        )
        
        if envolvido:
            flash(f'Envolvido "{envolvido.nome}" criado com sucesso!', 'success')
            return redirect(url_for('envolvidos.listar', unidade_id=unidade_id))
        else:
            flash('Erro ao criar envolvido. Verifique se o CPF já está cadastrado ou se é válido.', 'danger')
    
    return render_template('envolvidos/novo.html', unidade=unidade, cursos=cursos)

@envolvidos_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualiza detalhes de um envolvido"""
    envolvido = Envolvido.query.get_or_404(id)
    
    # Verifica permissão
    if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != envolvido.unidade_id):
        flash('Você não tem permissão para visualizar este envolvido.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('envolvidos/visualizar.html', envolvido=envolvido)

@envolvidos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita um envolvido existente"""
    envolvido = Envolvido.query.get_or_404(id)
    
    # Verifica permissão
    if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != envolvido.unidade_id):
        flash('Você não tem permissão para editar este envolvido.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Busca os cursos da unidade para associar a orientadores
    cursos = Curso.query.filter_by(unidade_id=envolvido.unidade_id).all()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        cargo = request.form.get('cargo')
        tipo = request.form.get('tipo')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        ativo = 'ativo' in request.form
        
        # Validações básicas
        if not all([nome, cpf, cargo, tipo]):
            flash('Nome, CPF, Cargo e Tipo são obrigatórios.', 'danger')
            return render_template('envolvidos/editar.html', envolvido=envolvido, cursos=cursos)
        
        # Para orientadores, deve selecionar ao menos um curso
        cursos_ids = request.form.getlist('cursos_ids', type=int)
        if tipo == 'Orientador' and not cursos_ids:
            flash('Orientadores devem estar associados a pelo menos um curso.', 'danger')
            return render_template('envolvidos/editar.html', envolvido=envolvido, cursos=cursos)
        
        # Atualiza o envolvido
        success = envolvidos_controller.update_envolvido(
            envolvido_id=id,
            nome=nome,
            cpf=cpf,
            cargo=cargo,
            tipo=tipo,
            cursos_ids=cursos_ids if tipo == 'Orientador' else None,
            telefone=telefone,
            email=email,
            ativo=ativo
        )
        
        if success:
            flash(f'Envolvido "{nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('envolvidos.visualizar', id=id))
        else:
            flash('Erro ao atualizar envolvido. Verifique se o CPF já está cadastrado ou se é válido.', 'danger')
    
    return render_template('envolvidos/editar.html', envolvido=envolvido, cursos=cursos)

@envolvidos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Exclui um envolvido"""
    envolvido = Envolvido.query.get_or_404(id)
    
    # Verifica permissão
    if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != envolvido.unidade_id):
        flash('Você não tem permissão para excluir este envolvido.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    unidade_id = envolvido.unidade_id
    nome = envolvido.nome
    
    # Exclui o envolvido
    success = envolvidos_controller.delete_envolvido(id)
    
    if success:
        flash(f'Envolvido "{nome}" excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir envolvido.', 'danger')
    
    return redirect(url_for('envolvidos.listar', unidade_id=unidade_id))

@envolvidos_bp.route('/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(id):
    """Ativa ou desativa um envolvido"""
    envolvido = Envolvido.query.get_or_404(id)
    
    # Verifica permissão
    if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != envolvido.unidade_id):
        flash('Você não tem permissão para alterar o status deste envolvido.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Altera o status
    success = envolvidos_controller.toggle_envolvido_status(id)
    
    if success:
        status = "ativado" if envolvido.ativo else "desativado"
        flash(f'Envolvido "{envolvido.nome}" {status} com sucesso!', 'success')
    else:
        flash('Erro ao alterar status do envolvido.', 'danger')
    
    return redirect(url_for('envolvidos.visualizar', id=id))

@envolvidos_bp.route('/por-tipo/<tipo>')
@login_required
def listar_por_tipo(tipo):
    """Lista envolvidos por tipo (Orientador ou Facilitador)"""
    if tipo not in ['Orientador', 'Facilitador']:
        abort(404)
    
    unidade_id = request.args.get('unidade_id', type=int)
    
    # Para diretores, força a visualização apenas da sua unidade
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
        
        # Obtém a unidade
        unidade = Unidade.query.get_or_404(unidade_id)
        
        # Obtém os envolvidos do tipo especificado na unidade
        envolvidos = envolvidos_controller.get_envolvidos_by_unidade(unidade_id, tipo)
        
        return render_template('envolvidos/listar.html', 
                              envolvidos=envolvidos, 
                              unidade=unidade, 
                              tipo_filtro=tipo)
    
    # Para administradores sem unidade especificada
    if current_user.is_admin() and not unidade_id:
        # Obtém todos os envolvidos do tipo especificado
        envolvidos = Envolvido.query.filter_by(tipo=tipo).order_by(Envolvido.nome).all()
        
        return render_template('envolvidos/listar_todos.html', 
                              envolvidos=envolvidos, 
                              tipo_filtro=tipo)
    
    # Para administradores com unidade especificada
    if current_user.is_admin() and unidade_id:
        # Verifica se a unidade existe
        unidade = Unidade.query.get_or_404(unidade_id)
        
        # Obtém os envolvidos do tipo especificado na unidade
        envolvidos = envolvidos_controller.get_envolvidos_by_unidade(unidade_id, tipo)
        
        return render_template('envolvidos/listar.html', 
                              envolvidos=envolvidos, 
                              unidade=unidade, 
                              tipo_filtro=tipo)
    
    abort(403)  # Acesso negado

@envolvidos_bp.route('/buscar-por-cpf')
@login_required
def buscar_por_cpf():
    """Busca um envolvido pelo CPF"""
    cpf = request.args.get('cpf')
    
    if not cpf:
        return render_template('envolvidos/buscar_cpf.html')
    
    # Formata o CPF para garantir consistência
    from ..models.envolvidos import Envolvido
    cpf_formatado = Envolvido.formatar_cpf(cpf)
    
    # Busca o envolvido
    envolvido = envolvidos_controller.get_envolvido_by_cpf(cpf_formatado)
    
    if envolvido:
        # Verifica permissão
        if not current_user.is_admin() and (not current_user.is_diretor() or current_user.unidade_id != envolvido.unidade_id):
            flash('Você não tem permissão para visualizar este envolvido.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return redirect(url_for('envolvidos.visualizar', id=envolvido.id))
    else:
        flash('Nenhum envolvido encontrado com este CPF.', 'info')
        return render_template('envolvidos/buscar_cpf.html', cpf=cpf)