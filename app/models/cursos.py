# app/models/cursos.py
from datetime import datetime

from . import db

# Tabela de associação entre Orientadores e Cursos
# Esta é uma tabela de relacionamento many-to-many
orientador_curso = db.Table('orientador_curso',
    db.Column('orientador_id', db.Integer, db.ForeignKey('envolvidos.id', ondelete='CASCADE'), primary_key=True),
    db.Column('curso_id', db.Integer, db.ForeignKey('cursos.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Curso(db.Model):
    """
    Modelo que representa um curso oferecido por uma unidade.
    Cada curso pode estar associado a vários orientadores de estágio.
    """
    __tablename__ = 'cursos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), nullable=True)  # Código opcional do curso
    descricao = db.Column(db.Text, nullable=True)     # Descrição opcional do curso
    ativo = db.Column(db.Boolean, default=True)       # Indica se o curso está ativo
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com orientadores através da tabela associativa
    # É definido na classe Envolvido para evitar referência circular
    
    def __init__(self, nome, unidade_id, codigo=None, descricao=None):
        self.nome = nome
        self.unidade_id = unidade_id
        self.codigo = codigo
        self.descricao = descricao
    
    def update(self, nome, codigo=None, descricao=None, ativo=True):
        """Atualiza os dados do curso"""
        self.nome = nome
        self.codigo = codigo
        self.descricao = descricao
        self.ativo = ativo
        self.updated_at = datetime.utcnow()
    
    def inativar(self):
        """Marca o curso como inativo"""
        self.ativo = False
        self.updated_at = datetime.utcnow()
    
    def ativar(self):
        """Marca o curso como ativo"""
        self.ativo = True
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Curso {self.nome}, Unidade: {self.unidade_id}>'
