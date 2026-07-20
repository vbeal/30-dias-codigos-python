# ###################################################################
#          🎯 Projeto: Login com SQLite (Dia 21)                   #
# ###################################################################
# 📁 Caminho: dia-21/dia21_app_login.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: flask (web), sqlite3 (banco local), werkzeug (hash)
# 🔗 Instalação: pip install flask
# 💾 Banco: database/app.db (criado automaticamente)
# ###################################################################

from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import SECRET_KEY
from db import create_user, init_db, verify_user

app = Flask(__name__)
app.secret_key = SECRET_KEY


# Bloqueia paginas que exigem usuario logado
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Faca login para acessar esta pagina.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


# Redireciona para o painel se ja estiver logado
def redirect_if_logged_in():
    if "user_id" in session:
        return redirect(url_for("painel"))
    return None


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("painel"))
    return redirect(url_for("login"))


# Pagina de cadastro de novo usuario
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


# Pagina de login
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
                session["user_id"] = user["id"]
                session["user_nome"] = user["nome"]
                session["user_email"] = user["email"]
                flash(message, "success")
                return redirect(url_for("painel"))
            flash(message, "danger")

    return render_template("login.html")


# Encerra a sessao do usuario
@app.route("/logout")
def logout():
    session.clear()
    flash("Voce saiu da sua conta.", "info")
    return redirect(url_for("login"))


# Area protegida — so acessivel apos login
@app.route("/painel")
@login_required
def painel():
    return render_template("painel.html")


if __name__ == "__main__":
    init_db()
    print("\n" + "=" * 50)
    print("  Sistema de Login - Dia 21")
    print("  Acesse: http://localhost:5000/")
    print("  Banco SQLite: database/app.db")
    print("  Ctrl+C para encerrar")
    print("=" * 50 + "\n")
    app.run(debug=True)
