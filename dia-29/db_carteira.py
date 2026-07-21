# CRUD de carteiras e lancamentos (Dia 26)
# Tabelas: carteiras (varias por usuario, 1 padrao) + lancamentos

from db import get_connection


def _ensure_column(conn, table, column, definition):
    cols = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _garantir_uma_padrao(conn, usuario_id):
    """Garante exatamente uma carteira padrao (se existir alguma)."""
    row = conn.execute(
        """
        SELECT id FROM carteiras
        WHERE usuario_id = ? AND COALESCE(eh_padrao, 0) = 1
        ORDER BY id LIMIT 1
        """,
        (usuario_id,),
    ).fetchone()
    if row:
        conn.execute(
            """
            UPDATE carteiras SET eh_padrao = 0
            WHERE usuario_id = ? AND id != ?
            """,
            (usuario_id, row["id"]),
        )
        conn.execute(
            "UPDATE carteiras SET eh_padrao = 1 WHERE id = ?",
            (row["id"],),
        )
        return

    primeira = conn.execute(
        "SELECT id FROM carteiras WHERE usuario_id = ? ORDER BY id LIMIT 1",
        (usuario_id,),
    ).fetchone()
    if primeira:
        conn.execute(
            "UPDATE carteiras SET eh_padrao = 1 WHERE id = ?",
            (primeira["id"],),
        )


