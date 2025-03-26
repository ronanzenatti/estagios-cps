# app/utils/__init__.py
"""
Pacote de utilitários para a aplicação de estágio do CPS.
Contém funções e classes auxiliares usadas em vários pontos da aplicação.
"""

# Importações para facilitar o acesso às funções através do pacote
from .validators import validar_cpf, validar_email
from .decorators import admin_required, diretor_required
