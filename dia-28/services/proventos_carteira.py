# Calcula dividendos recebidos na carteira (Dia 28)

from datetime import date, datetime

from db_mercado import ler_proventos, sincronizar_ticker


def _parse(s):
    try:
        return datetime.strptime((s or "")[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def quantidade_na_data(lancamentos: list[dict], ticker: str, ate: date) -> float:
    """Qtd liquida do ticker considerando lancamentos com data <= ate."""
    from services.carteira_resumo import calcular_posicoes

    ticker = ticker.upper()
    filtrados = []
    for lan in lancamentos:
        if (lan.get("ticker") or "").upper() != ticker:
            continue
        d = _parse(lan.get("data_transacao"))
        if d and d <= ate:
            filtrados.append(lan)
    pos = calcular_posicoes(filtrados)
    for p in pos:
        if p["ticker"] == ticker:
            return float(p["quantidade"])
    return 0.0


def calcular_proventos_recebidos(
    lancamentos: list[dict],
    sincronizar: bool = True,
) -> dict:
    """
    Para cada evento de provento do Yahoo (data ex):
    recebido = qtd na data_ex * valor por cota.
    """
    if not lancamentos:
        return {
            "total_recebido": 0.0,
            "por_ticker": {},
            "eventos": [],
        }

    datas = [_parse(l.get("data_transacao")) for l in lancamentos]
    datas = [d for d in datas if d]
    if not datas:
        return {"total_recebido": 0.0, "por_ticker": {}, "eventos": []}

    inicio = min(datas)
    tickers = sorted(
        {(l.get("ticker") or "").strip().upper() for l in lancamentos if l.get("ticker")}
    )

    eventos = []
    por_ticker = {}

    for ticker in tickers:
        if sincronizar:
            sincronizar_ticker(ticker, inicio)
        provs = ler_proventos(ticker, inicio)
        total_t = 0.0
        for pr in provs:
            data_ex = _parse(pr["data_ex"])
            if not data_ex or data_ex < inicio:
                continue
            qtd = quantidade_na_data(lancamentos, ticker, data_ex)
            if qtd <= 1e-9:
                continue
            valor = float(pr["valor"])
            recebido = round(qtd * valor, 2)
            if recebido <= 0:
                continue
            total_t += recebido
            eventos.append(
                {
                    "ticker": ticker,
                    "data_ex": pr["data_ex"],
                    "data_pagamento": pr.get("data_pagamento") or pr["data_ex"],
                    "valor_cota": round(valor, 6),
                    "quantidade": round(qtd, 6),
                    "recebido": recebido,
                }
            )
        if total_t > 0:
            por_ticker[ticker] = round(total_t, 2)

    eventos.sort(key=lambda e: e["data_ex"], reverse=True)
    total = round(sum(e["recebido"] for e in eventos), 2)
    return {
        "total_recebido": total,
        "por_ticker": por_ticker,
        "eventos": eventos,
    }