def init_carteira_tables():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS carteiras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            eh_padrao INTEGER NOT NULL DEFAULT 0,
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )
    _ensure_column(conn, "carteiras", "eh_padrao", "INTEGER NOT NULL DEFAULT 0")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carteira_id INTEGER NOT NULL,
            operacao TEXT NOT NULL CHECK (operacao IN ('compra', 'venda')),
            ticker TEXT NOT NULL,
            tipo_ativo TEXT NOT NULL CHECK (tipo_ativo IN ('fii', 'acao')),
            data_transacao TEXT NOT NULL,
            quantidade REAL NOT NULL,
            preco REAL NOT NULL,
            outros_custos REAL NOT NULL DEFAULT 0,
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (carteira_id) REFERENCES carteiras(id) ON DELETE CASCADE
        )
        """
    )
    usuarios = conn.execute("SELECT DISTINCT usuario_id FROM carteiras").fetchall()
    for u in usuarios:
        _garantir_uma_padrao(conn, u["usuario_id"])
    conn.commit()
    conn.close()


def listar_carteiras(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT c.id, c.nome, c.criado_em, COALESCE(c.eh_padrao, 0) AS eh_padrao,
               (SELECT COUNT(*) FROM lancamentos l WHERE l.carteira_id = c.id) AS qtd_lancamentos
        FROM carteiras c
        WHERE c.usuario_id = ?
        ORDER BY COALESCE(c.eh_padrao, 0) DESC, c.nome COLLATE NOCASE
        """,
        (usuario_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_carteira_padrao(usuario_id):
    conn = get_connection()
    _garantir_uma_padrao(conn, usuario_id)
    conn.commit()
    row = conn.execute(
        """
        SELECT id, usuario_id, nome, COALESCE(eh_padrao, 0) AS eh_padrao, criado_em
        FROM carteiras
        WHERE usuario_id = ? AND COALESCE(eh_padrao, 0) = 1
        LIMIT 1
        """,
        (usuario_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def criar_carteira(usuario_id, nome):
    nome = (nome or "").strip()
    if not nome:
        return False, None, "Informe o nome da carteira."
    if len(nome) > 80:
        return False, None, "Nome muito longo (max. 80)."

    conn = get_connection()
    qtd = conn.execute(
        "SELECT COUNT(*) AS n FROM carteiras WHERE usuario_id = ?",
        (usuario_id,),
    ).fetchone()["n"]
    # Primeira carteira vira padrao automaticamente
    eh_padrao = 1 if qtd == 0 else 0

    cur = conn.execute(
        "INSERT INTO carteiras (usuario_id, nome, eh_padrao) VALUES (?, ?, ?)",
        (usuario_id, nome, eh_padrao),
    )
    conn.commit()
    carteira_id = cur.lastrowid
    conn.close()
    msg = (
        "Carteira cadastrada e definida como padrao."
        if eh_padrao
        else "Carteira cadastrada."
    )
    return True, carteira_id, msg


def get_carteira(carteira_id, usuario_id):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT id, usuario_id, nome, COALESCE(eh_padrao, 0) AS eh_padrao, criado_em
        FROM carteiras
        WHERE id = ? AND usuario_id = ?
        """,
        (carteira_id, usuario_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def definir_carteira_padrao(carteira_id, usuario_id):
    if not get_carteira(carteira_id, usuario_id):
        return False, "Carteira nao encontrada."

    conn = get_connection()
    conn.execute(
        "UPDATE carteiras SET eh_padrao = 0 WHERE usuario_id = ?",
        (usuario_id,),
    )
    conn.execute(
        "UPDATE carteiras SET eh_padrao = 1 WHERE id = ? AND usuario_id = ?",
        (carteira_id, usuario_id),
    )
    conn.commit()
    conn.close()
    return True, "Carteira definida como padrao."


def renomear_carteira(carteira_id, usuario_id, nome):
    nome = (nome or "").strip()
    if not nome:
        return False, "Informe o nome da carteira."
    if not get_carteira(carteira_id, usuario_id):
        return False, "Carteira nao encontrada."

    conn = get_connection()
    conn.execute(
        "UPDATE carteiras SET nome = ? WHERE id = ? AND usuario_id = ?",
        (nome, carteira_id, usuario_id),
    )
    conn.commit()
    conn.close()
    return True, "Carteira renomeada."


def apagar_carteira(carteira_id, usuario_id):
    carteira = get_carteira(carteira_id, usuario_id)
    if not carteira:
        return False, "Carteira nao encontrada."

    era_padrao = bool(carteira.get("eh_padrao"))
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        "DELETE FROM lancamentos WHERE carteira_id = ?",
        (carteira_id,),
    )
    conn.execute(
        "DELETE FROM carteiras WHERE id = ? AND usuario_id = ?",
        (carteira_id, usuario_id),
    )
    if era_padrao:
        _garantir_uma_padrao(conn, usuario_id)
    conn.commit()
    conn.close()
    return True, "Carteira apagada."


def listar_lancamentos(carteira_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, operacao, ticker, tipo_ativo, data_transacao,
               quantidade, preco, outros_custos, criado_em,
               (quantidade * preco + outros_custos) AS valor_total
        FROM lancamentos
        WHERE carteira_id = ?
        ORDER BY data_transacao DESC, id DESC
        """,
        (carteira_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def quantidade_liquida(carteira_id, ticker):
    """Compras - vendas do ticker na carteira."""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT
          COALESCE(SUM(CASE WHEN operacao = 'compra' THEN quantidade ELSE 0 END), 0)
        - COALESCE(SUM(CASE WHEN operacao = 'venda' THEN quantidade ELSE 0 END), 0)
          AS qtd
        FROM lancamentos
        WHERE carteira_id = ? AND ticker = ?
        """,
        (carteira_id, ticker.upper()),
    ).fetchone()
    conn.close()
    return float(row["qtd"] if row else 0)


def parse_money_br(valor) -> float:
    """Aceita 10.5, 10,50, 1.234,56 (pt-BR) ou float."""
    if valor is None or valor == "":
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip().replace("R$", "").replace(" ", "")
    if not s:
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return float(s)


def adicionar_lancamento(
    carteira_id,
    usuario_id,
    operacao,
    ticker,
    tipo_ativo,
    data_transacao,
    quantidade,
    preco,
    outros_custos=0,
):
    if not get_carteira(carteira_id, usuario_id):
        return False, "Carteira nao encontrada."

    operacao = (operacao or "").strip().lower()
    if operacao not in ("compra", "venda"):
        return False, "Operacao invalida (compra ou venda)."

    ticker = (ticker or "").strip().upper()
    tipo_ativo = (tipo_ativo or "").strip().lower()
    if tipo_ativo not in ("fii", "acao"):
        return False, "Tipo de ativo invalido."

    data_transacao = (data_transacao or "").strip()
    if not data_transacao:
        return False, "Informe a data da transacao."

    try:
        quantidade = float(str(quantidade).replace(",", "."))
        preco = parse_money_br(preco)
        outros_custos = parse_money_br(outros_custos)
    except (TypeError, ValueError):
        return False, "Quantidade, preco ou custos invalidos."

    if quantidade <= 0:
        return False, "Quantidade deve ser maior que zero."
    if preco < 0 or outros_custos < 0:
        return False, "Preco e custos nao podem ser negativos."

    if operacao == "venda":
        disponivel = quantidade_liquida(carteira_id, ticker)
        if quantidade > disponivel + 1e-9:
            return False, f"Venda maior que a posicao ({disponivel:g} disponiveis)."

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO lancamentos
          (carteira_id, operacao, ticker, tipo_ativo, data_transacao,
           quantidade, preco, outros_custos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            carteira_id,
            operacao,
            ticker,
            tipo_ativo,
            data_transacao,
            quantidade,
            preco,
            outros_custos,
        ),
    )
    conn.commit()
    conn.close()
    return True, "Lancamento cadastrado."


def apagar_lancamento(lancamento_id, carteira_id, usuario_id):
    if not get_carteira(carteira_id, usuario_id):
        return False, "Carteira nao encontrada."

    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM lancamentos WHERE id = ? AND carteira_id = ?",
        (lancamento_id, carteira_id),
    )
    conn.commit()
    apagou = cur.rowcount > 0
    conn.close()
    if not apagou:
        return False, "Lancamento nao encontrado."
    return True, "Lancamento removido."
