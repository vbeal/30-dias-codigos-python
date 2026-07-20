import re
from datetime import datetime

from bs4 import BeautifulSoup

from scraper.client import fetch_html

# Rotulos da secao "Informacoes sobre a empresa" (pagina de acao)
ACAO_INFO_LABELS = {
    "Valor de mercado": "valor_mercado",
    "Valor de firma": "valor_firma",
    "Patrimônio Líquido": "patrimonio_liquido",
    "Nº total de papeis": "total_papeis",
    "Ativos": "ativos",
    "Ativo Circulante": "ativo_circulante",
    "Dívida Bruta": "divida_bruta",
    "Dívida Líquida": "divida_liquida",
    "Disponibilidade": "disponibilidade",
    "Segmento de Listagem": "segmento_listagem",
    "Free Float": "free_float",
    "Tag Along": "tag_along",
    "Liquidez Média Diária": "liquidez_media_diaria",
    "Setor": "setor",
    "Segmento": "segmento",
}

# Rotulos da tabela "Dados sobre a empresa"
EMPRESA_LABELS = {
    "Nome da Empresa:": "nome",
    "CNPJ:": "cnpj",
    "Ano de estreia na bolsa:": "ano_estreia_bolsa",
    "Número de funcionários:": "numero_funcionarios",
    "Ano de fundação:": "ano_fundacao",
}


# Extrai o valor de uma celula (suporta simple-value e value normal)
def cell_value(cell):
    value_el = cell.find("div", class_="value") or cell.find("span", class_="value")
    if not value_el:
        return ""

    simple = value_el.find("div", class_="simple-value")
    if simple:
        return simple.get_text(" ", strip=True)

    return value_el.get_text(" ", strip=True)


# Le os cards do topo (cotacao, P/L, P/VP, DY, variacao 12m)
def parse_acao_cards(soup):
    cotacao = {}
    for card in soup.select("div._card"):
        classes = card.get("class", [])
        text = card.get_text(" ", strip=True)

        if "cotacao" in classes:
            price_match = re.search(r"R\$\s*[\d.,]+", text)
            pct_match = re.search(r"(-?\d+[,.]\d+)%\s*$", text)
            cotacao["preco"] = price_match.group(0) if price_match else ""
            cotacao["variacao_dia"] = f"{pct_match.group(1)}%" if pct_match else ""
        elif "VARIA" in text.upper():
            value = re.search(r"(-?\d+[,.]\d+)%", text)
            cotacao["variacao_12m"] = value.group(0) if value else ""
        elif text.startswith("P/L"):
            value = re.search(r"P/L\s*(-?\d+[,.]\d+)", text)
            cotacao["pl"] = value.group(1) if value else ""
        elif "P/VP" in text:
            value = re.search(r"P/VP\s*(-?\d+[,.]\d+)", text)
            cotacao["pvp"] = value.group(1) if value else ""
        elif re.match(r"^DY\b", text):
            value = re.search(r"DY\s*(-?\d+[,.]\d+)%", text)
            cotacao["dy"] = value.group(0).replace("DY ", "") if value else ""

    return cotacao


# Le a tabela com nome, CNPJ, ano de estreia, etc.
def parse_empresa_table(soup):
    empresa = {}
    for table in soup.find_all("table"):
        first_row = table.find("tr")
        if not first_row or "Nome da Empresa" not in first_row.get_text():
            continue

        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            label = cols[0].get_text(" ", strip=True)
            key = EMPRESA_LABELS.get(label)
            if key:
                empresa[key] = cols[1].get_text(" ", strip=True)

        break

    return empresa


# Le tickers listados em "Papeis da empresa" ou "Papeis Fracionados"
def parse_ticker_tags(soup, title_text):
    header = None
    for h5 in soup.find_all("h5"):
        if title_text in h5.get_text(" ", strip=True):
            header = h5
            break

    if not header:
        return []

    tickers = []
    for sibling in header.find_next_siblings():
        if sibling.name == "h5":
            break

        for link in sibling.select("div.tag-ticker a"):
            ticker = link.get_text(" ", strip=True).upper()
            if ticker and ticker not in tickers:
                tickers.append(ticker)

    return tickers


# Le celulas de informacoes financeiras (valor de mercado, setor, etc.)
def parse_acao_cells(soup):
    informacoes = {}
    for cell in soup.select("div.cell"):
        label_el = cell.find("span", class_="title") or cell.find("span")
        if not label_el:
            continue

        label = label_el.get_text(" ", strip=True)
        key = ACAO_INFO_LABELS.get(label)
        if key:
            informacoes[key] = cell_value(cell)

    return informacoes


# Scrape completo da pagina de uma Acao no Investidor10
def scrape_acao_detail(ticker):
    slug = ticker.strip().lower()
    url = f"https://investidor10.com.br/acoes/{slug}/"
    soup = BeautifulSoup(fetch_html(url), "html.parser")

    empresa = parse_empresa_table(soup)
    empresa["papeis"] = parse_ticker_tags(soup, "Papéis da empresa")
    empresa["papeis_fracionados"] = parse_ticker_tags(soup, "Papéis Fracionados")

    return {
        "tipo": "acao",
        "ativo": ticker.strip().upper(),
        "fonte": url,
        "consultado_em": datetime.now().isoformat(timespec="seconds"),
        "cotacao": parse_acao_cards(soup),
        "empresa": empresa,
        "informacoes": parse_acao_cells(soup),
    }
