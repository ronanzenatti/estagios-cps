# app/__init__.py
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

# Adiciona o registro do PyMySQL como conector do MySQL
import pymysql
pymysql.install_as_MySQLdb()

from .models import db, User
from .config import config

login_manager = LoginManager()
login_manager.login_view = 'main.login'
csrf = CSRFProtect()
mail = Mail()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Adicione estas linhas para melhorar o logging
    import logging
    from logging import StreamHandler
    file_handler = StreamHandler()
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Teste de conexão com o banco
    try:
        app.logger.info(f"Inicializando aplicação em ambiente: {config_name}")
        app.logger.info(f"DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Não configurado')}")
        
        # Verificando certificado SSL
        if app.config.get('SQLALCHEMY_ENGINE_OPTIONS') and 'connect_args' in app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}):
            ssl_config = app.config['SQLALCHEMY_ENGINE_OPTIONS'].get('connect_args', {}).get('ssl', {})
            ssl_path = ssl_config.get('ca') if ssl_config else None
            import os
            if ssl_path and os.path.exists(ssl_path):
                app.logger.info(f"Certificado SSL encontrado: {ssl_path}")
            else:
                app.logger.error(f"Certificado SSL NÃO encontrado: {ssl_path}")
    except Exception as e:
        app.logger.error(f"Erro durante a inicialização: {str(e)}")
    
    # Inicializa extensões
    try:
        app.logger.info("Inicializando extensões...")
        db.init_app(app)
        app.logger.info("DB inicializado com sucesso")
        login_manager.init_app(app)
        app.logger.info("Login manager inicializado com sucesso")
        csrf.init_app(app)
        app.logger.info("CSRF inicializado com sucesso")
        mail.init_app(app)
        app.logger.info("Mail inicializado com sucesso")
    except Exception as e:
        app.logger.error(f"Erro ao inicializar extensões: {str(e)}")
    
    # Registra os blueprints
    try:
        app.logger.info("Registrando blueprints...")
        from .routes import register_blueprints
        register_blueprints(app)
        app.logger.info("Blueprints registrados com sucesso")
    except Exception as e:
        app.logger.error(f"Erro ao registrar blueprints: {str(e)}")
    
    app.logger.info("Aplicação inicializada com sucesso")
    return app
