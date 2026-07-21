# Precos Yahoo (Dia 26/27) — cotacao no dia, atual e historico mensal
# Ticker B3: PETR4 -> PETR4.SA

from datetime import date, datetime, timedelta

import yfinance as yf


def yahoo_symbol(ticker: str) -> str:
    t = (ticker or "").strip().upper()
    if not t.endswith(".SA"):
        t = f"{t}.SA"
    return t


def parse_data_iso(data_str: str):
    """Aceita YYYY-MM-DD. Retorna date ou None."""
    raw = (data_str or "").strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _closes_por_dia(hist) -> dict:
    closes = {}
    if hist is None or hist.empty or "Close" not in hist.columns:
        return closes
    for idx, row in hist.iterrows():
        d = idx.date() if hasattr(idx, "date") else idx
        closes[d] = float(row["Close"])
    return closes


def _preco_em_ou_antes(closes: dict, dia: date):
    if dia in closes:
        return dia, closes[dia]
    anteriores = [d for d in closes if d <= dia]
    if not anteriores:
        return None, None
    d = max(anteriores)
    return d, closes[d]


def preco_no_dia(ticker: str, data_str: str) -> dict:
    """Fechamento do dia (ou ultimo dia util anterior)."""
    ticker = (ticker or "").strip().upper()
    if not ticker:
        raise ValueError("Informe o ticker.")

    dia = parse_data_iso(data_str)
    if not dia:
        raise ValueError("Data invalida. Use AAAA-MM-DD.")

    symbol = yahoo_symbol(ticker)
    inicio = dia - timedelta(days=10)
    fim = dia + timedelta(days=2)

    hist = yf.Ticker(symbol).history(
        start=inicio.isoformat(),
        end=fim.isoformat(),
        interval="1d",
        auto_adjust=False,
    )
    closes = _closes_por_dia(hist)
    data_cotacao, preco = _preco_em_ou_antes(closes, dia)
    if preco is None:
        raise ValueError(f"Sem cotacao ate {dia.isoformat()} para {symbol}.")

    return {
        "ticker": ticker,
        "ticker_yahoo": symbol,
        "data_pedida": dia.isoformat(),
        "data_cotacao": data_cotacao.isoformat(),
        "preco": round(preco, 2),
        "fonte": "yfinance",
    }


def precos_atuais(tickers: list[str]) -> dict:
    """
    Ultimo fechamento disponivel por ticker.
    Retorno: { 'PETR4': {'preco': 39.9, 'data_cotacao': '2026-07-16', 'erro': None}, ... }
    """
    unicos = sorted({(t or "").strip().upper() for t in tickers if (t or "").strip()})
    out = {}
    if not unicos:
        return out

    hoje = date.today()
    inicio = hoje - timedelta(days=14)
    fim = hoje + timedelta(days=1)

    for ticker in unicos:
        symbol = yahoo_symbol(ticker)
        try:
            hist = yf.Ticker(symbol).history(
                start=inicio.isoformat(),
                end=fim.isoformat(),
                interval="1d",
                auto_adjust=False,
            )
            closes = _closes_por_dia(hist)
            data_cotacao, preco = _preco_em_ou_antes(closes, hoje)
            if preco is None:
                out[ticker] = {
                    "preco": None,
                    "data_cotacao": None,
                    "erro": f"Sem cotacao para {symbol}",
                }
            else:
                out[ticker] = {
                    "preco": round(preco, 2),
                    "data_cotacao": data_cotacao.isoformat(),
                    "erro": None,
                }
        except Exception as exc:
            out[ticker] = {"preco": None, "data_cotacao": None, "erro": str(exc)}
    return out


def historico_diario(tickers: list[str], data_inicio: date, data_fim: date | None = None) -> dict:
    """
    Historico diario Close por ticker.
    Retorno: { 'MXRF11': { date: float, ... }, ... }
    """
    data_fim = data_fim or date.today()
    unicos = sorted({(t or "").strip().upper() for t in tickers if (t or "").strip()})
    resultado = {t: {} for t in unicos}
    if not unicos:
        return resultado

    inicio = data_inicio - timedelta(days=5)
    fim = data_fim + timedelta(days=2)

    for ticker in unicos:
        symbol = yahoo_symbol(ticker)
        try:
            hist = yf.Ticker(symbol).history(
                start=inicio.isoformat(),
                end=fim.isoformat(),
                interval="1d",
                auto_adjust=False,
            )
            resultado[ticker] = _closes_por_dia(hist)
        except Exception:
            resultado[ticker] = {}
    return resultado
