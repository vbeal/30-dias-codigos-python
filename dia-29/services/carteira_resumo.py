# Resumo, posicoes, evolucao e proventos da carteira (Dia 27/28)

from calendar import monthrange
from datetime import date, datetime

from db_mercado import historico_diario_cache, precos_atuais_cache, sincronizar_tickers
from services.proventos_carteira import calcular_proventos_recebidos


def _parse_data(s: str):
    try:
        return datetime.strptime((s or "")[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _fim_do_mes(ano: int, mes: int) -> date:
    return date(ano, mes, monthrange(ano, mes)[1])


def _meses_entre(inicio: date, fim: date) -> list[date]:
    out = []
    y, m = inicio.year, inicio.month
    while (y, m) <= (fim.year, fim.month):
        ultimo = _fim_do_mes(y, m)
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
    ordem = sorted(
        lancamentos,
        key=lambda x: (_parse_data(x.get("data_transacao")) or date.min, x.get("id") or 0),
    )
    estado = {}

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
                "lucro_capital": None,
                "dividendos": 0.0,
                "lucro_total": None,
                "variacao_pct": None,
                "erro_preco": None,
            }
        )
    return posicoes


def _posicao_em_data(lancamentos: list[dict], ate: date) -> dict:
    filtrados = []
    for lan in lancamentos:
        d = _parse_data(lan.get("data_transacao"))
        if d and d <= ate:
            filtrados.append(lan)
    pos = calcular_posicoes(filtrados)
    return {p["ticker"]: p for p in pos}


from db_mercado import historico_diario_cache, ler_proventos, precos_atuais_cache, sincronizar_tickers
from services.proventos_carteira import calcular_proventos_recebidos


def _aviso_sem_proventos(ticker: str, lancamentos: list[dict]) -> str | None:
    """Mensagem quando o ativo ainda nao gerou provento recebido apos a compra."""
    ticker = ticker.upper()
    datas = [
        _parse_data(l.get("data_transacao"))
        for l in lancamentos
        if (l.get("ticker") or "").upper() == ticker
    ]
    datas = [d for d in datas if d]
    if not datas:
        return None
    primeira = min(datas)
    provs = ler_proventos(ticker)
    apos_compra = [
        p
        for p in provs
        if (_parse_data(p.get("data_ex")) or date.min) >= primeira
    ]
    if apos_compra:
        return (
            f"Nenhum recebido ainda — voce precisa ter cotas na data-ex. "
            f"Compra em {primeira.strftime('%d/%m/%Y')}."
        )
    return (
        f"Sem proventos no Yahoo apos sua compra ({primeira.strftime('%d/%m/%Y')}). "
        f"Aguarde o proximo pagamento do ativo."
    )


