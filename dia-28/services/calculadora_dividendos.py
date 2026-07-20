# Novidade Dia 25: calculadora de dividendos (estilo Brapi light)
# Simula aportes + DY atual (scrape) + reinvestimento opcional + comparacao IPCA+

import calendar
import math
import re
import time
from datetime import date

from services.detalhe_ativo import TIPOS_DETALHE, build_detalhe, limpar_ticker
from services.top_dividendos import agora_br, format_tempo
from scraper.ipca import scrape_ipca

# Periodos prontos (meses) — iguais a ideia da Brapi
PERIODOS_MESES = {
    "1 ano": 12,
    "2 anos": 24,
    "3 anos": 36,
    "5 anos": 60,
    "10 anos": 120,
}

# Juros reais default sobre o IPCA (estilo Tesouro IPCA+X)
TAXA_REAL_DEFAULT = 6.0


def adicionar_meses(base: date, meses: int) -> date:
    """Soma meses a uma data (dia limitado ao ultimo dia do mes destino)."""
    m0 = base.month - 1 + meses
    ano = base.year + m0 // 12
    mes = m0 % 12 + 1
    dia = min(base.day, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


def parse_preco_br(texto) -> float | None:
    """'R$ 9,72' ou '9.72' -> float."""
    if texto is None:
        return None
    s = str(texto).strip()
    if not s:
        return None
    s = s.replace("R$", "").replace(" ", "")
    # remove milhar e troca decimal
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        v = float(re.sub(r"[^\d.\-]", "", s))
        return v if v > 0 else None
    except ValueError:
        return None


def parse_pct_br(texto) -> float | None:
    """'12,34%' ou '12.34' -> 12.34 (percentual)."""
    if texto is None:
        return None
    s = str(texto).strip().replace("%", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(re.sub(r"[^\d.\-]", "", s))
    except ValueError:
        return None


def extrair_preco_dy(detalhe: dict) -> tuple[float, float]:
    """Pega preco e DY (%) do JSON de detalhe (FII ou Acao)."""
    cot = detalhe.get("cotacao") or {}
    preco = parse_preco_br(cot.get("preco"))
    dy = parse_pct_br(cot.get("dy_12m") or cot.get("dy"))
    if preco is None:
        raise ValueError("Nao foi possivel ler o preco do ativo no Investidor10.")
    if dy is None or dy <= 0:
        raise ValueError("Nao foi possivel ler o Dividend Yield (DY) do ativo.")
    return preco, dy


def simular_aportes(
    *,
    preco: float,
    dy_aa: float,
    aporte_inicial: float,
    aporte_mensal: float,
    meses: int,
    reinvestir: bool,
) -> dict:
    """
    Simulacao mensal simplificada:
    - Preco e DY fixos (cenario constante com dados atuais).
    - Dividendo mensal/cota = preco * (DY/100) / 12.
    - Compra cotas fracionadas (ok para estudo).
    """
    if meses < 1 or meses > 360:
        raise ValueError("Periodo deve ser entre 1 e 360 meses.")
    if aporte_inicial < 0 or aporte_mensal < 0:
        raise ValueError("Aportes nao podem ser negativos.")
    if aporte_inicial == 0 and aporte_mensal == 0:
        raise ValueError("Informe aporte inicial e/ou mensal.")

    div_mensal_cota = preco * (dy_aa / 100.0) / 12.0
    cotas = 0.0
    caixa_dividendos = 0.0
    total_aportado = 0.0
    total_dividendos = 0.0
    historico = []
    # Historico estilo Brapi: comeca hoje e avanca mes a mes (projecao)
    data_base = date.today().replace(day=min(15, calendar.monthrange(date.today().year, date.today().month)[1]))

    for m in range(1, meses + 1):
        aporte = aporte_inicial if m == 1 else aporte_mensal
        if m == 1:
            aporte = aporte_inicial + aporte_mensal  # mes 1: inicial + 1o mensal
        total_aportado += aporte

        # Dinheiro disponivel para compra neste mes
        disponivel = aporte
        if reinvestir and caixa_dividendos > 0:
            disponivel += caixa_dividendos
            caixa_dividendos = 0.0

        cotas_compradas = 0.0
        if disponivel > 0 and preco > 0:
            cotas_compradas = disponivel / preco
            cotas += cotas_compradas

        # Dividendos do mes sobre as cotas ja possuidas (apos compra do mes)
        div_mes = cotas * div_mensal_cota
        total_dividendos += div_mes
        if reinvestir:
            # reinveste no proximo ciclo via caixa
            caixa_dividendos += div_mes
        else:
            caixa_dividendos += div_mes

        patrimonio = cotas * preco + (0.0 if reinvestir else caixa_dividendos)
        # Se reinvestir, o caixa de dividendos ainda nao comprado conta no patrimonio
        if reinvestir:
            patrimonio = cotas * preco + caixa_dividendos

        data_mes = adicionar_meses(data_base, m - 1)
        historico.append(
            {
                "mes": m,
                "data": data_mes.isoformat(),
                "data_br": data_mes.strftime("%d/%m/%Y"),
                "aporte": round(aporte, 2),
                "preco": round(preco, 2),
                "cotas_compradas": round(cotas_compradas, 4),
                "cotas_compradas_int": int(cotas_compradas),  # visual aproximado
                "cotas": round(cotas, 4),
                "dividendos_mes": round(div_mes, 2),
                "total_aportado": round(total_aportado, 2),
                "total_dividendos": round(total_dividendos, 2),
                "patrimonio": round(patrimonio, 2),
            }
        )

    patrimonio_final = historico[-1]["patrimonio"] if historico else 0.0
    ganho = patrimonio_final - total_aportado
    rentabilidade = (ganho / total_aportado * 100.0) if total_aportado > 0 else 0.0
    renda_mensal_estimada = cotas * div_mensal_cota
    yield_on_cost = (
        (renda_mensal_estimada * 12.0 / total_aportado * 100.0) if total_aportado > 0 else 0.0
    )

    # Numero magico: cotas em que o dividendo do mes compra 1 cota nova
    # = preco / dividendo_mensal_por_cota (arredondado para CIMA: cota inteira)
    numero_magico = (
        int(math.ceil(preco / div_mensal_cota)) if div_mensal_cota > 0 else None
    )
    custo_magico = (
        round(numero_magico * preco, 2) if numero_magico is not None else None
    )
    mes_atingiu = None
    if numero_magico is not None:
        for h in historico:
            atingiu = h["cotas"] + 1e-9 >= numero_magico
            h["atingiu_numero_magico"] = atingiu
            if atingiu and mes_atingiu is None:
                mes_atingiu = h["mes"]
                h["primeiro_mes_magico"] = True
            else:
                h["primeiro_mes_magico"] = False

    return {
        "cotas": round(cotas, 4),
        "cotas_iniciais": historico[0]["cotas_compradas"] if historico else 0.0,
        "total_aportado": round(total_aportado, 2),
        "total_dividendos": round(total_dividendos, 2),
        "patrimonio_final": round(patrimonio_final, 2),
        "ganho": round(ganho, 2),
        "rentabilidade_pct": round(rentabilidade, 2),
        "renda_mensal_estimada": round(renda_mensal_estimada, 2),
        "renda_sobre_aporte_pct": round(yield_on_cost, 2),
        "yield_on_cost_pct": round(yield_on_cost, 2),  # legado
        "div_mensal_por_cota": round(div_mensal_cota, 4),
        "numero_magico": numero_magico,
        "custo_numero_magico": custo_magico,
        "mes_atingiu_numero_magico": mes_atingiu,
        "historico": historico,
    }


def build_simulacao(
    *,
    tipo: str,
    ticker: str,
    aporte_inicial: float,
    aporte_mensal: float,
    meses: int,
    reinvestir: bool = True,
    taxa_real_aa: float | None = None,
    ipca_mais_aa: float | None = None,
) -> dict:
    """Scrape do ativo + IPCA 12M + simulacao completa (API da calculadora)."""
    tipo = (tipo or "").strip().lower()
    ticker = limpar_ticker(ticker)
    if tipo not in TIPOS_DETALHE:
        raise ValueError("Tipo invalido. Use fii ou acao.")
    if not ticker:
        raise ValueError("Informe o ticker.")

    inicio = time.perf_counter()
    detalhe = build_detalhe(tipo, ticker)
    preco, dy = extrair_preco_dy(detalhe)

    ipca_info = scrape_ipca()
    ipca_12m = float(ipca_info["ipca_12m"])

    # Preferencia: taxa_real + IPCA. Fallback: ipca_mais_aa legado (campo unico).
    if taxa_real_aa is not None:
        taxa_real = float(taxa_real_aa)
        taxa_comparacao = round(ipca_12m + taxa_real, 2)
    elif ipca_mais_aa is not None:
        taxa_comparacao = float(ipca_mais_aa)
        taxa_real = round(taxa_comparacao - ipca_12m, 2)
    else:
        taxa_real = TAXA_REAL_DEFAULT
        taxa_comparacao = round(ipca_12m + taxa_real, 2)

    sim = simular_aportes(
        preco=preco,
        dy_aa=dy,
        aporte_inicial=float(aporte_inicial),
        aporte_mensal=float(aporte_mensal),
        meses=int(meses),
        reinvestir=bool(reinvestir),
    )

    ipca_final = _ipca_mesmo_fluxo(
        float(aporte_inicial),
        float(aporte_mensal),
        int(meses),
        taxa_comparacao,
    )

    vs_ipca = round(sim["patrimonio_final"] - ipca_final, 2)
    tempo = time.perf_counter() - inicio

    return {
        "ok": True,
        "ticker": ticker,
        "tipo": tipo,
        "tipo_label": detalhe.get("tipo_label"),
        "nome": (detalhe.get("informacoes") or {}).get("razao_social")
        or (detalhe.get("empresa") or {}).get("nome")
        or ticker,
        "preco": preco,
        "dy_aa": dy,
        "aporte_inicial": float(aporte_inicial),
        "aporte_mensal": float(aporte_mensal),
        "meses": int(meses),
        "reinvestir": bool(reinvestir),
        "ipca_12m": ipca_12m,
        "ipca_mes": ipca_info.get("ipca_mes"),
        "ipca_ano": ipca_info.get("ipca_ano"),
        "taxa_real_aa": taxa_real,
        "ipca_mais_aa": taxa_comparacao,
        "ipca_mais_final": ipca_final,
        "vs_ipca_mais": vs_ipca,
        "ipca_fonte": ipca_info.get("fonte"),
        "avisos": [
            "Isto e so uma simulacao educativa. O preco e o DY usados sao os de hoje e ficam fixos no calculo.",
            f"Comparamos com IPCA 12 meses ({ipca_12m:.2f}%) + taxa real ({taxa_real:.2f}%) = {taxa_comparacao:.2f}% ao ano.",
            "O passado nao garante o futuro: o rendimento pode subir ou cair.",
            "Nao entram corretagem, spread nem mudanca de preco das cotas.",
            (
                "FII: em geral a pessoa fisica nao paga Imposto de Renda sobre os dividendos recebidos "
                "(regras atuais — confira sempre a legislacao)."
                if tipo == "fii"
                else "Acao: dividendos de acoes podem ter regras diferentes de imposto — esta simulacao nao desconta IR."
            ),
        ],
        "consultado_em": agora_br(),
        "tempo_carregamento": format_tempo(tempo),
        "fonte": detalhe.get("fonte"),
        **sim,
    }


def _ipca_mesmo_fluxo(
    aporte_inicial: float,
    aporte_mensal: float,
    meses: int,
    taxa_aa: float,
) -> float:
    """Mesma sequencia de aportes da simulacao de cotas, rendendo IPCA+X a.a."""
    r = (taxa_aa / 100.0) / 12.0
    saldo = 0.0
    for m in range(1, meses + 1):
        aporte = aporte_inicial + aporte_mensal if m == 1 else aporte_mensal
        saldo = saldo * (1 + r) + aporte
    return round(saldo, 2)
