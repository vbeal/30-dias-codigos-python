# Validacao e parse do formulario do Radar (Dia 29)

from datetime import datetime

DIRECOES = {"compra", "venda"}


def parse_preco_br(texto):
    """Converte '72,60' ou '1.234,56' para float. Retorna None se vazio/invalido."""
    s = (texto or "").strip().replace("R$", "").strip()
    if not s:
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        valor = float(s)
    except ValueError:
        return None
    if valor < 0:
        return None
    return valor


def format_preco_br(valor):
    if valor is None:
        return ""
    return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_data_iso(texto):
    """Aceita YYYY-MM-DD (input type=date)."""
    s = (texto or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return None


def extrair_radar_do_form(form, ativos_por_ticker):
    """
    Le request.form e devolve (ok, erro_ou_none, payload).
    payload = {nome, data_inicio, data_fim, ativos: [...]}
    """
    nome = (form.get("nome") or "").strip()
    if not nome:
        return False, "Informe um nome para o radar.", None
    if len(nome) > 80:
        return False, "Nome muito longo (max. 80).", None

    data_inicio = parse_data_iso(form.get("data_inicio"))
    data_fim = parse_data_iso(form.get("data_fim"))
    if not data_inicio or not data_fim:
        return False, "Informe data de inicio e fim validas.", None
    if data_fim < data_inicio:
        return False, "Data fim nao pode ser anterior a data inicio.", None

    tickers = form.getlist("ticker")
    direcoes = form.getlist("direcao")
    entradas = form.getlist("preco_entrada")
    tetos = form.getlist("preco_teto")
    alvos = form.getlist("preco_alvo")
    stops = form.getlist("preco_stop")
    cortes = form.getlist("preco_corte")

    n = len(tickers)
    if n == 0:
        return False, "Adicione ao menos um ativo.", None
    if not all(len(lst) == n for lst in (direcoes, entradas, tetos, alvos, stops, cortes)):
        return False, "Formulario incompleto (linhas inconsistentes).", None

    ativos = []
    vistos = set()
    for i in range(n):
        ticker = (tickers[i] or "").strip().upper()
        if not ticker:
            continue
        if ticker in vistos:
            return False, f"Ticker duplicado: {ticker}.", None
        info = ativos_por_ticker.get(ticker)
        if not info:
            return False, f"Ativo fora da lista: {ticker}.", None

        direcao = (direcoes[i] or "").strip().lower()
        if direcao not in DIRECOES:
            return False, f"Direcao invalida em {ticker} (use compra ou venda).", None

        campos = {
            "preco_entrada": parse_preco_br(entradas[i]),
            "preco_teto": parse_preco_br(tetos[i]),
            "preco_alvo": parse_preco_br(alvos[i]),
            "preco_stop": parse_preco_br(stops[i]),
            "preco_corte": parse_preco_br(cortes[i]),
        }
        faltando = [k for k, v in campos.items() if v is None]
        if faltando:
            return False, f"Precos invalidos em {ticker}. Use formato 72,60.", None

        vistos.add(ticker)
        ativos.append(
            {
                "ticker": ticker,
                "tipo_ativo": info["tipo"],
                "direcao": direcao,
                **campos,
            }
        )

    if not ativos:
        return False, "Adicione ao menos um ativo com ticker valido.", None

    return True, None, {
        "nome": nome,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "ativos": ativos,
    }


def status_periodo(data_inicio, data_fim, hoje=None):
    """Retorna 'futuro' | 'ativo' | 'encerrado' (hoje em America/Sao_Paulo)."""
    if hoje is None:
        from web.timezone_util import hoje_sp

        hoje = hoje_sp().isoformat()
    if hoje < data_inicio:
        return "futuro"
    if hoje > data_fim:
        return "encerrado"
    return "ativo"
