# Classificacao de status do Radar (zonas compra/venda)

STATUS_ORDEM = ("STOP", "ALVO", "ZONA_ENTRADA", "CORTE", "FORA")

STATUS_LABEL = {
    "STOP": "Stop",
    "ALVO": "Alvo",
    "ZONA_ENTRADA": "Zona de entrada",
    "CORTE": "Corte / nao investir",
    "FORA": "Fora das zonas",
}


def classificar_preco(preco, ativo):
    """Classifica um preco pontual conforme direcao compra/venda."""
    p = float(preco)
    entrada = float(ativo["preco_entrada"])
    teto = float(ativo["preco_teto"])
    alvo = float(ativo["preco_alvo"])
    stop = float(ativo["preco_stop"])
    corte = float(ativo["preco_corte"])
    lo, hi = (entrada, teto) if entrada <= teto else (teto, entrada)

    if (ativo.get("direcao") or "compra").lower() == "venda":
        if p >= stop:
            return "STOP"
        if p <= alvo:
            return "ALVO"
        if lo <= p <= hi:
            return "ZONA_ENTRADA"
        if p > corte:
            return "CORTE"
        return "FORA"

    # compra
    if p <= stop:
        return "STOP"
    if p >= alvo:
        return "ALVO"
    if lo <= p <= hi:
        return "ZONA_ENTRADA"
    if p < corte:
        return "CORTE"
    return "FORA"


def _zona_tocada(low, high, z_lo, z_hi):
    return not (high < z_lo or low > z_hi)


def classificar_barra_diaria(low, high, close, ativo):
    """
    Dia completo: prioriza toque nas zonas (high/low), senao o fechamento.
    Ordem: STOP > ALVO > ZONA_ENTRADA > CORTE > FORA
    """
    low, high, close = float(low), float(high), float(close)
    entrada = float(ativo["preco_entrada"])
    teto = float(ativo["preco_teto"])
    alvo = float(ativo["preco_alvo"])
    stop = float(ativo["preco_stop"])
    corte = float(ativo["preco_corte"])
    lo, hi = (entrada, teto) if entrada <= teto else (teto, entrada)
    venda = (ativo.get("direcao") or "compra").lower() == "venda"

    tocados = []
    if venda:
        if high >= stop:
            tocados.append("STOP")
        if low <= alvo:
            tocados.append("ALVO")
        if _zona_tocada(low, high, lo, hi):
            tocados.append("ZONA_ENTRADA")
        if high > corte:
            tocados.append("CORTE")
    else:
        if low <= stop:
            tocados.append("STOP")
        if high >= alvo:
            tocados.append("ALVO")
        if _zona_tocada(low, high, lo, hi):
            tocados.append("ZONA_ENTRADA")
        if low < corte:
            tocados.append("CORTE")

    for st in STATUS_ORDEM:
        if st in tocados:
            return st
    return classificar_preco(close, ativo)


def prioridade(status):
    try:
        return STATUS_ORDEM.index(status)
    except ValueError:
        return len(STATUS_ORDEM)
