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


# Garante coluna nova sem quebrar banco ja criado no Dia 21
def _ensure_column(conn, table, column, definition):
    cols = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


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
    # Novidade Dia 22: coluna para nome do arquivo da foto de perfil
    _ensure_column(conn, "usuarios", "foto", "TEXT")
    conn.commit()
    conn.close()

    # Criar tabela de carteiras
    # Novidade Dia 26: carteiras + lancamentos
    from db_carteira import init_carteira_tables

    init_carteira_tables()
    # Novidade Dia 28: cache cotacoes + proventos (Yahoo)
    from db_mercado import init_mercado_tables

    init_mercado_tables()


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
        "SELECT id, nome, email, senha_hash, foto FROM usuarios WHERE email = ?",
        (email.strip().lower(),),
    ).fetchone()
    conn.close()
    return user


# Novidade Dia 22: busca usuario pelo id (painel e perfil)
def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, nome, email, senha_hash, foto, criado_em FROM usuarios WHERE id = ?",
        (user_id,),
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


# Novidade Dia 22: atualiza nome e e-mail do perfil
def update_profile(user_id, nome, email):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE usuarios SET nome = ?, email = ? WHERE id = ?",
            (nome.strip(), email.strip().lower(), user_id),
        )
        conn.commit()
        return True, "Dados do perfil atualizados."
    except sqlite3.IntegrityError:
        return False, "Este e-mail ja esta em uso por outra conta."
    finally:
        conn.close()


# Novidade Dia 22: trocar senha (exige senha atual correta)
def update_password(user_id, senha_atual, senha_nova):
    user = get_user_by_id(user_id)
    if not user:
        return False, "Usuario nao encontrado."

    if not check_password_hash(user["senha_hash"], senha_atual):
        return False, "Senha atual incorreta."

    if len(senha_nova) < 6:
        return False, "A nova senha deve ter pelo menos 6 caracteres."

    conn = get_connection()
    conn.execute(
        "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
        (generate_password_hash(senha_nova), user_id),
    )
    conn.commit()
    conn.close()
    return True, "Senha atualizada com sucesso."


# Novidade Dia 22: grava o nome do arquivo da foto no banco
def update_foto(user_id, filename):
    conn = get_connection()
    conn.execute("UPDATE usuarios SET foto = ? WHERE id = ?", (filename, user_id))
    conn.commit()
    conn.close()
    return True, "Foto de perfil atualizada."


# Novidade Dia 22: remove a referencia da foto no banco (arquivo apagado na rota)
def clear_foto(user_id):
    conn = get_connection()
    conn.execute("UPDATE usuarios SET foto = NULL WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True, "Foto de perfil removida."
