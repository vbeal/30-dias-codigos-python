# CRUD do Radar (Dia 29) — acompanhamento de ativos por periodo e niveis

from db import get_connection


def init_radar_tables():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS radares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT NOT NULL,
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS radar_ativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            radar_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            tipo_ativo TEXT NOT NULL CHECK (tipo_ativo IN ('fii', 'acao')),
            direcao TEXT NOT NULL CHECK (direcao IN ('compra', 'venda')),
            preco_entrada REAL NOT NULL,
            preco_teto REAL NOT NULL,
            preco_alvo REAL NOT NULL,
            preco_stop REAL NOT NULL,
            preco_corte REAL NOT NULL,
            ordem INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (radar_id) REFERENCES radares(id) ON DELETE CASCADE
        )
        """
    )
    # Preparado para cron / historico (proxima etapa)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS radar_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            radar_ativo_id INTEGER NOT NULL,
            coletado_em TEXT NOT NULL,
            preco REAL NOT NULL,
            intervalo TEXT NOT NULL CHECK (intervalo IN ('15m', '1d')),
            status TEXT,
            FOREIGN KEY (radar_ativo_id) REFERENCES radar_ativos(id) ON DELETE CASCADE,
            UNIQUE (radar_ativo_id, coletado_em, intervalo)
        )
        """
    )
    conn.commit()
    conn.close()


