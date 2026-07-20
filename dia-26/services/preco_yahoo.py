# Preco historico via Yahoo Finance (yfinance) — Dia 26
# Ticker B3: PETR4 -> PETR4.SA

from datetime import datetime, timedelta

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


def preco_no_dia(ticker: str, data_str: str) -> dict:
    """
    Busca o fechamento do dia (ou ultimo dia util anterior se feriado/fds).
    Retorna dict com preco, data_cotacao, ticker_yahoo.
    """
    ticker = (ticker or "").strip().upper()
    if not ticker:
        raise ValueError("Informe o ticker.")

    dia = parse_data_iso(data_str)
    if not dia:
        raise ValueError("Data invalida. Use AAAA-MM-DD.")

    symbol = yahoo_symbol(ticker)
    # Janela: alguns dias antes ate o dia seguinte (yfinance end e exclusivo)
    inicio = dia - timedelta(days=10)
    fim = dia + timedelta(days=2)

    hist = yf.Ticker(symbol).history(
        start=inicio.isoformat(),
        end=fim.isoformat(),
        interval="1d",
        auto_adjust=False,
    )
    if hist is None or hist.empty or "Close" not in hist.columns:
        raise ValueError(f"Sem cotacao Yahoo para {symbol} nessa data.")

    # Normaliza indice para date (sem timezone)
    closes = {}
    for idx, row in hist.iterrows():
        d = idx.date() if hasattr(idx, "date") else idx
        closes[d] = float(row["Close"])

    # Preferencia: dia exato; senao ultimo dia util <= data pedida
    if dia in closes:
        data_cotacao = dia
        preco = closes[dia]
    else:
        anteriores = [d for d in closes if d <= dia]
        if not anteriores:
            raise ValueError(f"Sem cotacao ate {dia.isoformat()} para {symbol}.")
        data_cotacao = max(anteriores)
        preco = closes[data_cotacao]

    return {
        "ticker": ticker,
        "ticker_yahoo": symbol,
        "data_pedida": dia.isoformat(),
        "data_cotacao": data_cotacao.isoformat(),
        "preco": round(preco, 2),
        "fonte": "yfinance",
    }
