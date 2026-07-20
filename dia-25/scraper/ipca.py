# Novidade Dia 25: IPCA acumulado 12 meses (Investidor10)
import re
from datetime import datetime

from bs4 import BeautifulSoup

from scraper.client import fetch_html

IPCA_URL = "https://investidor10.com.br/indices/ipca/"


def parse_pct(texto) -> float | None:
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


def scrape_ipca() -> dict:
    """
    Le a pagina de indices/IPCA.
    Retorna IPCA do mes, acumulado 12M e no ano (quando disponivel).
    """
    html = fetch_html(IPCA_URL)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    ipca_mes = None
    ipca_12m = None
    ipca_ano = None

    m_hoje = re.search(
        r"IPCA hoje[^\d\-]*(-?\d+[.,]\d+)\s*%",
        text,
        re.IGNORECASE,
    )
    if m_hoje:
        ipca_mes = parse_pct(m_hoje.group(1))

    m_12 = re.search(
        r"acumulado nos [uú]ltimos 12 meses[^\d\-]*(-?\d+[.,]\d+)\s*%",
        text,
        re.IGNORECASE,
    )
    if m_12:
        ipca_12m = parse_pct(m_12.group(1))

    m_ano = re.search(
        r"acumulado no ano[^\d\-]*(-?\d+[.,]\d+)\s*%",
        text,
        re.IGNORECASE,
    )
    if m_ano:
        ipca_ano = parse_pct(m_ano.group(1))

    # Fallback: primeira linha da tabela (Acumulado 12 meses)
    if ipca_12m is None:
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            if len(rows) > 1:
                cols = rows[1].find_all(["td", "th"])
                if len(cols) >= 4:
                    ipca_12m = parse_pct(cols[3].get_text(" ", strip=True))
                if ipca_mes is None and len(cols) >= 2:
                    ipca_mes = parse_pct(cols[1].get_text(" ", strip=True))

    if ipca_12m is None:
        raise ValueError("Nao foi possivel ler o IPCA 12 meses no Investidor10.")

    return {
        "fonte": IPCA_URL,
        "consultado_em": datetime.now().isoformat(timespec="seconds"),
        "ipca_mes": ipca_mes,
        "ipca_12m": ipca_12m,
        "ipca_ano": ipca_ano,
    }
