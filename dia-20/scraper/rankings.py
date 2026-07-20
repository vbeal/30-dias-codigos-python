import re
import time

from bs4 import BeautifulSoup

from config import PAGE_DELAY_SECONDS, RANKING_TOTAL_PAGES
from scraper.client import fetch_html

# URLs e indices das colunas — FIIs e Acoes usam tabelas com tamanhos diferentes
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


# Extrai o ticker pelo link do ativo ou pelo texto da celula
def extract_ticker(ativo_cell, link_path):
    link = ativo_cell.find("a", href=True)
    if link and link_path in link["href"]:
        return link["href"].rstrip("/").split("/")[-1].upper()

    text = ativo_cell.get_text(" ", strip=True)
    match = re.search(r"#\d+\s+([A-Z]{4}\d{1,2})\b", text)
    if match:
        return match.group(1)

    return text


# Le uma linha da tabela de ranking e monta o dicionario de campos
def parse_row(row, config):
    cols = row.find_all("td")
    colunas = config["colunas"]
    max_index = max(colunas.values())

    if len(cols) <= max_index:
        return None

    ativo_cell = cols[colunas["ativo"]]
    return {
        "ativo": extract_ticker(ativo_cell, config["link_path"]),
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
    for row in table.find_all("tr")[1:]:  # pula cabecalho
        item = parse_row(row, config)
        if item:
            rows.append(item)

    return rows


# Percorre todas as paginas do ranking e junta os resultados
def scrape_ranking(ranking_key):
    config = RANKINGS[ranking_key]
    all_rows = []

    for page in range(1, RANKING_TOTAL_PAGES + 1):
        url = f"{config['base_url']}?page={page}"
        html = fetch_html(url)
        all_rows.extend(parse_page(html, config))

        if page < RANKING_TOTAL_PAGES:
            time.sleep(PAGE_DELAY_SECONDS)

    return all_rows
