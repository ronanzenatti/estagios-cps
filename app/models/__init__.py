# app/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

# Inicializa o objeto SQLAlchemy
db = SQLAlchemy()

# Importa os modelos para torná-los disponíveis através do pacote models
from .users import User
from .unidades import Unidade
from .cursos import Curso, orientador_curso
from .envolvidos import Envolvido
