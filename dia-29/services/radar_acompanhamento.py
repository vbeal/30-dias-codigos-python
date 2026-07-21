# Orquestra sync + dados de visualizacao do Radar

from datetime import date, datetime, timedelta

from db_radar import (
    contar_snapshots_radar,
    listar_ativos_radar,
    listar_snapshots_serie,
    substituir_snapshots_ativo,
)
from services.radar_status import (
    STATUS_LABEL,
    classificar_barra_diaria,
    classificar_preco,
)
from services.radar_yahoo import (
    baixar_barras_15m,
    baixar_barras_1d,
    limite_15m,
    resolucao_grafico,
    semanas_do_periodo,
)
from web.timezone_util import hoje_sp


def _parse_iso(d):
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()


def _barras_hibridas(ticker, data_inicio, data_fim, hoje=None):
    """
    Parte antiga (>60d) em 1d; parte recente em 15m + 1d de apoio
    (grafico longo usa 1d; log usa 15m quando existir).
    """
    hoje = hoje or hoje_sp()
    lim = limite_15m(hoje)
    barras = []

    if data_inicio < lim:
        fim_diario = min(data_fim, lim - timedelta(days=1))
        if data_inicio <= fim_diario:
            barras.extend(baixar_barras_1d(ticker, data_inicio, fim_diario, hoje=hoje))

    ini_15 = max(data_inicio, lim)
    if ini_15 <= data_fim:
        barras.extend(baixar_barras_15m(ticker, ini_15, data_fim, hoje=hoje))
        barras.extend(baixar_barras_1d(ticker, ini_15, data_fim, hoje=hoje))

    return barras


def _snapshots_com_status(ativo, barras):
    out = []
    for b in barras:
        if b["intervalo"] == "1d":
            st = classificar_barra_diaria(b["low"], b["high"], b["preco"], ativo)
        else:
            st = classificar_preco(b["preco"], ativo)
        out.append(
            {
                "coletado_em": b["coletado_em"],
                "preco": b["preco"],
                "intervalo": b["intervalo"],
                "status": st,
            }
        )
    return out


def sincronizar_radar(radar, ativos=None, forcar=False, hoje=None):
    """Baixa Yahoo e grava snapshots. Pula se ja houver dados (salvo forcar)."""
    hoje = hoje or hoje_sp()
    ativos = ativos if ativos is not None else listar_ativos_radar(radar["id"])
    if not ativos:
        return {"ok": True, "msg": "Sem ativos.", "snapshots": 0}

    if not forcar and contar_snapshots_radar(radar["id"]) > 0:
        return {
            "ok": True,
            "msg": "Historico ja sincronizado.",
            "snapshots": contar_snapshots_radar(radar["id"]),
        }

    ini = _parse_iso(radar["data_inicio"])
    fim = _parse_iso(radar["data_fim"])
    total = 0
    erros = []
    for ativo in ativos:
        try:
            barras = _barras_hibridas(ativo["ticker"], ini, fim, hoje=hoje)
            snaps = _snapshots_com_status(ativo, barras)
            substituir_snapshots_ativo(ativo["id"], snaps)
            total += len(snaps)
        except Exception as exc:
            erros.append(f"{ativo['ticker']}: {exc}")

    msg = f"Sincronizado: {total} pontos."
    if erros:
        msg += " Falhas: " + "; ".join(erros[:3])
    return {"ok": not erros, "msg": msg, "snapshots": total, "erros": erros}


def meta_acompanhamento(radar, ativos):
    ini = _parse_iso(radar["data_inicio"])
    fim = _parse_iso(radar["data_fim"])
    res = resolucao_grafico(ini, fim)
    return {
        "resolucao_grafico": res,
        "semanas": semanas_do_periodo(ini, fim),
        "limite_15m": limite_15m().isoformat(),
        "ativos": [
            {
                "id": a["id"],
                "ticker": a["ticker"],
                "direcao": a["direcao"],
                "preco_entrada": a["preco_entrada"],
                "preco_teto": a["preco_teto"],
                "preco_alvo": a["preco_alvo"],
                "preco_stop": a["preco_stop"],
                "preco_corte": a["preco_corte"],
            }
            for a in ativos
        ],
        "status_labels": STATUS_LABEL,
    }


def serie_grafico(radar, ticker, semana_inicio, semana_fim):
    ini = _parse_iso(radar["data_inicio"])
    fim = _parse_iso(radar["data_fim"])
    res = resolucao_grafico(ini, fim)
    # Se pediu 15m mas Yahoo nao cobre a semana, cai para 1d
    lim = limite_15m()
    if res == "15m" and _parse_iso(semana_inicio) < lim:
        res = "1d"
    pontos = listar_snapshots_serie(
        radar["id"], ticker, res, semana_inicio, semana_fim
    )
    # Fallback: se 15m vazio, tenta 1d
    if res == "15m" and not pontos:
        res = "1d"
        pontos = listar_snapshots_serie(
            radar["id"], ticker, res, semana_inicio, semana_fim
        )
    return {"intervalo": res, "pontos": pontos}


def logs_paginados(radar_id, page=1, per_page=50, ticker=None):
    """
    Log: linhas 15m + linhas 1d apenas nos dias sem cobertura 15m
    (antes do limite Yahoo ~60 dias). Evita duplicar o mesmo dia.
    """
    lim = limite_15m().isoformat()
    # Reusa listar_snapshots com filtro SQL via funcao dedicada
    from db_radar import listar_snapshots_log

    dados = listar_snapshots_log(
        radar_id,
        ticker=ticker,
        limite_15m=lim,
        page=page,
        per_page=per_page,
    )
    for item in dados["itens"]:
        item["status_label"] = STATUS_LABEL.get(
            item.get("status") or "", item.get("status")
        )
    return dados
