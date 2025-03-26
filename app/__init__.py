# app/__init__.py
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail  # Adicione esta importação

from .models import db, User
from .config import config

login_manager = LoginManager()
login_manager.login_view = 'main.login'
csrf = CSRFProtect()
mail = Mail()  # Crie a instância do Flask-Mail

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)  # Inicializa o Flask-Mail
    
    # Registra os blueprints utilizando a função do pacote routes
    from .routes import register_blueprints
    register_blueprints(app)
    
    return app