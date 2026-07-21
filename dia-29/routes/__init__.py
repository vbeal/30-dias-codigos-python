# Registra todas as rotas no app Flask

from routes import (
    auth,
    ativos,
    calculadora,
    carteiras,
    painel,
    perfil,
    radar,
    rankings,
)


def register_all(app):
    auth.register(app)
    painel.register(app)
    rankings.register(app)
    ativos.register(app)
    calculadora.register(app)
    radar.register(app)
    carteiras.register(app)
    perfil.register(app)
