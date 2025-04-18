# app/config.py
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao-nao-use-em-producao'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações do Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@estagio.cps.sp.gov.br'
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'mysql+pymysql://root:123456@localhost:3307/estagio'


class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    
    # Configurações adicionais para SQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 299,  # Reconecta após 299 segundos
        "pool_timeout": 20,   # Timeout de 20 segundos
        "pool_pre_ping": True, # Verifica conexão antes de usar
        "max_overflow": 5,    # Conexões extras permitidas
        "pool_size": 10       # Tamanho do pool de conexões
    }
    
    # Adiciona configuração SSL se necessário
    if SQLALCHEMY_DATABASE_URI and 'mysql+pymysql' in SQLALCHEMY_DATABASE_URI and not 'ssl_disabled=True' in SQLALCHEMY_DATABASE_URI:
        cert_path = "/home/site/wwwroot/DigiCertGlobalRootCA.crt.pem"
        # Verifica se o certificado existe
        import os
        if os.path.exists(cert_path):
            SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {
                "ssl": {
                    "ca": cert_path
                }
            }


class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3307/estagio'


# Dicionário de configurações disponíveis
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}