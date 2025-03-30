# app/models/envolvidos.py
from datetime import datetime

from . import db
from .cursos import orientador_curso

class Envolvido(db.Model):
    """
    Modelo que representa uma pessoa envolvida com o estágio.
    Tipos possíveis:
    - FATEC: Orientador, Coordenador, Apoio
    - ETEC: ATA, Facilitador, Apoio
    """
    __tablename__ = 'envolvidos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    cargo = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'Orientador', 'Coordenador', 'ATA', 'Facilitador', 'Apoio'
    email_institucional = db.Column(db.String(200), nullable=False)  # Novo campo obrigatório
    celular = db.Column(db.String(20), nullable=False)  # Novo campo obrigatório
    # email_pessoal = db.Column(db.String(100), nullable=True)  # Antigo campo 'email' renomeado
    # telefone = db.Column(db.String(20), nullable=True)  # Mantido como opcional (telefone fixo)
    ativo = db.Column(db.Boolean, default=True)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com cursos (pode ser obrigatório ou opcional dependendo do tipo)
    cursos = db.relationship(
        'Curso', 
        secondary=orientador_curso, 
        lazy='subquery',
        backref=db.backref('envolvidos', lazy=True)
    )
    
    def __init__(self, nome, cpf, cargo, tipo, unidade_id, 
                 email_institucional, celular, 
                 email_pessoal=None, telefone=None):
        self.nome = nome
        self.cpf = cpf
        self.cargo = cargo
        self.tipo = tipo
        self.unidade_id = unidade_id
        self.email_institucional = email_institucional
        self.celular = celular
        # self.email_pessoal = email_pessoal
        # self.telefone = telefone
    
    # Propriedades para verificar tipo
    @property
    def is_orientador(self):
        """Verifica se o envolvido é um orientador"""
        return self.tipo == 'Orientador'
    
    @property
    def is_coordenador(self):
        """Verifica se o envolvido é um coordenador de curso"""
        return self.tipo == 'Coordenador'
    
    @property
    def is_ata(self):
        """Verifica se o envolvido é um ATA"""
        return self.tipo == 'ATA'
    
    @property
    def is_facilitador(self):
        """Verifica se o envolvido é um facilitador"""
        return self.tipo == 'Facilitador'
    
    @property
    def is_apoio(self):
        """Verifica se o envolvido é apoio de estágio"""
        return self.tipo == 'Apoio'
    
    @property
    def requires_cursos(self):
        """Verifica se o tipo de envolvido requer associação com cursos"""
        # Orientadores e Coordenadores (FATEC) DEVEM estar associados a cursos
        return self.tipo in ['Orientador', 'Coordenador']
    
    @property
    def allows_cursos(self):
        """Verifica se o tipo de envolvido permite associação com cursos"""
        # ATAs e Facilitadores (ETEC) PODEM estar associados a cursos,
        # além dos que obrigatoriamente precisam estar associados
        return self.tipo in ['Orientador', 'Coordenador', 'ATA', 'Facilitador']
    
    @property
    def is_fatec_tipo(self):
        """Verifica se o envolvido é de um tipo associado à FATEC"""
        return self.tipo in ['Orientador', 'Coordenador']
    
    @property
    def is_etec_tipo(self):
        """Verifica se o envolvido é de um tipo associado à ETEC"""
        return self.tipo in ['ATA', 'Facilitador']
    
    def update(self, nome, cpf, cargo, tipo, 
               email_institucional, celular, 
               email_pessoal=None, telefone=None, ativo=True):
        """Atualiza os dados do envolvido"""
        self.nome = nome
        self.cpf = cpf
        self.cargo = cargo
        self.tipo = tipo
        self.email_institucional = email_institucional
        self.celular = celular
        # self.email_pessoal = email_pessoal
        # self.telefone = telefone
        self.ativo = ativo
        self.updated_at = datetime.utcnow()
    
    def add_curso(self, curso):
        """Adiciona um curso para o envolvido (se aplicável)"""
        if self.allows_cursos and curso not in self.cursos:
            self.cursos.append(curso)
    
    def remove_curso(self, curso):
        """Remove um curso do envolvido"""
        if curso in self.cursos:
            self.cursos.remove(curso)
    
    def set_cursos(self, cursos_list):
        """Define a lista completa de cursos para o envolvido"""
        if self.allows_cursos:
            self.cursos = cursos_list
        else:
            # Se for um tipo que não permite cursos (Apoio), não deve ter cursos associados
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
        # Verificação para tipos que exigem cursos (Orientador, Coordenador)
        if self.requires_cursos and not self.cursos:
            return False, f"{self.tipo}es devem estar associados a pelo menos um curso."
        
        # Verificação para tipos que não permitem cursos (Apoio)
        if not self.allows_cursos and self.cursos:
            return False, f"{self.tipo}s não devem estar associados a cursos."
        
        # Verificação de consistência de unidade-tipo
        if self.unidade and self.unidade.tipo == 'Fatec' and self.is_etec_tipo:
            return False, f"{self.tipo}s só podem ser vinculados a unidades ETEC."
        
        if self.unidade and self.unidade.tipo == 'Etec' and self.is_fatec_tipo:
            return False, f"{self.tipo}s só podem ser vinculados a unidades FATEC."
        
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
        return f'<Envolvido {self.nome}, {self.tipo}, Unidade: {self.unidade_id}>'