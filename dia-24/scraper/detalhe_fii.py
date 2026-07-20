import re
from datetime import datetime

from bs4 import BeautifulSoup

from scraper.client import fetch_html

# Mapeia os rotulos da pagina do FII para chaves do JSON
FII_INFO_LABELS = {
    "Razão Social": "razao_social",
    "CNPJ": "cnpj",
    "PÚBLICO-ALVO": "publico_alvo",
    "MANDATO": "mandato",
    "SEGMENTO": "segmento",
    "TIPO DE FUNDO": "tipo_de_fundo",
    "PRAZO DE DURAÇÃO": "prazo_de_duracao",
    "TIPO DE GESTÃO": "tipo_de_gestao",
    "TAXA DE ADMINISTRAÇÃO": "taxa_de_administracao",
    "VACÂNCIA": "vacancia",
    "NUMERO DE COTISTAS": "numero_de_cotistas",
    "COTAS EMITIDAS": "cotas_emitidas",
    "VAL. PATRIMONIAL P/ COTA": "valor_patrimonial_por_cota",
    "VALOR PATRIMONIAL": "valor_patrimonial",
    "ÚLTIMO RENDIMENTO": "ultimo_rendimento",
}


# Le os cards do topo da pagina (cotacao, DY, P/VP, liquidez, variacao)
def parse_fii_cards(soup):
    cotacao = {}
    for card in soup.select("div._card"):
        classes = card.get("class", [])
        text = card.get_text(" ", strip=True)
        header = card.select_one("div._card-header")
        label = header.get_text(" ", strip=True) if header else ""

        if "cotacao" in classes:
            price_match = re.search(r"R\$\s*[\d.,]+", text)
            pct_match = re.search(r"(-?\d+[,.]\d+)%\s*$", text)
            cotacao["preco"] = price_match.group(0) if price_match else ""
            cotacao["variacao_dia"] = f"{pct_match.group(1)}%" if pct_match else ""
        elif "dy" in classes and "DY" in label.upper():
            value = re.search(r"(-?\d+[,.]\d+)%", text)
            cotacao["dy_12m"] = value.group(0) if value else ""
        elif "vp" in classes:
            value = re.search(r"(-?\d+[,.]\d+)", text)
            cotacao["pvp"] = value.group(1) if value else ""
        elif "val" in classes:
            value = re.search(r"R\$\s*[\d.,]+\s*[MBK]?", text)
            cotacao["liquidez_diaria"] = value.group(0) if value else ""
        elif "VARIA" in label.upper():
            value = re.search(r"(-?\d+[,.]\d+)%", text)
            cotacao["variacao_12m"] = value.group(0) if value else ""

    return cotacao


# Le a secao "Informacoes" com div.cell (razao social, CNPJ, etc.)
def parse_fii_cells(soup):
    informacoes = {}
    for cell in soup.select("div.cell"):
        label_el = cell.find("span")
        value_el = cell.find("div", class_="value")
        if not label_el or not value_el:
            continue

        label = label_el.get_text(" ", strip=True)
        key = FII_INFO_LABELS.get(label)
        if key:
            informacoes[key] = value_el.get_text(" ", strip=True)

    return informacoes


# Scrape completo da pagina de um FII no Investidor10
def scrape_fii_detail(ticker):
    slug = ticker.strip().lower()
    url = f"https://investidor10.com.br/fiis/{slug}/"
    soup = BeautifulSoup(fetch_html(url), "html.parser")

    return {
        "tipo": "fii",
        "ativo": ticker.strip().upper(),
        "fonte": url,
        "consultado_em": datetime.now().isoformat(timespec="seconds"),
        "cotacao": parse_fii_cards(soup),
        "informacoes": parse_fii_cells(soup),
    }
