# Rotas: index, cadastro, login, logout

from flask import flash, redirect, render_template, request, session, url_for

from db import create_user, verify_user
from web.helpers import redirect_if_logged_in, refresh_session


def register(app):
    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("painel"))
        return redirect(url_for("login"))

    @app.route("/cadastro", methods=["GET", "POST"])
    def cadastro():
        redirect_response = redirect_if_logged_in()
        if redirect_response:
            return redirect_response

        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "")
            confirmar = request.form.get("confirmar", "")

            if not nome or not email or not senha:
                flash("Preencha todos os campos.", "danger")
            elif len(senha) < 6:
                flash("A senha deve ter pelo menos 6 caracteres.", "danger")
            elif senha != confirmar:
                flash("As senhas nao conferem.", "danger")
            else:
                ok, message = create_user(nome, email, senha)
                flash(message, "success" if ok else "danger")
                if ok:
                    return redirect(url_for("login"))

        return render_template("cadastro.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        redirect_response = redirect_if_logged_in()
        if redirect_response:
            return redirect_response

        if request.method == "POST":
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "")

            if not email or not senha:
                flash("Preencha e-mail e senha.", "danger")
            else:
                ok, user, message = verify_user(email, senha)
                if ok:
                    refresh_session(user)
                    flash(message, "success")
                    return redirect(url_for("painel"))
                flash(message, "danger")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Voce saiu da sua conta.", "info")
        return redirect(url_for("login"))
