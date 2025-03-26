# Configurações do Flask
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=sua_chave_secreta_aqui_substitua_por_algo_seguro

# Configurações do Banco de Dados
DB_HOST=localhost
DB_NAME=estagio_cps
DB_USER=root
DB_PASSWORD=sua_senha_aqui

# Configuração da URI do SQLAlchemy
DATABASE_URI=mysql+pymysql://root:sua_senha_aqui@localhost/estagio_cps

# Configurações do Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_ou_app_password
MAIL_DEFAULT_SENDER=noreply@estagio.cps.sp.gov.br