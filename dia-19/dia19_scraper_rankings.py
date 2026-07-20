# ###################################################################
#     🎯 Projeto: Scraper FIIs + Ações Investidor10 (Dia 19)       #
# ###################################################################
# 📁 Caminho: dia-19/dia19_scraper_rankings.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: requests (HTTP), beautifulsoup4 (parse HTML)
# 🔗 Instalação: pip install requests beautifulsoup4
# 🌐 Fontes:
#    - FIIs:  investidor10.com.br/fiis/rankings/maior-dividend-yield/
#    - Ações: investidor10.com.br/acoes/rankings/maiores-dividend-yield/
# 💾 Saída: terminal + arquivo JSON em data/rankings.json
# ###################################################################

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
JSON_OUTPUT = BASE_DIR / "data" / "rankings.json"

TOTAL_PAGES = 3
PAGE_DELAY_SECONDS = 1

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}

# Configuracao de cada ranking (FIIs e Acoes tem colunas em posicoes diferentes)
RANKINGS = {
    "fiis": {
        "titulo": "Ranking FIIs - Maiores Dividend Yield",
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
        "titulo": "Ranking Acoes - Maiores Dividend Yield",
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


# Baixa o HTML de uma pagina do ranking
def fetch_page(base_url, page, label):
    url = f"{base_url}?page={page}"
    print(f"  Buscando {label} - pagina {page}/{TOTAL_PAGES}...")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


# Extrai o ticker (ex: CACR11 ou PETR4) da primeira coluna da tabela
def extract_ticker(ativo_cell, link_path):
    link = ativo_cell.find("a", href=True)
    if link and link_path in link["href"]:
        slug = link["href"].rstrip("/").split("/")[-1]
        return slug.upper()

    text = ativo_cell.get_text(" ", strip=True)
    match = re.search(r"#\d+\s+([A-Z]{4}\d{1,2})\b", text)
    if match:
        return match.group(1)

    return text


# Le uma linha <tr> da tabela e devolve um dicionario com os dados
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


# Converte o HTML da pagina em uma lista de ativos
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


# Percorre todas as paginas de um ranking e junta os resultados
def scrape_ranking(ranking_key):
    config = RANKINGS[ranking_key]
    label = ranking_key.upper()
    all_rows = []

    print(f"\nColetando {label}...")
    for page in range(1, TOTAL_PAGES + 1):
        html = fetch_page(config["base_url"], page, label)
        page_rows = parse_page(html, config)
        all_rows.extend(page_rows)
        print(f"    -> {len(page_rows)} ativos nesta pagina.")

        if page < TOTAL_PAGES:
            time.sleep(PAGE_DELAY_SECONDS)

    return all_rows


# Exibe os dados coletados em formato de tabela no terminal
def print_table(title, rows):
    print("\n" + title)
    print("=" * len(title))

    if not rows:
        print("Nenhum dado encontrado.")
        return

    header = (
        f"{'#':<4} {'Ativo':<8} {'DY':>8} {'Patrim.':>12} "
        f"{'P/VP':>6} {'Var 12m':>9} Segmento"
    )
    print(header)
    print("-" * len(header))

    for index, row in enumerate(rows, start=1):
        print(
            f"{index:<4} {row['ativo']:<8} {row['dividend_yield']:>8} "
            f"{row['patrimonio_liquido']:>12} {row['pvp']:>6} "
            f"{row['variacao_12m']:>9} {row['segmento']}"
        )


# Salva FIIs e Acoes em um arquivo JSON
def save_json(fiis, acoes):
    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "atualizado_em": datetime.now().isoformat(timespec="seconds"),
        "fonte": "investidor10.com.br",
        "total_fiis": len(fiis),
        "total_acoes": len(acoes),
        "fiis": fiis,
        "acoes": acoes,
    }

    with JSON_OUTPUT.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return JSON_OUTPUT


# Funcao principal: busca FIIs e Acoes, exibe no terminal e salva JSON
def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    started_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print("\n" + "=" * 58)
    print("  Scraper FIIs + Acoes - Dia 19")
    print(f"  Inicio: {started_at}")
    print("=" * 58)

    try:
        fiis = scrape_ranking("fiis")
        acoes = scrape_ranking("acoes")

        print_table(RANKINGS["fiis"]["titulo"], fiis)
        print_table(RANKINGS["acoes"]["titulo"], acoes)

        json_path = save_json(fiis, acoes)

        print(f"\nTotal FIIs: {len(fiis)}")
        print(f"Total Acoes: {len(acoes)}")
        print(f"JSON salvo em: {json_path}")
    except requests.RequestException as exc:
        print(f"\nErro ao acessar o site: {exc}")
    except Exception as exc:
        print(f"\nErro inesperado: {exc}")


if __name__ == "__main__":
    main()
