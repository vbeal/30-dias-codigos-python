# ###################################################################
#          🎯 Projeto: Perfil + Foto (Dia 22)                      #
# ###################################################################
# 📁 Caminho: dia-22/dia22_app_login.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# Continua o Dia 21 (login/cadastro/sessao) e adiciona:
# - CRUD de perfil (editar nome e e-mail)
# - Atualizar senha
# - Upload / trocar / remover foto de perfil
# ###################################################################
# 📚 Bibliotecas: flask (web), sqlite3 (banco), werkzeug (hash + upload)
# 🔗 Instalação: pip install flask
# 💾 Banco: database/app.db | Fotos: static/uploads/
# ###################################################################

from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, SECRET_KEY, UPLOAD_FOLDER
from db import (
    clear_foto,
    create_user,
    get_user_by_id,
    init_db,
    update_foto,
    update_password,
    update_profile,
    verify_user,
)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / UPLOAD_FOLDER


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


# Atualiza dados basicos da sessao apos editar perfil/login
def refresh_session(user):
    session["user_id"] = user["id"]
    session["user_nome"] = user["nome"]
    session["user_email"] = user["email"]
    # Novidade Dia 22: foto na sessao (None se nao houver)
    session["user_foto"] = user["foto"] if user["foto"] else None


# Verifica se a extensao da imagem e permitida
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Remove arquivo antigo da pasta de uploads, se existir
def delete_foto_file(filename):
    if not filename:
        return
    path = UPLOAD_DIR / filename
    if path.is_file():
        path.unlink()


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
                refresh_session(user)
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
    # Novidade Dia 22: busca dados atualizados do banco (inclui foto)
    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        flash("Usuario nao encontrado.", "danger")
        return redirect(url_for("login"))
    refresh_session(user)
    return render_template("painel.html", user=user)


# Abas validas da pagina de perfil (Navs & tabs do Bootstrap)
ABAS_PERFIL = {"dados", "senha", "foto"}


def aba_perfil(valor=None):
    aba = valor or request.form.get("aba") or request.args.get("aba") or "dados"
    return aba if aba in ABAS_PERFIL else "dados"


# --- Novidade Dia 22: pagina de atualizar perfil ---
@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        flash("Usuario nao encontrado.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        acao = request.form.get("acao", "")
        aba = aba_perfil()

        # Editar nome e e-mail
        if acao == "dados":
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()
            if not nome or not email:
                flash("Preencha nome e e-mail.", "danger")
            else:
                ok, message = update_profile(user["id"], nome, email)
                flash(message, "success" if ok else "danger")
                if ok:
                    user = get_user_by_id(user["id"])
                    refresh_session(user)

        # Trocar senha
        elif acao == "senha":
            senha_atual = request.form.get("senha_atual", "")
            senha_nova = request.form.get("senha_nova", "")
            confirmar = request.form.get("confirmar", "")
            if not senha_atual or not senha_nova or not confirmar:
                flash("Preencha todos os campos de senha.", "danger")
            elif senha_nova != confirmar:
                flash("A nova senha e a confirmacao nao conferem.", "danger")
            else:
                ok, message = update_password(user["id"], senha_atual, senha_nova)
                flash(message, "success" if ok else "danger")

        # Upload / trocar foto
        elif acao == "foto":
            arquivo = request.files.get("foto")
            if not arquivo or arquivo.filename == "":
                flash("Selecione uma imagem para enviar.", "danger")
            elif not allowed_file(arquivo.filename):
                flash("Formato invalido. Use: png, jpg, jpeg, gif ou webp.", "danger")
            else:
                UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
                ext = arquivo.filename.rsplit(".", 1)[1].lower()
                filename = secure_filename(f"user_{user['id']}.{ext}")
                # Apaga foto anterior (mesmo usuario, outra extensao)
                delete_foto_file(user["foto"])
                arquivo.save(UPLOAD_DIR / filename)
                ok, message = update_foto(user["id"], filename)
                flash(message, "success" if ok else "danger")
                user = get_user_by_id(user["id"])
                refresh_session(user)

        # Remover foto
        elif acao == "remover_foto":
            if not user["foto"]:
                flash("Nao ha foto para remover.", "warning")
            else:
                delete_foto_file(user["foto"])
                ok, message = clear_foto(user["id"])
                flash(message, "success" if ok else "danger")
                user = get_user_by_id(user["id"])
                refresh_session(user)

        return redirect(url_for("perfil", aba=aba))

    return render_template("perfil.html", user=user, aba=aba_perfil())


# Serve as fotos enviadas (pasta static/uploads)
@app.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == "__main__":
    init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print("\n" + "=" * 50)
    print("  Sistema de Perfil - Dia 22")
    print("  Acesse: http://localhost:5000/")
    print("  Banco SQLite: database/app.db")
    print("  Fotos: static/uploads/")
    print("  Ctrl+C para encerrar")
    print("=" * 50 + "\n")
    app.run(debug=True)
