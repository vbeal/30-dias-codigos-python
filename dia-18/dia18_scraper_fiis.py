# ###################################################################
#          🎯 Projeto: Scraper FIIs Investidor10 (Dia 18)          #
# ###################################################################
# 📁 Caminho: dia-18/dia18_scraper_fiis.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: requests (HTTP), beautifulsoup4 (parse HTML)
# 🔗 Instalação: pip install requests beautifulsoup4
# 🌐 Fonte: https://investidor10.com.br/fiis/rankings/maior-dividend-yield/
# ###################################################################

# O requests baixa o HTML do site, o BeautifulSoup desmonta essa página 
# em partes (table → tr → td), nós lemos cada linha da tabela pelas 
# posições das colunas e imprimimos os textos no terminal.
# ---------------------------------------------------------------------
# Site Investidor10
#     ↓  (retorna HTML — a página com a tabela)
# requests.get()
#     ↓  (texto HTML em memória)
# BeautifulSoup
#     ↓  (árvore navegável: table, tr, td...)
# Nosso código extrai textos
#     ↓  ("CACR11", "54,36%", "Híbrido"...)
# print no terminal
#     ↓  (texto puro, tabela alinhada)
# ---------------------------------------------------------------------

import re
import sys
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# URL base do ranking e quantidade de paginas do site
BASE_URL = "https://investidor10.com.br/fiis/rankings/maior-dividend-yield/"
TOTAL_PAGES = 3
PAGE_DELAY_SECONDS = 1  # pausa entre paginas para nao sobrecarregar o site

# Cabecalho HTTP: simula um navegador real e evita bloqueio
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}

# Indices das colunas na tabela HTML (a tabela tem 11 colunas no total)
COL_ATIVO = 0
COL_DIVIDEND_YIELD = 1
COL_PATRIMONIO = 3          # coluna 2 e o DY medio de 5 anos (nao usamos)
COL_PVP = 4
COL_VARIACAO_12M = 7        # colunas 5 e 6 sao liquidez e tipo de fundo
COL_SEGMENTO = 10


# Baixa o HTML de uma pagina do ranking
def fetch_page(page):
    url = f"{BASE_URL}?page={page}"
    print(f"Buscando pagina {page}/{TOTAL_PAGES}...")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()  # lanca erro se a pagina nao carregar (404, 500, etc.)
    return response.text


# Extrai o ticker (ex: CACR11) da primeira coluna da tabela
def extract_ticker(ativo_cell):
    # Preferencia: pegar o ticker pelo link do ativo (/fiis/cacr11/)
    link = ativo_cell.find("a", href=True)
    if link and "/fiis/" in link["href"]:
        slug = link["href"].rstrip("/").split("/")[-1]
        return slug.upper()

    # Plano B: buscar o padrao TICKER no texto da celula
    text = ativo_cell.get_text(" ", strip=True)
    match = re.search(r"#\d+\s+([A-Z]{4}\d{2})\b", text)
    if match:
        return match.group(1)

    return text


# Le uma linha <tr> da tabela e devolve um dicionario com os dados
def parse_row(row):
    cols = row.find_all("td")
    if len(cols) <= COL_SEGMENTO:
        return None

    return {
        "ativo": extract_ticker(cols[COL_ATIVO]),
        "dividend_yield": cols[COL_DIVIDEND_YIELD].get_text(" ", strip=True),
        "patrimonio_liquido": cols[COL_PATRIMONIO].get_text(" ", strip=True),
        "pvp": cols[COL_PVP].get_text(" ", strip=True),
        "variacao_12m": cols[COL_VARIACAO_12M].get_text(" ", strip=True),
        "segmento": cols[COL_SEGMENTO].get_text(" ", strip=True),
    }


# Converte o HTML da pagina em uma lista de FIIs
def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")  # transforma HTML em objeto navegavel
    table = soup.find("table")
    if not table:
        return []

    rows = []
    for row in table.find_all("tr")[1:]:  # [1:] pula a linha de cabecalho
        item = parse_row(row)
        if item:
            rows.append(item)

    return rows


# Percorre todas as paginas e junta os resultados em uma unica lista
def scrape_fiis():
    all_rows = []

    for page in range(1, TOTAL_PAGES + 1):
        html = fetch_page(page)
        page_rows = parse_page(html)
        all_rows.extend(page_rows)
        print(f"  -> {len(page_rows)} FIIs encontrados nesta pagina.")

        if page < TOTAL_PAGES:
            time.sleep(PAGE_DELAY_SECONDS)

    return all_rows


# Exibe os dados coletados em formato de tabela no terminal
def print_table(rows):
    title = "Ranking FIIs - Maiores Dividend Yield (Investidor10)"
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


# Funcao principal: busca os dados e exibe no terminal
def main():
    # Corrige acentos no terminal do Windows (ex: Hibrido, Titulos)
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    started_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print("\n" + "=" * 55)
    print("  Scraper FIIs - Dia 18")
    print(f"  Inicio: {started_at}")
    print("=" * 55)

    try:
        rows = scrape_fiis()   # 1) busca os dados no site
        print_table(rows)      # 2) mostra a tabela no terminal
        print(f"\nTotal: {len(rows)} FIIs coletados.")
    except requests.RequestException as exc:
        print(f"\nErro ao acessar o site: {exc}")
    except Exception as exc:
        print(f"\nErro inesperado: {exc}")


if __name__ == "__main__":
    main()