def montar_acompanhamento(
    lancamentos: list[dict],
    meses_grafico: int = 12,
    forcar: bool = False,
) -> dict:
    """Posicoes + resumo (com proventos) + evolucao — usa cache SQLite."""
    posicoes = calcular_posicoes(lancamentos)
    tickers_hist = sorted(
        {(l.get("ticker") or "").strip().upper() for l in lancamentos if l.get("ticker")}
    )
    tickers = [p["ticker"] for p in posicoes]

    # Uma unica sincronizacao Yahoo (so o que falta) para todos os tickers
    datas_lan = [_parse_data(l.get("data_transacao")) for l in lancamentos]
    datas_lan = [d for d in datas_lan if d]
    inicio_sync = min(datas_lan) if datas_lan else date.today()
    if tickers_hist:
        sincronizar_tickers(tickers_hist, inicio_sync, forcar=forcar)

    # Proventos e precos so leem cache (sem bater Yahoo de novo)
    prov = calcular_proventos_recebidos(lancamentos, sincronizar=False)
    por_ticker_div = prov.get("por_ticker") or {}
    avisos_proventos = []

    cotacoes = (
        precos_atuais_cache(tickers, sincronizar=False) if tickers else {}
    )
    for p in posicoes:
        info = cotacoes.get(p["ticker"]) or {}
        preco = info.get("preco")
        p["preco_atual"] = preco
        p["data_cotacao"] = info.get("data_cotacao")
        p["erro_preco"] = info.get("erro")
        divs = float(por_ticker_div.get(p["ticker"]) or 0)
        p["dividendos"] = divs
        p["aviso_proventos"] = None
        if divs <= 0 and p.get("quantidade", 0) > 0:
            aviso = _aviso_sem_proventos(p["ticker"], lancamentos)
            p["aviso_proventos"] = aviso
            if aviso:
                avisos_proventos.append({"ticker": p["ticker"], "mensagem": aviso})
        if preco is not None:
            saldo = p["quantidade"] * preco
            lucro_cap = saldo - p["valor_investido"]
            lucro_tot = lucro_cap + divs
            p["saldo_atual"] = round(saldo, 2)
            p["lucro_capital"] = round(lucro_cap, 2)
            p["lucro_total"] = round(lucro_tot, 2)
            inv = p["valor_investido"] or 0
            p["variacao_pct"] = round((lucro_tot / inv) * 100, 2) if inv else None
            # compat com front antigo
            p["lucro"] = p["lucro_total"]
        else:
            p["saldo_atual"] = None
            p["lucro_capital"] = None
            p["lucro_total"] = round(divs, 2) if divs else None
            p["lucro"] = p["lucro_total"]
            p["variacao_pct"] = None

    investido = round(sum(p["valor_investido"] for p in posicoes), 2)
    atual_vals = [p["saldo_atual"] for p in posicoes if p["saldo_atual"] is not None]
    patrimonio = round(sum(atual_vals), 2) if atual_vals else None
    eventos = prov.get("eventos") or []
    ultimo = eventos[0] if eventos else None  # ja ordenado data_ex desc
    dividendos_total = float(prov.get("total_recebido") or 0)
    lucro_capital = (
        round(patrimonio - investido, 2) if patrimonio is not None else None
    )
    lucro_total = (
        round(lucro_capital + dividendos_total, 2) if lucro_capital is not None else None
    )
    rent_pct = (
        round((lucro_total / investido) * 100, 2)
        if lucro_total is not None and investido
        else None
    )

    resumo = {
        "valor_investido": investido,
        "patrimonio": patrimonio,
        "lucro_capital": lucro_capital,
        "dividendos": round(dividendos_total, 2),
        "dividendos_total": round(dividendos_total, 2),
        "ultimo_dividendo": round(float(ultimo["recebido"]), 2) if ultimo else 0.0,
        "ultimo_dividendo_ticker": (ultimo or {}).get("ticker"),
        "ultimo_dividendo_data": (ultimo or {}).get("data_ex"),
        "lucro": lucro_total,
        "lucro_total": lucro_total,
        "rentabilidade_pct": rent_pct,
        "qtd_ativos": len(posicoes),
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }

    evolucao = _evolucao_mensal(lancamentos, meses_grafico, eventos=eventos)

    prov["avisos_sem_recebido"] = avisos_proventos

    return {
        "resumo": resumo,
        "posicoes": posicoes,
        "evolucao": evolucao,
        "proventos": prov,
        "tickers_historico": tickers_hist,
    }


def _evolucao_mensal(
    lancamentos: list[dict],
    meses: int = 12,
    eventos: list[dict] | None = None,
) -> list[dict]:
    if not lancamentos:
        return []

    datas = [_parse_data(l.get("data_transacao")) for l in lancamentos]
    datas = [d for d in datas if d]
    if not datas:
        return []

    hoje = date.today()
    inicio_hist = min(datas)
    cortes = _meses_entre(inicio_hist, hoje)
    if len(cortes) > meses:
        cortes = cortes[-meses:]

    tickers = sorted(
        {(l.get("ticker") or "").strip().upper() for l in lancamentos if l.get("ticker")}
    )
    hist = historico_diario_cache(tickers, inicio_hist, hoje, sincronizar=False)
    eventos = eventos or []

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

        # Dividendos ate o fim do mes + so os do mes
        div_acum = 0.0
        div_mes = 0.0
        for ev in eventos:
            d_ex = _parse_data(ev.get("data_ex"))
            if not d_ex or d_ex > dia_ref:
                continue
            rec = float(ev.get("recebido") or 0)
            div_acum += rec
            if d_ex.year == dia_ref.year and d_ex.month == dia_ref.month:
                div_mes += rec

        pontos.append(
            {
                "mes": f"{dia_ref.month:02d}/{dia_ref.year}",
                "data": dia_ref.isoformat(),
                "valor_aplicado": round(aplicado, 2),
                "patrimonio": round(patrimonio, 2),
                "ganho": round(patrimonio - aplicado, 2),
                "dividendos_mes": round(div_mes, 2),
                "dividendos_acumulado": round(div_acum, 2),
            }
        )
    return pontos
