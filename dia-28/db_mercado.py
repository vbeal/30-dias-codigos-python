# Cache de cotacoes e proventos (Yahoo) — Dia 28
# Dados de mercado por ticker (compartilhados); recebidos = calculados por carteira

from datetime import date, datetime, timedelta

from db import get_connection
from services.preco_yahoo import historico_diario, yahoo_symbol
import yfinance as yf


def init_mercado_tables():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cotacoes_historico (
            ticker TEXT NOT NULL,
            data TEXT NOT NULL,
            preco REAL NOT NULL,
            PRIMARY KEY (ticker, data)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS proventos_historico (
            ticker TEXT NOT NULL,
            data_ex TEXT NOT NULL,
            data_pagamento TEXT,
            valor REAL NOT NULL,
            PRIMARY KEY (ticker, data_ex, valor)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mercado_sync (
            ticker TEXT PRIMARY KEY,
            cotacoes_ate TEXT,
            proventos_sync_em TEXT,
            atualizado_em TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def _parse(s):
    try:
        return datetime.strptime((s or "")[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def ultima_cotacao_salva(ticker: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT MAX(data) AS d FROM cotacoes_historico WHERE ticker = ?",
        (ticker.upper(),),
    ).fetchone()
    conn.close()
    return _parse(row["d"]) if row and row["d"] else None


def primeira_cotacao_salva(ticker: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT MIN(data) AS d FROM cotacoes_historico WHERE ticker = ?",
        (ticker.upper(),),
    ).fetchone()
    conn.close()
    return _parse(row["d"]) if row and row["d"] else None


def ultimo_provento_salvo(ticker: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT MAX(data_ex) AS d FROM proventos_historico WHERE ticker = ?",
        (ticker.upper(),),
    ).fetchone()
    conn.close()
    return _parse(row["d"]) if row and row["d"] else None


def _ler_sync(ticker: str) -> dict:
    conn = get_connection()
    row = conn.execute(
        "SELECT cotacoes_ate, proventos_sync_em, atualizado_em FROM mercado_sync WHERE ticker = ?",
        (ticker.upper(),),
    ).fetchone()
    conn.close()
    return dict(row) if row else {}


def _gravar_sync(
    ticker: str,
    cotacoes_ate: date | None = None,
    proventos_sync_em: date | None = None,
):
    ticker = ticker.upper()
    atual = _ler_sync(ticker)
    cot = (
        cotacoes_ate.isoformat()
        if cotacoes_ate
        else atual.get("cotacoes_ate")
    )
    prov = (
        proventos_sync_em.isoformat()
        if proventos_sync_em
        else atual.get("proventos_sync_em")
    )
    agora = datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO mercado_sync (ticker, cotacoes_ate, proventos_sync_em, atualizado_em)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(ticker) DO UPDATE SET
          cotacoes_ate = excluded.cotacoes_ate,
          proventos_sync_em = excluded.proventos_sync_em,
          atualizado_em = excluded.atualizado_em
        """,
        (ticker, cot, prov, agora),
    )
    conn.commit()
    conn.close()


def salvar_cotacoes(ticker: str, closes: dict):
    """closes: {date: float}"""
    ticker = ticker.upper()
    if not closes:
        return 0
    conn = get_connection()
    n = 0
    for d, preco in closes.items():
        data = d.isoformat() if hasattr(d, "isoformat") else str(d)[:10]
        conn.execute(
            """
            INSERT INTO cotacoes_historico (ticker, data, preco)
            VALUES (?, ?, ?)
            ON CONFLICT(ticker, data) DO UPDATE SET preco = excluded.preco
            """,
            (ticker, data, float(preco)),
        )
        n += 1
    conn.commit()
    conn.close()
    return n


def salvar_proventos(ticker: str, eventos: list[dict]):
    """eventos: [{data_ex, data_pagamento, valor}, ...]"""
    ticker = ticker.upper()
    if not eventos:
        return 0
    conn = get_connection()
    n = 0
    for ev in eventos:
        data_ex = (ev.get("data_ex") or "")[:10]
        if not data_ex:
            continue
        valor = float(ev.get("valor") or 0)
        if valor <= 0:
            continue
        pag = (ev.get("data_pagamento") or data_ex)[:10]
        conn.execute(
            """
            INSERT INTO proventos_historico (ticker, data_ex, data_pagamento, valor)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(ticker, data_ex, valor) DO UPDATE SET
              data_pagamento = excluded.data_pagamento
            """,
            (ticker, data_ex, pag, valor),
        )
        n += 1
    conn.commit()
    conn.close()
    return n


def ler_cotacoes(ticker: str, data_inicio: date | None = None) -> dict:
    """Retorna {date: preco}."""
    conn = get_connection()
    if data_inicio:
        rows = conn.execute(
            """
            SELECT data, preco FROM cotacoes_historico
            WHERE ticker = ? AND data >= ?
            ORDER BY data
            """,
            (ticker.upper(), data_inicio.isoformat()),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT data, preco FROM cotacoes_historico
            WHERE ticker = ? ORDER BY data
            """,
            (ticker.upper(),),
        ).fetchall()
    conn.close()
    out = {}
    for r in rows:
        d = _parse(r["data"])
        if d:
            out[d] = float(r["preco"])
    return out


def ler_proventos(ticker: str, data_inicio: date | None = None) -> list[dict]:
    conn = get_connection()
    if data_inicio:
        rows = conn.execute(
            """
            SELECT data_ex, data_pagamento, valor FROM proventos_historico
            WHERE ticker = ? AND data_ex >= ?
            ORDER BY data_ex
            """,
            (ticker.upper(), data_inicio.isoformat()),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT data_ex, data_pagamento, valor FROM proventos_historico
            WHERE ticker = ? ORDER BY data_ex
            """,
            (ticker.upper(),),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _baixar_proventos_yahoo(ticker: str, inicio: date) -> list[dict]:
    symbol = yahoo_symbol(ticker)
    t = yf.Ticker(symbol)
    # dividends index = data ex
    try:
        divs = t.dividends
    except Exception:
        return []
    if divs is None or len(divs) == 0:
        return []
    eventos = []
    for idx, val in divs.items():
        d = idx.date() if hasattr(idx, "date") else idx
        if d < inicio:
            continue
        v = float(val)
        if v <= 0:
            continue
        eventos.append(
            {
                "data_ex": d.isoformat(),
                "data_pagamento": d.isoformat(),  # Yahoo nao traz pagamento separado
                "valor": v,
            }
        )
    return eventos


def sincronizar_ticker(
    ticker: str,
    data_inicio: date | None = None,
    forcar: bool = False,
) -> dict:
    """
    Atualiza cache so do que falta:
    - cotacoes: buraco antes do primeiro dia OU dias apos a ultima data salva ate hoje
    - proventos: so se nunca sincronizou hoje (ou forcar / cotacoes precisaram update)
    Se ja tem historico ate hoje, nao chama Yahoo.
    """
    ticker = (ticker or "").strip().upper()
    hoje = date.today()
    inicio_pedido = data_inicio or (hoje - timedelta(days=365 * 2))
    meta = _ler_sync(ticker)
    meta_cot = _parse(meta.get("cotacoes_ate"))
    prov_sync = _parse(meta.get("proventos_sync_em"))

    ult_cot = ultima_cotacao_salva(ticker)
    prim_cot = primeira_cotacao_salva(ticker)
    precisa_backfill = prim_cot is None or prim_cot > inicio_pedido

    # Ja verificamos Yahoo hoje e o historico cobre data_inicio → so le cache
    if (
        not forcar
        and not precisa_backfill
        and meta_cot
        and meta_cot >= hoje
        and prov_sync
        and prov_sync >= hoje
    ):
        return {
            "ticker": ticker,
            "cotacoes_gravadas": 0,
            "proventos_gravados": 0,
            "usou_cache": True,
        }

    n_cot = 0
    baixou_cot = False

    # Feriado/fds: se ja checamos ate hoje no meta, nao busca de novo
    precisa_frente = ult_cot is None or (
        ult_cot < hoje and (meta_cot is None or meta_cot < hoje)
    )

    if forcar or precisa_backfill or precisa_frente:
        if forcar or precisa_backfill or ult_cot is None:
            start = inicio_pedido
        else:
            start = ult_cot + timedelta(days=1)
        if start <= hoje:
            hist = historico_diario([ticker], start, hoje)
            n_cot = salvar_cotacoes(ticker, hist.get(ticker) or {})
            baixou_cot = True
        ult_cot = ultima_cotacao_salva(ticker) or ult_cot

    n_prov = 0
    precisa_prov = forcar or baixou_cot or prov_sync is None or prov_sync < hoje
    if precisa_prov:
        ult_prov = ultimo_provento_salvo(ticker)
        if ult_prov and not forcar and not precisa_backfill:
            inicio_prov = ult_prov - timedelta(days=5)
        else:
            inicio_prov = inicio_pedido
        if inicio_prov < inicio_pedido:
            inicio_prov = inicio_pedido
        eventos = _baixar_proventos_yahoo(ticker, inicio_prov)
        n_prov = salvar_proventos(ticker, eventos)

    # Marca checagem ate hoje (mesmo sem pregão) para nao bater no Yahoo de novo
    _gravar_sync(ticker, cotacoes_ate=hoje, proventos_sync_em=hoje)

    return {
        "ticker": ticker,
        "cotacoes_gravadas": n_cot,
        "proventos_gravados": n_prov,
        "usou_cache": n_cot == 0 and n_prov == 0,
    }


def sincronizar_tickers(
    tickers: list[str],
    data_inicio: date | None = None,
    forcar: bool = False,
) -> list[dict]:
    out = []
    for t in sorted({(x or "").strip().upper() for x in tickers if x}):
        try:
            out.append(sincronizar_ticker(t, data_inicio, forcar=forcar))
        except Exception as exc:
            out.append({"ticker": t, "erro": str(exc)})
    return out


def precos_atuais_cache(tickers: list[str], sincronizar: bool = True) -> dict:
    """Usa ultimo preco do cache; opcionalmente completa o que falta."""
    hoje = date.today()
    resultado = {}
    for ticker in sorted({(t or "").strip().upper() for t in tickers if t}):
        if sincronizar:
            sincronizar_ticker(ticker, hoje - timedelta(days=30))
        closes = ler_cotacoes(ticker)
        if not closes:
            resultado[ticker] = {
                "preco": None,
                "data_cotacao": None,
                "erro": "Sem cotacao em cache",
            }
            continue
        dmax = max(closes)
        resultado[ticker] = {
            "preco": round(closes[dmax], 2),
            "data_cotacao": dmax.isoformat(),
            "erro": None,
        }
    return resultado


def historico_diario_cache(
    tickers: list[str],
    data_inicio: date,
    data_fim: date | None = None,
    sincronizar: bool = True,
) -> dict:
    data_fim = data_fim or date.today()
    out = {}
    for ticker in sorted({(t or "").strip().upper() for t in tickers if t}):
        if sincronizar:
            sincronizar_ticker(ticker, data_inicio)
        closes = ler_cotacoes(ticker, data_inicio)
        out[ticker] = {d: p for d, p in closes.items() if d <= data_fim}
    return out
