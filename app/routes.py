                return render_template('atividades/nova.html', unidades=unidades)
            
            unidade = Unidade.query.get_or_404(unidade_id)
            # Recarrega os envolvidos e cursos da unidade selecionada
            envolvidos = Envolvido.query.filter_by(unidade_id=unidade_id, ativo=True).order_by(Envolvido.nome).all()
            cursos = Curso.query.filter_by(unidade_id=unidade_id, ativo=True).order_by(Curso.nome).all()
        
        # Validações básicas
        if not all([descricao, data_inicio, status, envolvido_id]):
            flash('Os campos Descrição, Data de Início, Status e Envolvido são obrigatórios.', 'danger')
            return render_template('atividades/nova.html', 
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 envolvido_pre=envolvido_pre,
                                 cursos=cursos)
        
        if status not in ['Pendente', 'Em Andamento', 'Concluída', 'Cancelada']:
            flash('Status inválido.', 'danger')
            return render_template('atividades/nova.html', 
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 envolvido_pre=envolvido_pre,
                                 cursos=cursos)
        
        # Verifica se o envolvido pertence à unidade
        envolvido = Envolvido.query.get_or_404(envolvido_id)
        if envolvido.unidade_id != unidade_id:
            flash('O envolvido selecionado não pertence à unidade.', 'danger')
            return render_template('atividades/nova.html', 
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 envolvido_pre=envolvido_pre,
                                 cursos=cursos)
        
        # Verifica se o curso foi informado para orientadores
        if envolvido.is_orientador and not curso_id:
            flash('Para orientadores, é necessário selecionar um curso.', 'danger')
            return render_template('atividades/nova.html', 
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 envolvido_pre=envolvido,
                                 cursos=cursos)
        
        # Se um curso foi selecionado, verifica se pertence à unidade
        if curso_id:
            curso = Curso.query.get_or_404(curso_id)
            if curso.unidade_id != unidade_id:
                flash('O curso selecionado não pertence à unidade.', 'danger')
                return render_template('atividades/nova.html', 
                                     unidade=unidade, 
                                     envolvidos=envolvidos, 
                                     envolvido_pre=envolvido,
                                     cursos=cursos)
            
            # Para orientadores, verifica se o curso está associado ao envolvido
            if envolvido.is_orientador and curso not in envolvido.cursos:
                flash('O orientador selecionado não está associado ao curso escolhido.', 'danger')
                return render_template('atividades/nova.html', 
                                     unidade=unidade, 
                                     envolvidos=envolvidos, 
                                     envolvido_pre=envolvido,
                                     cursos=cursos)
        
        # Converte as datas
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            if data_fim:
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                if data_fim < data_inicio:
                    flash('A data de fim deve ser posterior à data de início.', 'danger')
                    return render_template('atividades/nova.html', 
                                         unidade=unidade, 
                                         envolvidos=envolvidos, 
                                         envolvido_pre=envolvido,
                                         cursos=cursos)
        except ValueError:
            flash('Formato de data inválido.', 'danger')
            return render_template('atividades/nova.html', 
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 envolvido_pre=envolvido,
                                 cursos=cursos)
        
        # Cria a nova atividade
        atividade = AtividadeEstagio(
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            observacoes=observacoes,
            unidade_id=unidade_id,
            envolvido_id=envolvido_id,
            curso_id=curso_id,
            criado_por=current_user.id
        )
        
        db.session.add(atividade)
        db.session.commit()
        
        flash('Atividade de estágio criada com sucesso!', 'success')
        return redirect(url_for('main.listar_atividades', unidade_id=unidade_id))
    
    return render_template('atividades/nova.html', 
                         unidade=unidade, 
                         envolvidos=envolvidos, 
                         envolvido_pre=envolvido_pre,
                         cursos=cursos)

