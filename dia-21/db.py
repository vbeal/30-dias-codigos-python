import sqlite3
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

from config import DATABASE_PATH

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / DATABASE_PATH


# Abre conexao com o SQLite (cria o arquivo se nao existir)
def get_connection():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# Cria a tabela de usuarios na primeira execucao
def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
        """
    )
    conn.commit()
    conn.close()


# Cadastra um novo usuario com senha em hash
def create_user(nome, email, senha):
    senha_hash = generate_password_hash(senha)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (nome.strip(), email.strip().lower(), senha_hash),
        )
        conn.commit()
        return True, "Cadastro realizado com sucesso."
    except sqlite3.IntegrityError:
        return False, "Este e-mail ja esta cadastrado."
    finally:
        conn.close()


# Busca usuario pelo e-mail
def get_user_by_email(email):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?",
        (email.strip().lower(),),
    ).fetchone()
    conn.close()
    return user


# Valida e-mail e senha no login
def verify_user(email, senha):
    user = get_user_by_email(email)
    if not user:
        return False, None, "E-mail ou senha incorretos."

    if not check_password_hash(user["senha_hash"], senha):
        return False, None, "E-mail ou senha incorretos."

    return True, dict(user), "Login realizado com sucesso."