def listar_radares(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT r.id, r.nome, r.data_inicio, r.data_fim, r.criado_em,
               (SELECT COUNT(*) FROM radar_ativos a WHERE a.radar_id = r.id) AS qtd_ativos
        FROM radares r
        WHERE r.usuario_id = ?
        ORDER BY r.data_inicio DESC, r.id DESC
        """,
        (usuario_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_radar(radar_id, usuario_id):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT id, usuario_id, nome, data_inicio, data_fim, criado_em
        FROM radares
        WHERE id = ? AND usuario_id = ?
        """,
        (radar_id, usuario_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def listar_ativos_radar(radar_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, radar_id, ticker, tipo_ativo, direcao,
               preco_entrada, preco_teto, preco_alvo, preco_stop, preco_corte, ordem
        FROM radar_ativos
        WHERE radar_id = ?
        ORDER BY ordem, id
        """,
        (radar_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def criar_radar(usuario_id, nome, data_inicio, data_fim, ativos):
    """Cria radar + lista de ativos. ativos = list[dict]."""
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        cur = conn.execute(
            """
            INSERT INTO radares (usuario_id, nome, data_inicio, data_fim)
            VALUES (?, ?, ?, ?)
            """,
            (usuario_id, nome, data_inicio, data_fim),
        )
        radar_id = cur.lastrowid
        _inserir_ativos(conn, radar_id, ativos)
        conn.commit()
        return True, radar_id, "Radar criado com sucesso."
    except Exception as exc:
        conn.rollback()
        return False, None, f"Erro ao criar radar: {exc}"
    finally:
        conn.close()


def atualizar_radar(radar_id, usuario_id, nome, data_inicio, data_fim, ativos):
    """Atualiza cabecalho e substitui a lista de ativos."""
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        row = conn.execute(
            "SELECT id FROM radares WHERE id = ? AND usuario_id = ?",
            (radar_id, usuario_id),
        ).fetchone()
        if not row:
            return False, "Radar nao encontrado."

        conn.execute(
            """
            UPDATE radares
            SET nome = ?, data_inicio = ?, data_fim = ?
            WHERE id = ? AND usuario_id = ?
            """,
            (nome, data_inicio, data_fim, radar_id, usuario_id),
        )
        conn.execute("DELETE FROM radar_ativos WHERE radar_id = ?", (radar_id,))
        _inserir_ativos(conn, radar_id, ativos)
        conn.commit()
        return True, "Radar atualizado."
    except Exception as exc:
        conn.rollback()
        return False, f"Erro ao atualizar radar: {exc}"
    finally:
        conn.close()


def apagar_radar(radar_id, usuario_id):
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.execute(
        "DELETE FROM radares WHERE id = ? AND usuario_id = ?",
        (radar_id, usuario_id),
    )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return (True, "Radar apagado.") if ok else (False, "Radar nao encontrado.")


def _inserir_ativos(conn, radar_id, ativos):
    for i, a in enumerate(ativos):
        conn.execute(
            """
            INSERT INTO radar_ativos (
                radar_id, ticker, tipo_ativo, direcao,
                preco_entrada, preco_teto, preco_alvo, preco_stop, preco_corte, ordem
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                radar_id,
                a["ticker"],
                a["tipo_ativo"],
                a["direcao"],
                a["preco_entrada"],
                a["preco_teto"],
                a["preco_alvo"],
                a["preco_stop"],
                a["preco_corte"],
                i,
            ),
        )


def limpar_snapshots_radar(radar_id):
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        DELETE FROM radar_snapshots
        WHERE radar_ativo_id IN (
            SELECT id FROM radar_ativos WHERE radar_id = ?
        )
        """,
        (radar_id,),
    )
    conn.commit()
    conn.close()


def substituir_snapshots_ativo(radar_ativo_id, snapshots):
    """Apaga snapshots do ativo e grava a lista nova."""
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.execute(
            "DELETE FROM radar_snapshots WHERE radar_ativo_id = ?",
            (radar_ativo_id,),
        )
        for s in snapshots:
            conn.execute(
                """
                INSERT OR REPLACE INTO radar_snapshots
                    (radar_ativo_id, coletado_em, preco, intervalo, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    radar_ativo_id,
                    s["coletado_em"],
                    s["preco"],
                    s["intervalo"],
                    s.get("status"),
                ),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def contar_snapshots_radar(radar_id):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT COUNT(*) AS n
        FROM radar_snapshots s
        JOIN radar_ativos a ON a.id = s.radar_ativo_id
        WHERE a.radar_id = ?
        """,
        (radar_id,),
    ).fetchone()
    conn.close()
    return int(row["n"] if row else 0)


def listar_snapshots(
    radar_id,
    ticker=None,
    intervalo=None,
    data_inicio=None,
    data_fim=None,
    page=1,
    per_page=50,
):
    """Lista paginada de logs (mais recente primeiro)."""
    page = max(1, int(page or 1))
    per_page = max(1, min(200, int(per_page or 50)))
    offset = (page - 1) * per_page

    where = ["a.radar_id = ?"]
    params = [radar_id]
    if ticker:
        where.append("a.ticker = ?")
        params.append(ticker.upper())
    if intervalo:
        where.append("s.intervalo = ?")
        params.append(intervalo)
    if data_inicio:
        where.append("s.coletado_em >= ?")
        params.append(f"{data_inicio} 00:00:00")
    if data_fim:
        where.append("s.coletado_em <= ?")
        params.append(f"{data_fim} 23:59:59")

    clause = " AND ".join(where)
    conn = get_connection()
    total = conn.execute(
        f"""
        SELECT COUNT(*) AS n
        FROM radar_snapshots s
        JOIN radar_ativos a ON a.id = s.radar_ativo_id
        WHERE {clause}
        """,
        params,
    ).fetchone()["n"]

    rows = conn.execute(
        f"""
        SELECT s.id, s.coletado_em, s.preco, s.intervalo, s.status,
               a.ticker, a.direcao, a.id AS radar_ativo_id
        FROM radar_snapshots s
        JOIN radar_ativos a ON a.id = s.radar_ativo_id
        WHERE {clause}
        ORDER BY s.coletado_em DESC, s.id DESC
        LIMIT ? OFFSET ?
        """,
        params + [per_page, offset],
    ).fetchall()
    conn.close()
    return {
        "total": int(total),
        "page": page,
        "per_page": per_page,
        "pages": max(1, (int(total) + per_page - 1) // per_page),
        "itens": [dict(r) for r in rows],
    }


def listar_snapshots_serie(
    radar_id,
    ticker,
    intervalo,
    data_inicio,
    data_fim,
):
    """Serie cronologica (para grafico)."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT s.coletado_em, s.preco, s.intervalo, s.status
        FROM radar_snapshots s
        JOIN radar_ativos a ON a.id = s.radar_ativo_id
        WHERE a.radar_id = ?
          AND a.ticker = ?
          AND s.intervalo = ?
          AND s.coletado_em >= ?
          AND s.coletado_em <= ?
        ORDER BY s.coletado_em ASC, s.id ASC
        """,
        (
            radar_id,
            ticker.upper(),
            intervalo,
            f"{data_inicio} 00:00:00",
            f"{data_fim} 23:59:59",
        ),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_snapshot(radar_ativo_id, coletado_em, preco, intervalo, status):
    """Insere ou atualiza um ponto (cron ao vivo / sync pontual)."""
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        INSERT INTO radar_snapshots
            (radar_ativo_id, coletado_em, preco, intervalo, status)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(radar_ativo_id, coletado_em, intervalo)
        DO UPDATE SET preco = excluded.preco, status = excluded.status
        """,
        (radar_ativo_id, coletado_em, preco, intervalo, status),
    )
    conn.commit()
    conn.close()


def listar_radares_vigentes(hoje=None):
    """Radares com hoje entre data_inicio e data_fim (qualquer usuario)."""
    from datetime import date as date_cls

    if hoje is None:
        hoje = date_cls.today().isoformat()
    elif hasattr(hoje, "isoformat"):
        hoje = hoje.isoformat()
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, usuario_id, nome, data_inicio, data_fim, criado_em
        FROM radares
        WHERE date(data_inicio) <= date(?)
          AND date(data_fim) >= date(?)
        ORDER BY id
        """,
        (hoje, hoje),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def listar_snapshots_log(radar_id, ticker=None, limite_15m=None, page=1, per_page=50):
    """
    15m sempre; 1d so quando a data < limite_15m (fora da janela Yahoo).
    """
    page = max(1, int(page or 1))
    per_page = max(1, min(200, int(per_page or 50)))
    offset = (page - 1) * per_page
    lim = limite_15m or "1970-01-01"

    where = [
        "a.radar_id = ?",
        """(
            s.intervalo = '15m'
            OR (s.intervalo = '1d' AND date(s.coletado_em) < date(?))
        )""",
    ]
    params = [radar_id, lim]
    if ticker:
        where.append("a.ticker = ?")
        params.append(ticker.upper())

    clause = " AND ".join(where)
    conn = get_connection()
    total = conn.execute(
        f"""
        SELECT COUNT(*) AS n
        FROM radar_snapshots s
        JOIN radar_ativos a ON a.id = s.radar_ativo_id
        WHERE {clause}
        """,
        params,
    ).fetchone()["n"]

    rows = conn.execute(
        f"""
        SELECT s.id, s.coletado_em, s.preco, s.intervalo, s.status,
               a.ticker, a.direcao, a.id AS radar_ativo_id,
               a.preco_entrada, a.preco_teto, a.preco_alvo,
               a.preco_stop, a.preco_corte
        FROM radar_snapshots s
        JOIN radar_ativos a ON a.id = s.radar_ativo_id
        WHERE {clause}
        ORDER BY s.coletado_em DESC, s.id DESC
        LIMIT ? OFFSET ?
        """,
        params + [per_page, offset],
    ).fetchall()
    conn.close()
    return {
        "total": int(total),
        "page": page,
        "per_page": per_page,
        "pages": max(1, (int(total) + per_page - 1) // per_page),
        "itens": [dict(r) for r in rows],
    }