@main.route('/atividades/<int:id>')
@login_required
def visualizar_atividade(id):
    """Visualiza detalhes de uma atividade"""
    atividade = AtividadeEstagio.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(atividade.unidade_id):
        flash('Você não tem permissão para acessar esta atividade.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtém o usuário que criou a atividade
    criador = User.query.get(atividade.criado_por)
    
    return render_template('atividades/visualizar.html', 
                         atividade=atividade,
                         criador=criador)

@main.route('/atividades/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_atividade(id):
    """Edita uma atividade existente"""
    atividade = AtividadeEstagio.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(atividade.unidade_id):
        flash('Você não tem permissão para editar esta atividade.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtém a unidade e o envolvido
    unidade = Unidade.query.get_or_404(atividade.unidade_id)
    envolvido = Envolvido.query.get_or_404(atividade.envolvido_id)
    
    # Obtém a lista de envolvidos da unidade
    envolvidos = Envolvido.query.filter_by(unidade_id=unidade.id, ativo=True).order_by(Envolvido.nome).all()
    
    # Obtém os cursos da unidade
    cursos = Curso.query.filter_by(unidade_id=unidade.id, ativo=True).order_by(Curso.nome).all()
    
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim') or None
        status = request.form.get('status')
        observacoes = request.form.get('observacoes')
        envolvido_id = request.form.get('envolvido_id', type=int)
        curso_id = request.form.get('curso_id', type=int) or None
        
        # Validações básicas
        if not all([descricao, data_inicio, status, envolvido_id]):
            flash('Os campos Descrição, Data de Início, Status e Envolvido são obrigatórios.', 'danger')
            return render_template('atividades/editar.html', 
                                 atividade=atividade,
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 cursos=cursos)
        
        if status not in ['Pendente', 'Em Andamento', 'Concluída', 'Cancelada']:
            flash('Status inválido.', 'danger')
            return render_template('atividades/editar.html', 
                                 atividade=atividade,
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 cursos=cursos)
        
        # Verifica se o envolvido pertence à unidade
        envolvido = Envolvido.query.get_or_404(envolvido_id)
        if envolvido.unidade_id != unidade.id:
            flash('O envolvido selecionado não pertence à unidade.', 'danger')
            return render_template('atividades/editar.html', 
                                 atividade=atividade,
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 cursos=cursos)
        
        # Verifica se o curso foi informado para orientadores
        if envolvido.is_orientador and not curso_id:
            flash('Para orientadores, é necessário selecionar um curso.', 'danger')
            return render_template('atividades/editar.html', 
                                 atividade=atividade,
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 cursos=cursos)
        
        # Se um curso foi selecionado, verifica se pertence à unidade
        if curso_id:
            curso = Curso.query.get_or_404(curso_id)
            if curso.unidade_id != unidade.id:
                flash('O curso selecionado não pertence à unidade.', 'danger')
                return render_template('atividades/editar.html', 
                                     atividade=atividade,
                                     unidade=unidade, 
                                     envolvidos=envolvidos, 
                                     cursos=cursos)
            
            # Para orientadores, verifica se o curso está associado ao envolvido
            if envolvido.is_orientador and curso not in envolvido.cursos:
                flash('O orientador selecionado não está associado ao curso escolhido.', 'danger')
                return render_template('atividades/editar.html', 
                                     atividade=atividade,
                                     unidade=unidade, 
                                     envolvidos=envolvidos, 
                                     cursos=cursos)
        
        # Converte as datas
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            if data_fim:
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                if data_fim < data_inicio:
                    flash('A data de fim deve ser posterior à data de início.', 'danger')
                    return render_template('atividades/editar.html', 
                                         atividade=atividade,
                                         unidade=unidade, 
                                         envolvidos=envolvidos, 
                                         cursos=cursos)
        except ValueError:
            flash('Formato de data inválido.', 'danger')
            return render_template('atividades/editar.html', 
                                 atividade=atividade,
                                 unidade=unidade, 
                                 envolvidos=envolvidos, 
                                 cursos=cursos)
        
        # Atualiza a atividade
        atividade.descricao = descricao
        atividade.data_inicio = data_inicio
        atividade.data_fim = data_fim
        atividade.status = status
        atividade.observacoes = observacoes
        atividade.envolvido_id = envolvido_id
        atividade.curso_id = curso_id
        atividade.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        flash('Atividade de estágio atualizada com sucesso!', 'success')
        return redirect(url_for('main.visualizar_atividade', id=id))
    
    return render_template('atividades/editar.html', 
                         atividade=atividade,
                         unidade=unidade, 
                         envolvidos=envolvidos, 
                         cursos=cursos)

@main.route('/atividades/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_atividade(id):
    """Exclui uma atividade"""
    atividade = AtividadeEstagio.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(atividade.unidade_id):
        flash('Você não tem permissão para excluir esta atividade.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    unidade_id = atividade.unidade_id
    
    try:
        db.session.delete(atividade)
        db.session.commit()
        flash('Atividade de estágio excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir atividade: {str(e)}', 'danger')
    
    return redirect(url_for('main.listar_atividades', unidade_id=unidade_id))

@main.route('/atividades/<int:id>/atualizar-status', methods=['POST'])
@login_required
def atualizar_status_atividade(id):
    """Atualiza o status de uma atividade"""
    atividade = AtividadeEstagio.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(atividade.unidade_id):
        flash('Você não tem permissão para atualizar esta atividade.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    novo_status = request.form.get('status')
    observacoes = request.form.get('observacoes')
    
    if novo_status not in ['Pendente', 'Em Andamento', 'Concluída', 'Cancelada']:
        flash('Status inválido.', 'danger')
        return redirect(url_for('main.visualizar_atividade', id=id))
    
    # Se está marcando como concluída, verifica se há data de fim
    if novo_status == 'Concluída' and not atividade.data_fim:
        data_fim = request.# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime
import re

from .models import db, User, Unidade, Curso, Envolvido, AtividadeEstagio
from .utils.decorators import admin_required, diretor_required
from .utils.validators import validar_cpf, validar_email

# Criar o Blueprint principal
main = Blueprint('main', __name__)

#------------------------------------------------------
# Funções auxiliares para controle de acesso
#------------------------------------------------------

def check_unidade_access(unidade_id):
    """Verifica se o usuário atual tem acesso à unidade especificada"""
    if current_user.is_admin():
        return True
    if current_user.is_diretor() and current_user.unidade_id == unidade_id:
        return True
    return False

def get_unidade_atual():
    """Retorna a unidade do usuário atual ou None se for admin"""
    if current_user.is_diretor():
        return Unidade.query.get(current_user.unidade_id)
    return None

#------------------------------------------------------
# Rotas de autenticação
#------------------------------------------------------

@main.route('/login', methods=['GET', 'POST'])
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
        
        # Busca o usuário pelo email
        user = User.query.filter_by(email=email).first()
        
        # Verifica se o usuário existe e a senha está correta
        if user and user.check_password(password):
            login_user(user)
            
            # Atualiza data do último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Redireciona para a página solicitada ou dashboard
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            
            flash(f'Bem-vindo, {user.nome or user.email}!', 'success')
            return redirect(next_page)
        
        flash('Email ou senha inválidos.', 'danger')
    
    return render_template('auth/login.html')

@main.route('/logout')
@login_required
def logout():
    """Rota para logout do sistema"""
    logout_user()
    flash('Você saiu do sistema com sucesso.', 'info')
    return redirect(url_for('main.login'))

@main.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    """Rota para recuperação de senha"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Implementação simplificada - em um sistema real, enviaria um email
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Se esse email estiver registrado, você receberá instruções para redefinir sua senha.', 'info')
        else:
            flash('Se esse email estiver registrado, você receberá instruções para redefinir sua senha.', 'info')
        
        return redirect(url_for('main.login'))
    
    return render_template('auth/recuperar_senha.html')

#------------------------------------------------------
# Dashboard e páginas principais
#------------------------------------------------------

@main.route('/')
@login_required
def dashboard():
    """Dashboard principal do sistema"""
    unidade = None
    total_cursos = 0
    total_envolvidos = 0
    total_orientadores = 0
    total_facilitadores = 0
    
    if current_user.is_admin():
        # Estatísticas para administradores (todas as unidades)
        total_unidades = Unidade.query.count()
        total_cursos = Curso.query.count()
        total_envolvidos = Envolvido.query.count()
        total_orientadores = Envolvido.query.filter_by(tipo='Orientador').count()
        total_facilitadores = Envolvido.query.filter_by(tipo='Facilitador').count()
        
        return render_template('admin/dashboard.html',
                              total_unidades=total_unidades,
                              total_cursos=total_cursos,
                              total_envolvidos=total_envolvidos,
                              total_orientadores=total_orientadores,
                              total_facilitadores=total_facilitadores)
    else:
        # Estatísticas para diretores (apenas sua unidade)
        unidade = Unidade.query.get(current_user.unidade_id)
        if not unidade:
            flash('Sua unidade não foi encontrada. Entre em contato com o administrador.', 'danger')
            return redirect(url_for('main.logout'))
        
        total_cursos = Curso.query.filter_by(unidade_id=unidade.id).count()
        total_envolvidos = Envolvido.query.filter_by(unidade_id=unidade.id).count()
        total_orientadores = Envolvido.query.filter_by(unidade_id=unidade.id, tipo='Orientador').count()
        total_facilitadores = Envolvido.query.filter_by(unidade_id=unidade.id, tipo='Facilitador').count()
        
        return render_template('diretor/dashboard.html',
                              unidade=unidade,
                              total_cursos=total_cursos,
                              total_envolvidos=total_envolvidos,
                              total_orientadores=total_orientadores,
                              total_facilitadores=total_facilitadores)

#------------------------------------------------------
# Rotas de Unidades (Admin)
#------------------------------------------------------

@main.route('/unidades')
@login_required
@admin_required
def listar_unidades():
    """Lista todas as unidades (apenas admin)"""
    unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
    return render_template('admin/unidades/listar.html', unidades=unidades)

@main.route('/unidades/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def nova_unidade():
    """Formulário para criar nova unidade (apenas admin)"""
    if request.method == 'POST':
        # Obter dados do formulário
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
            return render_template('admin/unidades/novo.html')
        
        if tipo not in ['Fatec', 'Etec']:
            flash('Tipo de unidade inválido.', 'danger')
            return render_template('admin/unidades/novo.html')
        
        # Verifica se já existe unidade com mesmo número e tipo
        existe = Unidade.query.filter_by(tipo=tipo, numero=numero).first()
        if existe:
            flash(f'Já existe uma {tipo} com o número {numero}!', 'danger')
            return render_template('admin/unidades/novo.html')
        
        # Cria a nova unidade
        unidade = Unidade(
            tipo=tipo,
            numero=numero,
            nome=nome,
            cidade=cidade,
            telefone=telefone,
            nome_diretor=nome_diretor,
            email_diretor=email_diretor
        )
        
        db.session.add(unidade)
        
        # Cria o usuário para o diretor
        email_institucional = unidade.email_institucional
        diretor_user = User(
            email=email_institucional,
            role='diretor',
            nome=nome_diretor
        )
        diretor_user.set_password(numero)  # Senha inicial é o número da unidade
        
        db.session.add(diretor_user)
        db.session.commit()
        
        # Associa o usuário à unidade
        diretor_user.unidade_id = unidade.id
        db.session.commit()
        
        flash(f'Unidade {unidade.nome} criada com sucesso!', 'success')
        return redirect(url_for('main.listar_unidades'))
    
    return render_template('admin/unidades/novo.html')

@main.route('/unidades/<int:id>')
@login_required
def visualizar_unidade(id):
    """Visualiza detalhes de uma unidade"""
    unidade = Unidade.query.get_or_404(id)
    
    # Verifica permissão de acesso
    if not check_unidade_access(id):
        flash('Você não tem permissão para acessar esta unidade.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    cursos = Curso.query.filter_by(unidade_id=id).all()
    orientadores = Envolvido.query.filter_by(unidade_id=id, tipo='Orientador').all()
    facilitadores = Envolvido.query.filter_by(unidade_id=id, tipo='Facilitador').all()
    
    return render_template('unidades/visualizar.html', 
                          unidade=unidade, 
                          cursos=cursos, 
                          orientadores=orientadores, 
                          facilitadores=facilitadores)

@main.route('/unidades/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_unidade(id):
    """Edita uma unidade existente (apenas admin)"""
    unidade = Unidade.query.get_or_404(id)
    
    if request.method == 'POST':
        # Obter dados do formulário
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
            return render_template('admin/unidades/editar.html', unidade=unidade)
        
        # Verifica se mudou o tipo ou número e se já existe outra unidade com esses dados
        if (tipo != unidade.tipo or numero != unidade.numero):
            existe = Unidade.query.filter_by(tipo=tipo, numero=numero).first()
            if existe and existe.id != id:
                flash(f'Já existe uma {tipo} com o número {numero}!', 'danger')
                return render_template('admin/unidades/editar.html', unidade=unidade)
        
        # Atualiza a unidade
        unidade.update(
            tipo=tipo,
            numero=numero,
            nome=nome,
            cidade=cidade,
            telefone=telefone,
            nome_diretor=nome_diretor,
            email_diretor=email_diretor
        )
        
        # Verifica se o email institucional mudou (por causa da mudança de tipo ou número)
        novo_email = f"{tipo[0]}{numero}dir@cps.sp.gov.br".lower()
        if unidade.email_institucional != novo_email:
            # Atualiza o email do usuário diretor
            diretor_user = User.query.filter_by(unidade_id=id, role='diretor').first()
            if diretor_user:
                diretor_user.email = novo_email
                diretor_user.nome = nome_diretor
                db.session.commit()
        
        db.session.commit()
        flash(f'Unidade {unidade.nome} atualizada com sucesso!', 'success')
        return redirect(url_for('main.listar_unidades'))
    
    return render_template('admin/unidades/editar.html', unidade=unidade)

@main.route('/unidades/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_unidade(id):
    """Exclui uma unidade (apenas admin)"""
    unidade = Unidade.query.get_or_404(id)
    
    try:
        # Exclui o usuário diretor associado
        diretor_user = User.query.filter_by(unidade_id=id, role='diretor').first()
        if diretor_user:
            db.session.delete(diretor_user)
        
        nome_unidade = unidade.nome
        db.session.delete(unidade)
        db.session.commit()
        flash(f'Unidade {nome_unidade} excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir unidade: {str(e)}', 'danger')
    
    return redirect(url_for('main.listar_unidades'))

#------------------------------------------------------
# Rotas de Perfil (Diretor)
#------------------------------------------------------

@main.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Visualiza e edita o perfil do usuário"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        # Atualiza o nome
        if nome and nome != current_user.nome:
            current_user.nome = nome
            db.session.commit()
            flash('Nome atualizado com sucesso!', 'success')
        
        # Atualiza a senha
        if senha_atual and nova_senha and confirmar_senha:
            if not current_user.check_password(senha_atual):
                flash('Senha atual incorreta.', 'danger')
            elif nova_senha != confirmar_senha:
                flash('As senhas não coincidem.', 'danger')
            else:
                current_user.set_password(nova_senha)
                db.session.commit()
                flash('Senha atualizada com sucesso!', 'success')
                return redirect(url_for('main.logout'))
        
    # Se for diretor, carrega os dados da unidade
    unidade = None
    if current_user.is_diretor():
        unidade = Unidade.query.get(current_user.unidade_id)
        
    return render_template('perfil/index.html', user=current_user, unidade=unidade)

@main.route('/perfil/unidade', methods=['GET', 'POST'])
@login_required
@diretor_required
def editar_perfil_unidade():
    """Permite ao diretor atualizar os dados da sua unidade"""
    unidade = Unidade.query.get_or_404(current_user.unidade_id)
    
    if request.method == 'POST':
        telefone = request.form.get('telefone')
        nome_diretor = request.form.get('nome_diretor')
        
        # Só permite atualizar o telefone e o nome do diretor
        if telefone and nome_diretor:
            unidade.telefone = telefone
            unidade.nome_diretor = nome_diretor
            
            # Atualiza também o nome no usuário
            current_user.nome = nome_diretor
            
            db.session.commit()
            flash('Informações da unidade atualizadas com sucesso!', 'success')
            return redirect(url_for('main.perfil'))
        else:
            flash('Preencha todos os campos obrigatórios.', 'warning')
    
    return render_template('perfil/editar_unidade.html', unidade=unidade)

#------------------------------------------------------
# Rotas de Cursos
#------------------------------------------------------

@main.route('/cursos')
@login_required
def listar_cursos():
    """Lista os cursos da unidade atual ou de todas as unidades (para admin)"""
    unidade_id = request.args.get('unidade_id', type=int)
    
    # Para diretores, força a visualização apenas da sua unidade
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    # Obtém a unidade, se especificada
    unidade = None
    if unidade_id:
        unidade = Unidade.query.get_or_404(unidade_id)
        # Verifica permissão
        if not check_unidade_access(unidade_id):
            flash('Você não tem permissão para acessar esta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    # Obtém os cursos conforme o contexto
    if unidade_id:
        cursos = Curso.query.filter_by(unidade_id=unidade_id).order_by(Curso.nome).all()
    else:
        # Apenas admin pode ver todos os cursos
        if not current_user.is_admin():
            return redirect(url_for('main.dashboard'))
        cursos = Curso.query.order_by(Curso.nome).all()
    
    # Obtém a lista de unidades para o filtro (apenas para admin)
    unidades = []
    if current_user.is_admin():
        unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
    
    return render_template('cursos/listar.html', 
                          cursos=cursos, 
                          unidade=unidade, 
                          unidades=unidades)

@main.route('/cursos/novo', methods=['GET', 'POST'])
@login_required
def novo_curso():
    """Cria um novo curso"""
    unidade_id = request.args.get('unidade_id', type=int)
    
    # Para diretores, força a unidade atual
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    # Verifica se a unidade existe e se o usuário tem acesso
    if unidade_id:
        unidade = Unidade.query.get_or_404(unidade_id)
        if not check_unidade_access(unidade_id):
            flash('Você não tem permissão para acessar esta unidade.', 'danger')
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
        
        # Verifica se já existe um curso com mesmo nome na unidade
        existe = Curso.query.filter_by(unidade_id=unidade_id, nome=nome).first()
        if existe:
            flash(f'Já existe um curso com o nome "{nome}" nesta unidade!', 'danger')
            return render_template('cursos/novo.html', unidade=unidade)
        
        # Cria o novo curso
        curso = Curso(
            nome=nome,
            unidade_id=unidade_id,
            codigo=codigo,
            descricao=descricao
        )
        
        db.session.add(curso)
        db.session.commit()
        
        flash(f'Curso "{curso.nome}" criado com sucesso!', 'success')
        return redirect(url_for('main.listar_cursos', unidade_id=unidade_id))
    
    return render_template('cursos/novo.html', unidade=unidade)

@main.route('/cursos/<int:id>')
@login_required
def visualizar_curso(id):
    """Visualiza detalhes de um curso"""
    curso = Curso.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(curso.unidade_id):
        flash('Você não tem permissão para acessar este curso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtém a lista de orientadores associados ao curso
    orientadores = curso.orientadores
    
    return render_template('cursos/visualizar.html', 
                          curso=curso, 
                          orientadores=orientadores)

@main.route('/cursos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_curso(id):
    """Edita um curso existente"""
    curso = Curso.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(curso.unidade_id):
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
        
        # Verifica se já existe outro curso com mesmo nome na unidade
        existe = Curso.query.filter_by(unidade_id=curso.unidade_id, nome=nome).first()
        if existe and existe.id != id:
            flash(f'Já existe um curso com o nome "{nome}" nesta unidade!', 'danger')
            return render_template('cursos/editar.html', curso=curso)
        
        # Atualiza o curso
        curso.update(
            nome=nome,
            codigo=codigo,
            descricao=descricao,
            ativo=ativo
        )
        
        db.session.commit()
        flash(f'Curso "{curso.nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('main.visualizar_curso', id=id))
    
    return render_template('cursos/editar.html', curso=curso)

@main.route('/cursos/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_curso(id):
    """Exclui um curso"""
    curso = Curso.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(curso.unidade_id):
        flash('Você não tem permissão para excluir este curso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    unidade_id = curso.unidade_id
    nome_curso = curso.nome
    
    try:
        db.session.delete(curso)
        db.session.commit()
        flash(f'Curso "{nome_curso}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir curso: {str(e)}', 'danger')
    
    return redirect(url_for('main.listar_cursos', unidade_id=unidade_id))

#------------------------------------------------------
# Rotas de Envolvidos (Facilitadores e Orientadores)
#------------------------------------------------------

@main.route('/envolvidos')
@login_required
def listar_envolvidos():
    """Lista os envolvidos com estágio"""
    unidade_id = request.args.get('unidade_id', type=int)
    tipo = request.args.get('tipo')  # 'Facilitador' ou 'Orientador'
    
    # Para diretores, força a visualização apenas da sua unidade
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    # Obtém a unidade, se especificada
    unidade = None
    if unidade_id:
        unidade = Unidade.query.get_or_404(unidade_id)
        # Verifica permissão
        if not check_unidade_access(unidade_id):
            flash('Você não tem permissão para acessar esta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    # Constrói a query base
    query = Envolvido.query
    
    # Filtra por unidade
    if unidade_id:
        query = query.filter_by(unidade_id=unidade_id)
    
    # Filtra por tipo
    if tipo in ['Facilitador', 'Orientador']:
        query = query.filter_by(tipo=tipo)
    
    # Ordena e executa
    envolvidos = query.order_by(Envolvido.nome).all()
    
    # Obtém a lista de unidades para o filtro (apenas para admin)
    unidades = []
    if current_user.is_admin():
        unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
    
    return render_template('envolvidos/listar.html', 
                          envolvidos=envolvidos, 
                          unidade=unidade, 
                          unidades=unidades,
                          tipo_filtro=tipo)

@main.route('/envolvidos/novo', methods=['GET', 'POST'])
@login_required
def novo_envolvido():
    """Cria um novo envolvido (Facilitador ou Orientador)"""
    unidade_id = request.args.get('unidade_id', type=int)
    tipo_pre = request.args.get('tipo')  # Tipo pré-selecionado
    
    # Para diretores, força a unidade atual
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    # Verifica se a unidade existe e se o usuário tem acesso
    if unidade_id:
        unidade = Unidade.query.get_or_404(unidade_id)
        if not check_unidade_access(unidade_id):
            flash('Você não tem permissão para acessar esta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
    else:
        # Se não foi especificada uma unidade e o usuário é admin, mostra formulário com seleção
        if current_user.is_admin():
            unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
            return render_template('envolvidos/novo.html', unidades=unidades, tipo=tipo_pre)
        else:
            flash('Unidade não especificada.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    # Obtém os cursos da unidade para associação (caso seja orientador)
    cursos = Curso.query.filter_by(unidade_id=unidade_id, ativo=True).order_by(Curso.nome).all()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        cargo = request.form.get('cargo')
        tipo = request.form.get('tipo')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        cursos_ids = request.form.getlist('cursos')
        
        # Se o usuário é admin, pode mudar a unidade
        if current_user.is_admin():
            unidade_id = request.form.get('unidade_id', type=int)
            if not unidade_id:
                flash('Selecione uma unidade.', 'danger')
                unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
                return render_template('envolvidos/novo.html', unidades=unidades, tipo=tipo)
            
            unidade = Unidade.query.get_or_404(unidade_id)
            # Recarrega os cursos da unidade selecionada
            cursos = Curso.query.filter_by(unidade_id=unidade_id, ativo=True).order_by(Curso.nome).all()
        
        # Validações básicas
        if not all([nome, cpf, cargo, tipo]):
            flash('Os campos Nome, CPF, Cargo e Tipo são obrigatórios.', 'danger')
            return render_template('envolvidos/novo.html', unidade=unidade, cursos=cursos, tipo=tipo)
        
        if tipo not in ['Facilitador', 'Orientador']:
            flash('Tipo inválido.', 'danger')
            return render_template('envolvidos/novo.html', unidade=unidade, cursos=cursos)
        
        # Formata o CPF
        cpf = Envolvido.formatar_cpf(cpf)
        
        # Valida o CPF
        if not Envolvido.validar_cpf(cpf):
            flash('CPF inválido.', 'danger')
            return render_template('envolvidos/novo.html', unidade=unidade, cursos=cursos, tipo=tipo)
        
        # Verifica se já existe um envolvido com o mesmo CPF
        existe = Envolvido.query.filter_by(cpf=cpf).first()
        if existe:
            flash(f'Já existe um envolvido com o CPF {cpf}!', 'danger')
            return render_template('envolvidos/novo.html', unidade=unidade, cursos=cursos, tipo=tipo)
        
        # Cria o novo envolvido
        envolvido = Envolvido(
            nome=nome,
            cpf=cpf,
            cargo=cargo,
            tipo=tipo,
            unidade_id=unidade_id,
            telefone=telefone,
            email=email
        )
        
        db.session.add(envolvido)
        
        # Para orientadores, associa aos cursos selecionados
        if tipo == 'Orientador' and cursos_ids:
            cursos_selecionados = Curso.query.filter(Curso.id.in_(cursos_ids)).all()
            envolvido.cursos = cursos_selecionados
            
            # Validação da regra de negócio
            if not cursos_selecionados:
                flash('Orientadores devem estar associados a pelo menos um curso.', 'danger')
                db.session.rollback()
                return render_template('envolvidos/novo.html', unidade=unidade, cursos=cursos, tipo=tipo)
        elif tipo == 'Orientador' and not cursos_ids:
            flash('Orientadores devem estar associados a pelo menos um curso.', 'danger')
            return render_template('envolvidos/novo.html', unidade=unidade, cursos=cursos, tipo=tipo)
        
        db.session.commit()
        
        flash(f'{envolvido.tipo} {envolvido.nome} cadastrado com sucesso!', 'success')
        return redirect(url_for('main.listar_envolvidos', unidade_id=unidade_id, tipo=tipo))
    
    return render_template('envolvidos/novo.html', 
                          unidade=unidade, 
                          cursos=cursos,
                          tipo=tipo_pre)

@main.route('/envolvidos/<int:id>')
@login_required
def visualizar_envolvido(id):
    """Visualiza detalhes de um envolvido"""
    envolvido = Envolvido.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(envolvido.unidade_id):
        flash('Você não tem permissão para acessar este envolvido.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('envolvidos/visualizar.html', envolvido=envolvido)

@main.route('/envolvidos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_envolvido(id):
    """Edita um envolvido existente"""
    envolvido = Envolvido.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(envolvido.unidade_id):
        flash('Você não tem permissão para editar este envolvido.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtém os cursos da unidade para associação (caso seja orientador)
    cursos = Curso.query.filter_by(unidade_id=envolvido.unidade_id, ativo=True).order_by(Curso.nome).all()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        cargo = request.form.get('cargo')
        tipo = request.form.get('tipo')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        ativo = 'ativo' in request.form
        cursos_ids = request.form.getlist('cursos')
        
        # Validações básicas
        if not all([nome, cpf, cargo, tipo]):
            flash('Os campos Nome, CPF, Cargo e Tipo são obrigatórios.', 'danger')
            return render_template('envolvidos/editar.html', envolvido=envolvido, cursos=cursos)
        
        if tipo not in ['Facilitador', 'Orientador']:
            flash('Tipo inválido.', 'danger')
            return render_template('envolvidos/editar.html', envolvido=envolvido, cursos=cursos)
        
        # Formata o CPF
        cpf = Envolvido.formatar_cpf(cpf)
        
        # Valida o CPF
        if not Envolvido.validar_cpf(cpf):
            flash('CPF inválido.', 'danger')
            return render_template('envolvidos/editar.html', envolvido=envolvido, cursos=cursos)
        
        # Verifica se já existe outro envolvido com o mesmo CPF
        existe = Envolvido.query.filter_by(cpf=cpf).first()
        if existe and existe.id != id:
            flash(f'Já existe um envolvido com o CPF {cpf}!', 'danger')
            return render_template('envolvidos/editar.html', envolvido=envolvido, cursos=cursos)
        
        # Atualiza o envolvido
        envolvido.update(
            nome=nome,
            cpf=cpf,
            cargo=cargo,
            tipo=tipo,
            telefone=telefone,
            email=email,
            ativo=ativo
        )
        
        # Para orientadores, associa aos cursos selecionados
        if tipo == 'Orientador':
            cursos_selecionados = Curso.query.filter(Curso.id.in_(cursos_ids)).all()
            envolvido.cursos = cursos_selecionados
            
            # Validação da regra de negócio
            if not cursos_selecionados:
                flash('Orientadores devem estar associados a pelo menos um curso.', 'danger')
                db.session.rollback()
                return render_template('envolvidos/editar.html', envolvido=envolvido, cursos=cursos)
        else:
            # Se for facilitador, remove associações com cursos (se houver)
            envolvido.cursos = []
        
        db.session.commit()
        
        flash(f'{envolvido.tipo} {envolvido.nome} atualizado com sucesso!', 'success')
        return redirect(url_for('main.visualizar_envolvido', id=id))
    
    return render_template('envolvidos/editar.html', envolvido=envolvido, cursos=cursos)

@main.route('/envolvidos/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_envolvido(id):
    """Exclui um envolvido"""
    envolvido = Envolvido.query.get_or_404(id)
    
    # Verifica permissão
    if not check_unidade_access(envolvido.unidade_id):
        flash('Você não tem permissão para excluir este envolvido.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    unidade_id = envolvido.unidade_id
    tipo = envolvido.tipo
    nome = envolvido.nome
    
    try:
        db.session.delete(envolvido)
        db.session.commit()
        flash(f'{tipo} {nome} excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir envolvido: {str(e)}', 'danger')
    
    return redirect(url_for('main.listar_envolvidos', unidade_id=unidade_id, tipo=tipo))

#------------------------------------------------------
# Rotas de Atividades de Estágio
#------------------------------------------------------

@main.route('/atividades')
@login_required
def listar_atividades():
    """Lista as atividades de estágio"""
    unidade_id = request.args.get('unidade_id', type=int)
    envolvido_id = request.args.get('envolvido_id', type=int)
    status = request.args.get('status')
    
    # Para diretores, força a visualização apenas da sua unidade
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    # Constrói a query base
    query = AtividadeEstagio.query
    
    # Aplica os filtros
    if unidade_id:
        query = query.filter_by(unidade_id=unidade_id)
        # Verifica permissão
        if not check_unidade_access(unidade_id):
            flash('Você não tem permissão para acessar esta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    if envolvido_id:
        query = query.filter_by(envolvido_id=envolvido_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Ordena e executa
    atividades = query.order_by(AtividadeEstagio.data_inicio.desc()).all()
    
    # Dados para filtros
    unidades = []
    envolvidos = []
    status_options = ['Pendente', 'Em Andamento', 'Concluída', 'Cancelada']
    
    # Prepara dados para os filtros
    if current_user.is_admin():
        unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
        
        if unidade_id:
            envolvidos = Envolvido.query.filter_by(unidade_id=unidade_id).order_by(Envolvido.nome).all()
    else:
        unidade = Unidade.query.get(current_user.unidade_id)
        if unidade:
            unidades = [unidade]
            envolvidos = Envolvido.query.filter_by(unidade_id=unidade.id).order_by(Envolvido.nome).all()
    
    return render_template('atividades/listar.html', 
                          atividades=atividades,
                          unidades=unidades,
                          envolvidos=envolvidos,
                          status_options=status_options,
                          filtro_unidade_id=unidade_id,
                          filtro_envolvido_id=envolvido_id,
                          filtro_status=status)

@main.route('/atividades/nova', methods=['GET', 'POST'])
@login_required
def nova_atividade():
    """Cria uma nova atividade de estágio"""
    unidade_id = request.args.get('unidade_id', type=int)
    envolvido_id = request.args.get('envolvido_id', type=int)
    
    # Para diretores, força a unidade atual
    if current_user.is_diretor():
        unidade_id = current_user.unidade_id
    
    # Verifica se a unidade existe e se o usuário tem acesso
    if unidade_id:
        unidade = Unidade.query.get_or_404(unidade_id)
        if not check_unidade_access(unidade_id):
            flash('Você não tem permissão para acessar esta unidade.', 'danger')
            return redirect(url_for('main.dashboard'))
    else:
        # Se não foi especificada uma unidade e o usuário é admin, mostra formulário com seleção
        if current_user.is_admin():
            unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
            return render_template('atividades/nova.html', unidades=unidades)
        else:
            flash('Unidade não especificada.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    # Obtém a lista de envolvidos da unidade
    envolvidos = Envolvido.query.filter_by(unidade_id=unidade_id, ativo=True).order_by(Envolvido.nome).all()
    
    # Obtém o envolvido pré-selecionado, se houver
    envolvido_pre = None
    if envolvido_id:
        envolvido_pre = Envolvido.query.get(envolvido_id)
        if not envolvido_pre or envolvido_pre.unidade_id != unidade_id:
            envolvido_pre = None
    
    # Obtém os cursos da unidade
    cursos = Curso.query.filter_by(unidade_id=unidade_id, ativo=True).order_by(Curso.nome).all()
    
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim') or None
        status = request.form.get('status')
        observacoes = request.form.get('observacoes')
        envolvido_id = request.form.get('envolvido_id', type=int)
        curso_id = request.form.get('curso_id', type=int) or None
        
        # Se o usuário é admin, pode mudar a unidade
        if current_user.is_admin():
            unidade_id = request.form.get('unidade_id', type=int)
            if not unidade_id:
                flash('Selecione uma unidade.', 'danger')
                unidades = Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()
                return render_template('ativ