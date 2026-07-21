# Busca Yahoo 15m / 1d para o Radar (limites: 15m ~60 dias)

from datetime import date, datetime, timedelta, time

import yfinance as yf

from services.preco_yahoo import yahoo_symbol
from web.timezone_util import hoje_sp

YAHOO_15M_DIAS = 60
HORA_PREGAO_INI = time(10, 0)
HORA_PREGAO_FIM = time(18, 0)


def limite_15m(hoje=None):
    """Primeira data em que ainda ha barras 15m no Yahoo."""
    hoje = hoje or hoje_sp()
    return hoje - timedelta(days=YAHOO_15M_DIAS)


def dias_periodo(data_inicio, data_fim):
    return (data_fim - data_inicio).days + 1


def resolucao_grafico(data_inicio, data_fim):
    """<=7 dias -> 15m; acima -> 1d."""
    return "15m" if dias_periodo(data_inicio, data_fim) <= 7 else "1d"


def semanas_do_periodo(data_inicio, data_fim):
    """Lista de semanas (seg-dom) que cruzam o periodo do radar."""
    # weekday: Mon=0
    cursor = data_inicio - timedelta(days=data_inicio.weekday())
    semanas = []
    idx = 1
    while cursor <= data_fim:
        fim_sem = cursor + timedelta(days=6)
        ini = max(cursor, data_inicio)
        fim = min(fim_sem, data_fim)
        semanas.append(
            {
                "indice": idx,
                "inicio": ini.isoformat(),
                "fim": fim.isoformat(),
                "label": f"Semana {idx} ({ini.strftime('%d/%m')}–{fim.strftime('%d/%m')})",
            }
        )
        idx += 1
        cursor = fim_sem + timedelta(days=1)
    return semanas


def _to_local_naive(ts):
    """Converte Timestamp/datetime Yahoo para datetime naive (America/Sao_Paulo)."""
    try:
        import pandas as pd

        if isinstance(ts, pd.Timestamp):
            if ts.tzinfo is not None:
                ts = ts.tz_convert("America/Sao_Paulo")
            return ts.to_pydatetime().replace(tzinfo=None)
    except Exception:
        pass
    if hasattr(ts, "to_pydatetime"):
        ts = ts.to_pydatetime()
    if isinstance(ts, datetime) and ts.tzinfo is not None:
        try:
            from zoneinfo import ZoneInfo

            ts = ts.astimezone(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)
        except Exception:
            ts = ts.replace(tzinfo=None)
    return ts


def _no_pregao(dt: datetime) -> bool:
    if dt.weekday() >= 5:
        return False
    t = dt.time()
    return HORA_PREGAO_INI <= t <= HORA_PREGAO_FIM


def baixar_barras_15m(ticker, data_inicio: date, data_fim: date, hoje=None):
    """
    Barras 15m no pregao. Corta automaticamente o que Yahoo nao cobre (>60d).
    Retorno: list[{coletado_em, preco, high, low, intervalo}]
    """
    hoje = hoje or hoje_sp()
    lim = limite_15m(hoje)
    ini = max(data_inicio, lim)
    fim = min(data_fim, hoje)
    if ini > fim:
        return []

    symbol = yahoo_symbol(ticker)
    # end exclusivo no yfinance: +1 dia
    hist = yf.Ticker(symbol).history(
        start=ini.isoformat(),
        end=(fim + timedelta(days=1)).isoformat(),
        interval="15m",
        auto_adjust=False,
    )
    out = []
    if hist is None or hist.empty or "Close" not in hist.columns:
        return out

    for idx, row in hist.iterrows():
        dt = _to_local_naive(idx)
        if not isinstance(dt, datetime):
            continue
        dia = dt.date()
        if dia < ini or dia > fim:
            continue
        if not _no_pregao(dt):
            continue
        close = float(row["Close"])
        high = float(row["High"]) if "High" in hist.columns else close
        low = float(row["Low"]) if "Low" in hist.columns else close
        out.append(
            {
                "coletado_em": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "preco": round(close, 4),
                "high": round(high, 4),
                "low": round(low, 4),
                "intervalo": "15m",
            }
        )
    return out


def baixar_barras_1d(ticker, data_inicio: date, data_fim: date, hoje=None):
    """Barras diarias OHLC. Retorno igual ao 15m (coletado_em = dia 18:00)."""
    hoje = hoje or hoje_sp()
    ini = data_inicio
    fim = min(data_fim, hoje)
    if ini > fim:
        return []

    symbol = yahoo_symbol(ticker)
    hist = yf.Ticker(symbol).history(
        start=(ini - timedelta(days=3)).isoformat(),
        end=(fim + timedelta(days=2)).isoformat(),
        interval="1d",
        auto_adjust=False,
    )
    out = []
    if hist is None or hist.empty or "Close" not in hist.columns:
        return out

    for idx, row in hist.iterrows():
        dt = _to_local_naive(idx)
        dia = dt.date() if isinstance(dt, datetime) else dt
        if not isinstance(dia, date):
            continue
        if dia < ini or dia > fim:
            continue
        close = float(row["Close"])
        high = float(row["High"]) if "High" in hist.columns else close
        low = float(row["Low"]) if "Low" in hist.columns else close
        out.append(
            {
                "coletado_em": f"{dia.isoformat()} 18:00:00",
                "preco": round(close, 4),
                "high": round(high, 4),
                "low": round(low, 4),
                "intervalo": "1d",
            }
        )
    return out
