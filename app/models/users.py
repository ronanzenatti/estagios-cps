# app/models/users.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db

class User(db.Model, UserMixin):
    """
    Modelo de usuário para autenticação no sistema.
    Este modelo representa tanto administradores quanto diretores.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' ou 'diretor'
    nome = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relacionamento com Unidade (somente para diretores)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=True)
    
    def __init__(self, email, role, nome=None, unidade_id=None):
        self.email = email
        self.role = role
        self.nome = nome
        self.unidade_id = unidade_id
    
    def set_password(self, password):
        """Define a senha do usuário (armazenada como hash)"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash armazenado"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verifica se o usuário é um administrador"""
        return self.role == 'admin'
    
    def is_diretor(self):
        """Verifica se o usuário é um diretor"""
        return self.role == 'diretor'
    
    def update_last_login(self):
        """Atualiza o timestamp de último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.email}, Role: {self.role}>'
