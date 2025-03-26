# app/models/unidades.py
from datetime import datetime

from . import db

class Unidade(db.Model):
    """
    Modelo que representa uma unidade de ensino (Fatec ou Etec).
    Gerenciado principalmente pelo administrador do sistema.
    """
    __tablename__ = 'unidades'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(5), nullable=False)  # 'Fatec' ou 'Etec'
    numero = db.Column(db.String(3), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    nome_diretor = db.Column(db.String(100), nullable=False)
    email_diretor = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    diretor_user = db.relationship('User', backref='unidade', uselist=False, foreign_keys='User.unidade_id')
    cursos = db.relationship('Curso', backref='unidade', lazy=True, cascade='all, delete-orphan')
    envolvidos = db.relationship('Envolvido', backref='unidade', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, tipo, numero, nome, cidade, telefone, nome_diretor, email_diretor):
        self.tipo = tipo
        self.numero = numero
        self.nome = nome
        self.cidade = cidade
        self.telefone = telefone
        self.nome_diretor = nome_diretor
        self.email_diretor = email_diretor
    
    @property
    def codigo(self):
        """
        Retorna o código da unidade (F000 ou E000) baseado no tipo e número.
        Usado para gerar o email institucional.
        """
        prefixo = 'F' if self.tipo == 'Fatec' else 'E'
        return f'{prefixo}{self.numero.zfill(3)}'
    
    @property
    def email_institucional(self):
        """
        Retorna o email institucional do diretor com base no código da unidade.
        Padrão: [codigo]dir@cps.sp.gov.br
        """
        return f'{self.codigo}dir@cps.sp.gov.br'.lower()
    
    def update(self, tipo, numero, nome, cidade, telefone, nome_diretor, email_diretor):
        """Atualiza os dados da unidade"""
        self.tipo = tipo
        self.numero = numero
        self.nome = nome
        self.cidade = cidade
        self.telefone = telefone
        self.nome_diretor = nome_diretor
        self.email_diretor = email_diretor
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Unidade {self.codigo}: {self.nome}>'
