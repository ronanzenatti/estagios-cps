# app/routes/__init__.py
"""
Pacote de rotas da aplicação.
Define os Blueprints para organizar as rotas por contexto.
"""

from flask import Blueprint

# Criação dos blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
diretor_bp = Blueprint('diretor', __name__, url_prefix='/diretor')
unidades_bp = Blueprint('unidades', __name__, url_prefix='/unidades')
cursos_bp = Blueprint('cursos', __name__, url_prefix='/cursos')
envolvidos_bp = Blueprint('envolvidos', __name__, url_prefix='/envolvidos')
main_bp = Blueprint('main', __name__)

# Importa as rotas específicas
from . import auth_routes
from . import admin_routes
from . import diretor_routes
from . import unidades_routes
from . import cursos_routes
from . import envolvidos_routes
from . import main_routes

# Registra os blueprints na aplicação
def register_blueprints(app):
    """
    Registra todos os blueprints na aplicação Flask.
    
    Args:
        app: Aplicação Flask
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(diretor_bp)
    app.register_blueprint(unidades_bp)
    app.register_blueprint(cursos_bp)
    app.register_blueprint(envolvidos_bp)
    
    # Registra manipuladores de erro personalizados usando as funções definidas em main_routes.py
    from .main_routes import handle_error_404, handle_error_403, handle_error_500
    
    app.register_error_handler(404, handle_error_404)
    app.register_error_handler(403, handle_error_403)
    app.register_error_handler(500, handle_error_500)
    
    return app