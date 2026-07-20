# Resumo, posicoes e evolucao mensal da carteira (Dia 27)

from calendar import monthrange
from datetime import date, datetime

from services.preco_yahoo import historico_diario, precos_atuais


def _parse_data(s: str):
    try:
        return datetime.strptime((s or "")[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _fim_do_mes(ano: int, mes: int) -> date:
    return date(ano, mes, monthrange(ano, mes)[1])


def _meses_entre(inicio: date, fim: date) -> list[date]:
    """Lista de datas = ultimo dia de cada mes de inicio..fim (inclusive)."""
    out = []
    y, m = inicio.year, inicio.month
    while (y, m) <= (fim.year, fim.month):
        ultimo = _fim_do_mes(y, m)
        # No mes corrente, usa hoje se ainda nao acabou o mes
        if y == fim.year and m == fim.month:
            out.append(min(ultimo, fim))
        else:
            out.append(ultimo)
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
    return out


def calcular_posicoes(lancamentos: list[dict]) -> list[dict]:
    """
    Agrupa lancamentos por ticker (ordem cronologica).
    Preco medio: compras somam custo; venda reduz qtd mantendo PM (padrao BR).
    """
    ordem = sorted(
        lancamentos,
        key=lambda x: (_parse_data(x.get("data_transacao")) or date.min, x.get("id") or 0),
    )
    estado = {}  # ticker -> dict

    for lan in ordem:
        ticker = (lan.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        tipo = (lan.get("tipo_ativo") or "acao").strip().lower()
        op = (lan.get("operacao") or "").strip().lower()
        qtd = float(lan.get("quantidade") or 0)
        preco = float(lan.get("preco") or 0)
        custos = float(lan.get("outros_custos") or 0)
        if qtd <= 0:
            continue

        if ticker not in estado:
            estado[ticker] = {
                "ticker": ticker,
                "tipo_ativo": tipo,
                "quantidade": 0.0,
                "custo_total": 0.0,
                "preco_medio": 0.0,
            }
        st = estado[ticker]
        st["tipo_ativo"] = tipo

        if op == "compra":
            custo = qtd * preco + custos
            nova_qtd = st["quantidade"] + qtd
            st["custo_total"] = st["custo_total"] + custo
            st["quantidade"] = nova_qtd
            st["preco_medio"] = st["custo_total"] / nova_qtd if nova_qtd else 0.0
        elif op == "venda":
            if qtd > st["quantidade"] + 1e-9:
                qtd = st["quantidade"]
            # Mantem PM; reduz custo proporcional a qtd vendida
            st["quantidade"] -= qtd
            st["custo_total"] = st["preco_medio"] * st["quantidade"]
            if st["quantidade"] <= 1e-9:
                st["quantidade"] = 0.0
                st["custo_total"] = 0.0
                st["preco_medio"] = 0.0

    posicoes = []
    for ticker, st in sorted(estado.items()):
        if st["quantidade"] <= 1e-9:
            continue
        posicoes.append(
            {
                "ticker": ticker,
                "tipo_ativo": st["tipo_ativo"],
                "quantidade": round(st["quantidade"], 6),
                "preco_medio": round(st["preco_medio"], 4),
                "valor_investido": round(st["custo_total"], 2),
                "preco_atual": None,
                "data_cotacao": None,
                "saldo_atual": None,
                "lucro": None,
                "variacao_pct": None,
                "erro_preco": None,
            }
        )
    return posicoes


def _posicao_em_data(lancamentos: list[dict], ate: date) -> dict:
    """Estado qtd/custo por ticker considerando so lancamentos com data <= ate."""
    filtrados = []
    for lan in lancamentos:
        d = _parse_data(lan.get("data_transacao"))
        if d and d <= ate:
            filtrados.append(lan)
    pos = calcular_posicoes(filtrados)
    return {p["ticker"]: p for p in pos}


def montar_acompanhamento(lancamentos: list[dict], meses_grafico: int = 12) -> dict:
    """
    Posicoes + resumo + evolucao mensal (Yahoo).
    """
    posicoes = calcular_posicoes(lancamentos)
    tickers = [p["ticker"] for p in posicoes]

    # Precos atuais
    cotacoes = precos_atuais(tickers) if tickers else {}
    for p in posicoes:
        info = cotacoes.get(p["ticker"]) or {}
        preco = info.get("preco")
        p["preco_atual"] = preco
        p["data_cotacao"] = info.get("data_cotacao")
        p["erro_preco"] = info.get("erro")
        if preco is not None:
            saldo = p["quantidade"] * preco
            lucro = saldo - p["valor_investido"]
            p["saldo_atual"] = round(saldo, 2)
            p["lucro"] = round(lucro, 2)
            inv = p["valor_investido"] or 0
            p["variacao_pct"] = round((lucro / inv) * 100, 2) if inv else None
        else:
            p["saldo_atual"] = None
            p["lucro"] = None
            p["variacao_pct"] = None

    investido = round(sum(p["valor_investido"] for p in posicoes), 2)
    atual_vals = [p["saldo_atual"] for p in posicoes if p["saldo_atual"] is not None]
    patrimonio = round(sum(atual_vals), 2) if atual_vals else None
    lucro_total = round(patrimonio - investido, 2) if patrimonio is not None else None
    rent_pct = (
        round((lucro_total / investido) * 100, 2)
        if patrimonio is not None and investido
        else None
    )

    resumo = {
        "valor_investido": investido,
        "patrimonio": patrimonio,
        "lucro": lucro_total,
        "rentabilidade_pct": rent_pct,
        "qtd_ativos": len(posicoes),
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }

    evolucao = _evolucao_mensal(lancamentos, meses_grafico)

    return {
        "resumo": resumo,
        "posicoes": posicoes,
        "evolucao": evolucao,
    }


def _evolucao_mensal(lancamentos: list[dict], meses: int = 12) -> list[dict]:
    """
    Por mes: valor aplicado (custo) e patrimonio (qtd * fechamento).
    """
    if not lancamentos:
        return []

    datas = [_parse_data(l.get("data_transacao")) for l in lancamentos]
    datas = [d for d in datas if d]
    if not datas:
        return []

    hoje = date.today()
    inicio_hist = min(datas)
    # Limita aos ultimos N meses
    cortes = _meses_entre(inicio_hist, hoje)
    if len(cortes) > meses:
        cortes = cortes[-meses:]

    # Todos tickers que ja apareceram
    tickers = sorted(
        {(l.get("ticker") or "").strip().upper() for l in lancamentos if l.get("ticker")}
    )
    hist = historico_diario(tickers, inicio_hist, hoje)

    pontos = []
    for dia_ref in cortes:
        pos_map = _posicao_em_data(lancamentos, dia_ref)
        aplicado = 0.0
        patrimonio = 0.0
        for ticker, p in pos_map.items():
            aplicado += p["valor_investido"]
            closes = hist.get(ticker) or {}
            preco = None
            anteriores = [d for d in closes if d <= dia_ref]
            if anteriores:
                dmax = max(anteriores)
                preco = closes[dmax]
            if preco is None:
                continue
            patrimonio += p["quantidade"] * preco

        pontos.append(
            {
                "mes": f"{dia_ref.month:02d}/{dia_ref.year}",
                "data": dia_ref.isoformat(),
                "valor_aplicado": round(aplicado, 2),
                "patrimonio": round(patrimonio, 2),
                "ganho": round(patrimonio - aplicado, 2),
            }
        )
    return pontos
