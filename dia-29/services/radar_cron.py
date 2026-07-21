# Cron do Radar (Dia 29) — coleta a cada 15 min no pregão B3
# Roda dentro do processo Flask (APScheduler). Local e produção iguais:
# basta o app estar ligado (python dia29_app.py).

from __future__ import annotations

import logging
from datetime import datetime, time

import yfinance as yf
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from db_radar import (
    listar_ativos_radar,
    listar_radares_vigentes,
    upsert_snapshot,
)
from services.preco_yahoo import yahoo_symbol
from services.radar_status import classificar_preco
from web.timezone_util import TZ, agora_sp

logger = logging.getLogger(__name__)

HORA_INI = time(10, 0)
HORA_FIM = time(18, 0)

_scheduler: BackgroundScheduler | None = None


def no_horario_pregao(agora: datetime | None = None) -> bool:
    """Seg–sex, 10:00–18:00 (America/Sao_Paulo / UTC-3)."""
    agora = agora or agora_sp()
    if agora.weekday() >= 5:
        return False
    t = agora.time()
    return HORA_INI <= t <= HORA_FIM


def slot_15m(agora: datetime | None = None) -> str:
    """Arredonda para o bloco de 15 min (YYYY-MM-DD HH:MM:00) em SP."""
    agora = agora or agora_sp()
    minuto = (agora.minute // 15) * 15
    dt = agora.replace(minute=minuto, second=0, microsecond=0)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def cotacao_15m_atual(ticker: str) -> float | None:
    """Ultima barra 15m do dia (Yahoo)."""
    symbol = yahoo_symbol(ticker)
    try:
        hist = yf.Ticker(symbol).history(period="1d", interval="15m", auto_adjust=False)
        if hist is None or hist.empty or "Close" not in hist.columns:
            return None
        return round(float(hist["Close"].iloc[-1]), 4)
    except Exception as exc:
        logger.warning("Yahoo 15m falhou para %s: %s", ticker, exc)
        return None


def executar_coleta_radar(forcar: bool = False) -> dict:
    """
    Coleta cotacao dos radares vigentes e grava snapshot 15m.
    forcar=True ignora horario (util para teste).
    """
    agora = agora_sp()
    if not forcar and not no_horario_pregao(agora):
        return {
            "ok": True,
            "pulou": True,
            "msg": "Fora do horario de pregao.",
            "pontos": 0,
        }

    slot = slot_15m(agora)
    radares = listar_radares_vigentes(agora.date())
    pontos = 0
    erros = []

    for radar in radares:
        ativos = listar_ativos_radar(radar["id"])
        for ativo in ativos:
            try:
                preco = cotacao_15m_atual(ativo["ticker"])
                if preco is None:
                    erros.append(f"{ativo['ticker']}: sem cotacao")
                    continue
                status = classificar_preco(preco, ativo)
                upsert_snapshot(ativo["id"], slot, preco, "15m", status)
                pontos += 1
            except Exception as exc:
                erros.append(f"{ativo['ticker']}: {exc}")

    msg = f"Cron Radar: {pontos} ponto(s) em {len(radares)} radar(es) · slot {slot}"
    if erros:
        msg += f" · {len(erros)} falha(s)"
        logger.warning("Cron Radar erros: %s", "; ".join(erros[:5]))
    else:
        logger.info(msg)

    return {
        "ok": len(erros) == 0,
        "pulou": False,
        "msg": msg,
        "pontos": pontos,
        "radares": len(radares),
        "slot": slot,
        "erros": erros,
    }


def iniciar_scheduler() -> BackgroundScheduler | None:
    """
    Agenda job a cada 15 min nos minutos 0,15,30,45 (seg–sex).
    O proprio job verifica 10h–18h SP.
    """
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone=TZ)
    _scheduler.add_job(
        executar_coleta_radar,
        trigger=CronTrigger(
            day_of_week="mon-fri",
            hour="10-18",
            minute="0,15,30,45",
            timezone=TZ,
        ),
        id="radar_coleta_15m",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("APScheduler Radar iniciado (seg–sex 10h–18h SP, a cada 15 min).")
    return _scheduler


def parar_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
