# Novidade Dia 24: detalhe de FII / Ação (scrape ao vivo, so para logado)
import re
import time

from scraper.detalhe_acao import scrape_acao_detail
from scraper.detalhe_fii import scrape_fii_detail
from services.top_dividendos import agora_br, format_tempo

TIPOS_DETALHE = {"fii", "acao"}


# Normaliza ticker digitado na busca (PETR4, petr4, PETR4.SA)
def limpar_ticker(ticker):
    t = (ticker or "").strip().upper()
    t = t.replace(".SA", "")
    t = re.sub(r"[^A-Z0-9]", "", t)
    return t


# Busca detalhe no Investidor10 com tempo de carregamento
def build_detalhe(tipo, ticker):
    tipo = (tipo or "").strip().lower()
    ticker = limpar_ticker(ticker)

    if tipo not in TIPOS_DETALHE:
        raise ValueError("Tipo invalido. Use fii ou acao.")
    if not ticker or len(ticker) < 4:
        raise ValueError("Ticker invalido.")

    inicio = time.perf_counter()
    if tipo == "fii":
        data = scrape_fii_detail(ticker)
        data["tipo_label"] = "FII"
    else:
        data = scrape_acao_detail(ticker)
        data["tipo_label"] = "Ação"

    tempo = time.perf_counter() - inicio
    data["consultado_em"] = agora_br()
    data["tempo_carregamento"] = format_tempo(tempo)
    data["tempo_carregamento_segundos"] = round(tempo, 2)
    return data
