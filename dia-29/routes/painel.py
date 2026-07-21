# Rotas: painel

from flask import flash, redirect, render_template, session, url_for

from db import get_user_by_id
from db_carteira import get_carteira_padrao
from web.helpers import login_required, refresh_session


def register(app):
    @app.route("/painel")
    @login_required
    def painel():
        user = get_user_by_id(session["user_id"])
        if not user:
            session.clear()
            flash("Usuario nao encontrado.", "danger")
            return redirect(url_for("login"))
        refresh_session(user)
        carteira_padrao = get_carteira_padrao(session["user_id"])
        return render_template(
            "painel.html",
            user=user,
            carteira_padrao=carteira_padrao,
        )
