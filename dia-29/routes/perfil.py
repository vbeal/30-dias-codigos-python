# Rotas: perfil + uploads

from flask import flash, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.utils import secure_filename

from db import (
    clear_foto,
    get_user_by_id,
    update_foto,
    update_password,
    update_profile,
)
from web.helpers import (
    UPLOAD_DIR,
    allowed_file,
    delete_foto_file,
    ensure_upload_dir,
    login_required,
    refresh_session,
)

ABAS_PERFIL = {"dados", "senha", "foto"}


def aba_perfil(valor=None):
    aba = valor or request.form.get("aba") or request.args.get("aba") or "dados"
    return aba if aba in ABAS_PERFIL else "dados"


def register(app):
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

            elif acao == "foto":
                arquivo = request.files.get("foto")
                if not arquivo or arquivo.filename == "":
                    flash("Selecione uma imagem para enviar.", "danger")
                elif not allowed_file(arquivo.filename):
                    flash("Formato invalido. Use: png, jpg, jpeg, gif ou webp.", "danger")
                else:
                    ensure_upload_dir()
                    ext = arquivo.filename.rsplit(".", 1)[1].lower()
                    filename = secure_filename(f"user_{user['id']}.{ext}")
                    delete_foto_file(user["foto"])
                    arquivo.save(UPLOAD_DIR / filename)
                    ok, message = update_foto(user["id"], filename)
                    flash(message, "success" if ok else "danger")
                    user = get_user_by_id(user["id"])
                    refresh_session(user)

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

    @app.route("/uploads/<path:filename>")
    @login_required
    def uploaded_file(filename):
        return send_from_directory(UPLOAD_DIR, filename)
