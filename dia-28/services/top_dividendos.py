# Novidade Dia 23: monta Top 10 misto (5 FIIs + 5 Ações) ordenado por DY
import time
from datetime import datetime

from config import TOP_N_POR_TIPO
from scraper.rankings import scrape_ranking


# Data/hora no padrao brasileiro: 14/07/2026 09:20:20
def agora_br():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


# Formata segundos de carregamento (ex.: 5,82 s)
def format_tempo(segundos):
    return f"{segundos:.2f} s".replace(".", ",")


# Converte "54,36%" em float 54.36
def dy_to_float(texto):
    if not texto:
        return None
    limpo = str(texto).replace("%", "").strip().replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


# DY mensal estimado (anual / 12) — igual a ideia dos Dias 15-17
def format_dy_mensal(dy_anual):
    if dy_anual is None:
        return "-"
    mensal = dy_anual / 12
    return f"{mensal:.2f}%".replace(".", ",")


def enrich(item, tipo):
    dy_num = dy_to_float(item.get("dividend_yield"))
    return {
        "ativo": item.get("ativo"),
        "nome": item.get("nome") or item.get("segmento") or item.get("ativo"),
        "tipo": tipo,
        "dividend_yield": item.get("dividend_yield"),
        "dy_num": dy_num if dy_num is not None else -1,
        "dy_mensal": format_dy_mensal(dy_num),
        "segmento": item.get("segmento"),
        "pvp": item.get("pvp"),
        "variacao_12m": item.get("variacao_12m"),
        "patrimonio_liquido": item.get("patrimonio_liquido"),
    }


# Top 5 FIIs + Top 5 Ações da 1a pagina, ordenados pelo maior DY
def build_top10():
    inicio = time.perf_counter()
    fiis = [enrich(i, "FII") for i in scrape_ranking("fiis", max_pages=1)[:TOP_N_POR_TIPO]]
    acoes = [enrich(i, "Ação") for i in scrape_ranking("acoes", max_pages=1)[:TOP_N_POR_TIPO]]
    mistos = sorted(fiis + acoes, key=lambda x: x["dy_num"], reverse=True)
    tempo = time.perf_counter() - inicio

    return {
        "consultado_em": agora_br(),
        "tempo_carregamento": format_tempo(tempo),
        "tempo_carregamento_segundos": round(tempo, 2),
        "fonte": "investidor10.com.br",
        "aviso": "Top 5 FIIs + Top 5 Ações (1a pagina), ordenados por Dividend Yield. Dados em tempo real.",
        "total": len(mistos),
        "itens": mistos,
    }


# Ranking completo de um tipo (Ver todos) — varias paginas
def build_ranking_completo(tipo):
    inicio = time.perf_counter()
    chave = "fiis" if tipo == "fiis" else "acoes"
    label = "FII" if chave == "fiis" else "Ação"
    itens = [enrich(i, label) for i in scrape_ranking(chave)]
    tempo = time.perf_counter() - inicio

    return {
        "consultado_em": agora_br(),
        "tempo_carregamento": format_tempo(tempo),
        "tempo_carregamento_segundos": round(tempo, 2),
        "fonte": "investidor10.com.br",
        "tipo": chave,
        "total": len(itens),
        "itens": itens,
    }
