# ###################################################################
#          🎯 Projeto: Top Dividendos B3 (Dia 15)                  #
# ###################################################################
# 📁 Caminho: dia-15/dia15_top_dividendos_b3.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: yfinance (consulta de cotações e dividendos Yahoo Finance)
# 🔗 Instalação: pip install yfinance 
# Digite-> .venv\Scripts\activate  
# No prompt do Windows para instalar localmente as bibliotecas
# Configuração: config.py (definir ACOES_LIST, FIIS_LIST e TOP_N)
# ###################################################################

import contextlib
import io
import logging
from datetime import datetime, timedelta

import yfinance as yf

from config import ACOES_LIST, FIIS_LIST, TOP_N

logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("curl_cffi").setLevel(logging.CRITICAL)


def y_symbol(symbol):
    return symbol if symbol.endswith(".SA") else f"{symbol}.SA"


def quiet_call(func, *args, **kwargs):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            return func(*args, **kwargs)
    except Exception:
        return None


def get_price(ticker):
    try:
        fast = quiet_call(lambda: ticker.fast_info) or {}
        for key in ("last_price", "lastPrice", "regular_market_price"):
            value = fast.get(key)
            if value is not None:
                return float(value)
    except Exception:
        pass

    try:
        hist = quiet_call(ticker.history, period="5d")
        if hist is not None and not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])
    except Exception:
        pass

    return 0.0


def get_estimated_month_dividend(ticker):
    # DYm estimado: soma dos proventos dos ultimos 12 meses / 12.
    cutoff = datetime.now() - timedelta(days=365)
    try:
        divs = quiet_call(lambda: ticker.dividends)
    except Exception:
        return 0.0

    if divs is None or len(divs) == 0:
        return 0.0

    try:
        index_no_tz = divs.index.tz_localize(None)
    except Exception:
        try:
            index_no_tz = divs.index.tz_convert(None)
        except Exception:
            index_no_tz = divs.index

    last_12m = divs[index_no_tz >= cutoff]
    if len(last_12m) == 0:
        return 0.0

    annual_dividend = float(last_12m.sum())
    return annual_dividend / 12.0


def build_rows(symbols, label):
    print(f"Buscando resultados para {label}")
    rows = []
    total = len(symbols)

    for index, symbol in enumerate(symbols, start=1):
        print(f"[{index}/{total}] {symbol}...", end="", flush=True)
        ticker = yf.Ticker(y_symbol(symbol))

        price = get_price(ticker)
        if price <= 0:
            print(" sem preco")
            continue

        month_dividend = get_estimated_month_dividend(ticker)
        if month_dividend <= 0:
            print(" sem dividendos 12m")
            continue

        month_yield_percent = (month_dividend / price) * 100
        rows.append(
            {
                "symbol": symbol,
                "name": symbol,
                "price": price,
                "monthly_payment": month_dividend,
                "monthly_yield_percent": month_yield_percent,
            }
        )
        print(f" ok (DYm {month_yield_percent:.2f}%)")

    print(f"Busca de {label} finalizada.")
    rows.sort(key=lambda item: item["monthly_yield_percent"], reverse=True)
    return rows[:TOP_N]


def print_table(title, rows, is_fii=False):
    print("\n" + title)
    print("=" * len(title))

    if not rows:
        print("Nenhum dado encontrado.")
        return

    if is_fii:
        print(f"{'#':<3} {'Ticker':<8} {'DYm%':>8} {'Preco':>10} {'Div Mes':>10} Nome")
    else:
        print(f"{'#':<3} {'Ticker':<8} {'DYm%':>8} {'Preco':>10} {'Div Mes':>10} Nome")

    for index, row in enumerate(rows, start=1):
        print(
            f"{index:<3} {row['symbol']:<8} {row['monthly_yield_percent']:>8.2f} {row['price']:>10.2f} {row['monthly_payment']:>10.2f} {row['name']}"
        )

def build_top_stocks(acoes):
    return build_rows(acoes, "acoes")


def build_top_fiis(fiis):
    return build_rows(fiis, "FIIs")


def main():
    acoes = ACOES_LIST
    fiis = FIIS_LIST

    while True:
        print("\nTop Dividendos B3 - Dia 15")
        print("1) Top 5 acoes pagadoras do mes")
        print("2) Top 5 FIIs pagadores do mes")
        print("3) Top 5 geral (acoes + FIIs) do mes")
        print("0) Sair")

        option = input("\nEscolha uma opcao: ").strip()

        if option == "0":
            print("Saindo...")
            break

        if option == "1":
            stocks = build_top_stocks(acoes)
            print_table("Top 5 Acoes por Dividend Yield do Mes", stocks, is_fii=False)
            input("\nPressione ENTER para voltar ao menu...")
            continue

        if option == "2":
            funds = build_top_fiis(fiis)
            print_table("Top 5 FIIs por Dividend Yield do Mes", funds, is_fii=True)
            input("\nPressione ENTER para voltar ao menu...")
            continue

        if option == "3":
            stocks = build_top_stocks(acoes)
            funds = build_top_fiis(fiis)
            combined = []
            for row in stocks:
                combined.append({"kind": "Acao", **row})
            for row in funds:
                combined.append({"kind": "FII", **row})
            combined.sort(key=lambda item: item["monthly_yield_percent"], reverse=True)
            combined = combined[:TOP_N]

            print("\nTop 5 Geral (Acoes + FIIs) do Mes")
            print("=" * 33)
            print(f"{'#':<3} {'Tipo':<6} {'Ticker':<8} {'DYm%':>8} {'Preco':>10} {'Div Mes':>10} Nome")
            for index, row in enumerate(combined, start=1):
                print(
                    f"{index:<3} {row['kind']:<6} {row['symbol']:<8} {row['monthly_yield_percent']:>8.2f} {row['price']:>10.2f} {row['monthly_payment']:>10.2f} {row['name']}"
                )

            input("\nPressione ENTER para voltar ao menu...")
            continue

        print("Opcao invalida.")
        input("\nPressione ENTER para voltar ao menu...")


if __name__ == '__main__':
    main()
