import os
from dotenv import load_dotenv
from flask_migrate import Migrate

# Carrega as variáveis de ambiente
load_dotenv()

# Cria a aplicação Flask
from app import create_app, db
from app.models import User, Unidade, Curso, Envolvido

app = create_app(os.getenv('FLASK_ENV', 'development'))
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Permite acessar os modelos diretamente no shell Flask."""
    return dict(
        app=app, 
        db=db, 
        User=User, 
        Unidade=Unidade, 
        Curso=Curso, 
        Envolvido=Envolvido
    )

@app.cli.command("create-admin")
def create_admin():
    """Cria um usuário administrador inicial."""
    from app.models import User, db
    
    # Verifica se já existe um administrador
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print("Um administrador já existe no sistema.")
        return
    
    # Cria o administrador
    admin = User(
        email='admin@cps.sp.gov.br',
        role='admin'
    )
    admin.set_password('admin123')  # Senha temporária, deve ser alterada após o primeiro login
    
    db.session.add(admin)
    db.session.commit()
    
    print("Administrador criado com sucesso!")
    print("Email: admin@cps.sp.gov.br")
    print("Senha: admin123")
    print("Por favor, altere esta senha após o primeiro login.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
