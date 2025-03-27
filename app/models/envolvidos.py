# app/models/envolvidos.py
from datetime import datetime

from . import db
from .cursos import orientador_curso

class Envolvido(db.Model):
    """
    Modelo que representa uma pessoa envolvida com o estágio (Facilitador ou Orientador).
    Pode ser cadastrado por administradores ou diretores da unidade.
    """
    __tablename__ = 'envolvidos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    cargo = db.Column(db.String(100), nullable=True)
    tipo = db.Column(db.String(12), nullable=True)  # 'Facilitador' ou 'Orientador'
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com cursos (somente para orientadores)
    cursos = db.relationship(
        'Curso', 
        secondary=orientador_curso, 
        lazy='subquery',
        backref=db.backref('orientadores', lazy=True)
    )
    
    def __init__(self, nome, cpf, cargo, tipo, unidade_id, telefone=None, email=None):
        self.nome = nome
        self.cpf = cpf
        self.cargo = cargo
        self.tipo = tipo
        self.unidade_id = unidade_id
        self.telefone = telefone
        self.email = email
    
    @property
    def is_orientador(self):
        """Verifica se o envolvido é um orientador"""
        return self.tipo == 'Orientador'
    
    @property
    def is_facilitador(self):
        """Verifica se o envolvido é um facilitador"""
        return self.tipo == 'Facilitador'
    
    def update(self, nome, cpf, cargo, tipo, telefone=None, email=None, ativo=True):
        """Atualiza os dados do envolvido"""
        self.nome = nome
        self.cpf = cpf
        self.cargo = cargo
        self.tipo = tipo
        self.telefone = telefone
        self.email = email
        self.ativo = ativo
        self.updated_at = datetime.utcnow()
    
    def add_curso(self, curso):
        """Adiciona um curso para o orientador (se aplicável)"""
        if self.is_orientador and curso not in self.cursos:
            self.cursos.append(curso)
    
    def remove_curso(self, curso):
        """Remove um curso do orientador"""
        if curso in self.cursos:
            self.cursos.remove(curso)
    
    def set_cursos(self, cursos_list):
        """Define a lista completa de cursos para o orientador"""
        if self.is_orientador:
            self.cursos = cursos_list
        else:
            # Se for facilitador, não deve ter cursos associados
            self.cursos = []
    
    def inativar(self):
        """Marca o envolvido como inativo"""
        self.ativo = False
        self.updated_at = datetime.utcnow()
    
    def ativar(self):
        """Marca o envolvido como ativo"""
        self.ativo = True
        self.updated_at = datetime.utcnow()
    
    def validate(self):
        """
        Valida se os dados do envolvido estão corretos de acordo com seu tipo
        """
        # Verificação específica para orientadores
        if self.is_orientador and not self.cursos:
            return False, "Orientadores devem estar associados a pelo menos um curso."
        
        # Verificação específica para facilitadores
        if self.is_facilitador and self.cursos:
            return False, "Facilitadores não devem estar associados a cursos."
        
        return True, "Dados válidos."
    
    @staticmethod
    def formatar_cpf(cpf):
        """
        Formata um CPF para o padrão XXX.XXX.XXX-XX.
        Remove caracteres não numéricos e aplica a formatação.
        """
        # Remove caracteres não numéricos
        cpf_numeros = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se tem 11 dígitos
        if len(cpf_numeros) != 11:
            return cpf  # Retorna o CPF original se não tiver 11 dígitos
        
        # Aplica a formatação
        return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
    
    @staticmethod
    def validar_cpf(cpf):
        """
        Verifica se um CPF é válido segundo as regras da Receita Federal.
        """
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Cálculo do primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(cpf[i]) * (10 - i)
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Verifica o primeiro dígito verificador
        if digito1 != int(cpf[9]):
            return False
        
        # Cálculo do segundo dígito verificador
        soma = 0
        for i in range(10):
            soma += int(cpf[i]) * (11 - i)
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verifica o segundo dígito verificador
        return digito2 == int(cpf[10])
    
    def __repr__(self):
        tipo_str = "Orientador" if self.is_orientador else "Facilitador"
        return f'<Envolvido {self.nome}, {tipo_str}, Unidade: {self.unidade_id}>'
