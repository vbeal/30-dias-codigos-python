import re
import time

from bs4 import BeautifulSoup

from config import PAGE_DELAY_SECONDS, RANKING_TOTAL_PAGES
from scraper.client import fetch_html

# URLs e indices das colunas — FIIs e Ações usam tabelas com tamanhos diferentes
RANKINGS = {
    "fiis": {
        "base_url": "https://investidor10.com.br/fiis/rankings/maior-dividend-yield/",
        "link_path": "/fiis/",
        "colunas": {
            "ativo": 0,
            "dividend_yield": 1,
            "patrimonio_liquido": 3,
            "pvp": 4,
            "variacao_12m": 7,
            "segmento": 10,
        },
    },
    "acoes": {
        "base_url": "https://investidor10.com.br/acoes/rankings/maiores-dividend-yield/",
        "link_path": "/acoes/",
        "colunas": {
            "ativo": 0,
            "dividend_yield": 1,
            "patrimonio_liquido": 17,
            "pvp": 5,
            "variacao_12m": 8,
            "segmento": 26,
        },
    },
}


# Extrai ticker e nome completo da celula do ativo
def extract_ticker_and_name(ativo_cell, link_path):
    link = ativo_cell.find("a", href=True)
    ticker = None
    if link and link_path in link["href"]:
        ticker = link["href"].rstrip("/").split("/")[-1].upper()

    text = ativo_cell.get_text(" ", strip=True)
    if not ticker:
        match = re.search(r"#\d+\s+([A-Z]{4}\d{1,2})\b", text)
        if match:
            ticker = match.group(1)
        else:
            ticker = text

    # Remove ranking (#1) e ticker para sobrar o nome
    nome = re.sub(r"#\d+\s*", "", text)
    if ticker:
        nome = re.sub(re.escape(ticker), "", nome, count=1, flags=re.IGNORECASE)
    nome = " ".join(nome.split()).strip(" -|") or ticker

    return ticker, nome


# Le uma linha da tabela de ranking e monta o dicionario de campos
def parse_row(row, config):
    cols = row.find_all("td")
    colunas = config["colunas"]
    max_index = max(colunas.values())

    if len(cols) <= max_index:
        return None

    ativo_cell = cols[colunas["ativo"]]
    ticker, nome = extract_ticker_and_name(ativo_cell, config["link_path"])
    return {
        "ativo": ticker,
        "nome": nome,
        "dividend_yield": cols[colunas["dividend_yield"]].get_text(" ", strip=True),
        "patrimonio_liquido": cols[colunas["patrimonio_liquido"]].get_text(" ", strip=True),
        "pvp": cols[colunas["pvp"]].get_text(" ", strip=True),
        "variacao_12m": cols[colunas["variacao_12m"]].get_text(" ", strip=True),
        "segmento": cols[colunas["segmento"]].get_text(" ", strip=True),
    }


# Converte o HTML de uma pagina de ranking em lista de ativos
def parse_page(html, config):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    rows = []
    for row in table.find_all("tr")[1:]:
        item = parse_row(row, config)
        if item:
            rows.append(item)

    return rows


# Percorre paginas do ranking (max_pages=1 para Top 10 rapido)
def scrape_ranking(ranking_key, max_pages=None):
    config = RANKINGS[ranking_key]
    total = RANKING_TOTAL_PAGES if max_pages is None else max_pages
    all_rows = []

    for page in range(1, total + 1):
        url = f"{config['base_url']}?page={page}"
        html = fetch_html(url)
        all_rows.extend(parse_page(html, config))

        if page < total:
            time.sleep(PAGE_DELAY_SECONDS)

    return all_rows
