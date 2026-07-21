# Helpers compartilhados das rotas (auth, upload, mapa de ativos)

import json
from functools import wraps
from pathlib import Path

from flask import flash, redirect, session, url_for

from config import ALLOWED_EXTENSIONS, ATIVOS, UPLOAD_FOLDER
from db_carteira import listar_carteiras
from web.timezone_util import ano_atual_sp

ATIVOS_POR_TICKER = {a["ticker"].upper(): a for a in ATIVOS}

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / UPLOAD_FOLDER


def inject_globals():
    dados = {
        "current_year": ano_atual_sp(),
        "ativos_json": json.dumps(ATIVOS, ensure_ascii=False),
        "carteiras_usuario": [],
    }
    uid = session.get("user_id")
    if uid:
        dados["carteiras_usuario"] = listar_carteiras(uid)
    return dados


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Faca login para acessar esta pagina.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def redirect_if_logged_in():
    if "user_id" in session:
        return redirect(url_for("painel"))
    return None


def refresh_session(user):
    session["user_id"] = user["id"]
    session["user_nome"] = user["nome"]
    session["user_email"] = user["email"]
    session["user_foto"] = user["foto"] if user["foto"] else None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_foto_file(filename):
    if not filename:
        return
    path = UPLOAD_DIR / filename
    if path.is_file():
        path.unlink()


def ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
