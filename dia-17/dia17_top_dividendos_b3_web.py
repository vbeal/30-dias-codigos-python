# ###################################################################
#          🎯 Projeto: Top Dividendos B3 Web (Dia 17)              #
# ###################################################################
# 📁 Caminho: dia-17/dia17_top_dividendos_b3_web.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: flask (web), yfinance (dados B3)
# 🔗 Instalação: pip install flask yfinance
# Configuração: config.py (ACOES_LIST, FIIS_LIST e TOP_N)
# 🌐 Web: Flask + Bootstrap + Chart.js (gráficos no navegador)
# ###################################################################

import contextlib
import io
import logging
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import yfinance as yf
from flask import Flask, jsonify, render_template, request

from config import ACOES_LIST, FIIS_LIST, TOP_N

logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("curl_cffi").setLevel(logging.CRITICAL)

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="/assets")

jobs = {}
jobs_lock = threading.Lock()


def y_symbol(symbol):
    return symbol if symbol.endswith(".SA") else f"{symbol}.SA"


def quiet_call(func, *args, **kwargs):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            return func(*args, **kwargs)
    except Exception:
        return None


def safe_fast_value(fast_info_obj, key):
    try:
        return fast_info_obj.get(key)
    except Exception:
        return None


def get_price(ticker):
    fast = quiet_call(lambda: ticker.fast_info) or {}
    for key in ("last_price", "lastPrice", "regular_market_price"):
        value = safe_fast_value(fast, key)
        if value is not None:
            return float(value)

    hist = quiet_call(ticker.history, period="5d")
    if hist is not None and not hist.empty:
        return float(hist["Close"].dropna().iloc[-1])

    return 0.0


def get_estimated_month_dividend(ticker):
    cutoff = datetime.now() - timedelta(days=365)
    divs = quiet_call(lambda: ticker.dividends)

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


def get_job(job_id):
    with jobs_lock:
        return jobs.get(job_id)


def append_log(job_id, message):
    with jobs_lock:
        job = jobs.get(job_id)
        if job:
            job["logs"].append(message)


def update_progress(job_id, done, total):
    with jobs_lock:
        job = jobs.get(job_id)
        if job:
            job["done"] = done
            job["total"] = total


def finish_job(job_id, rows, title, with_kind=False):
    with jobs_lock:
        job = jobs.get(job_id)
        if job:
            job["status"] = "done"
            job["done"] = job["total"]
            job["result"] = {"title": title, "rows": rows, "with_kind": with_kind}


def fail_job(job_id, message):
    with jobs_lock:
        job = jobs.get(job_id)
        if job:
            job["status"] = "error"
            job["error"] = message
            job["logs"].append(message)


def build_rows(job_id, symbols, label):
    append_log(job_id, f"Buscando resultados para {label}")
    rows = []
    total = len(symbols)

    for index, symbol in enumerate(symbols, start=1):
        append_log(job_id, f"[{index}/{total}] {symbol}...")
        try:
            ticker = yf.Ticker(y_symbol(symbol))
            price = get_price(ticker)
            if price <= 0:
                append_log(job_id, f"[{symbol}] sem preco")
                continue

            month_dividend = get_estimated_month_dividend(ticker)
            if month_dividend <= 0:
                append_log(job_id, f"[{symbol}] sem dividendos 12m")
                continue

            month_yield_percent = (month_dividend / price) * 100
            rows.append(
                {
                    "symbol": symbol,
                    "name": symbol,
                    "price": round(price, 2),
                    "monthly_payment": round(month_dividend, 2),
                    "monthly_yield_percent": round(month_yield_percent, 2),
                }
            )
            append_log(job_id, f"[{symbol}] ok (DYm {month_yield_percent:.2f}%)")
        except Exception as exc:
            append_log(job_id, f"[{symbol}] erro: {exc}")
        finally:
            job = get_job(job_id)
            if job:
                update_progress(job_id, job["done"] + 1, job["total"])

    rows.sort(key=lambda item: item["monthly_yield_percent"], reverse=True)
    append_log(job_id, f"Busca de {label} finalizada.")
    return rows[:TOP_N]


def run_mode(job_id, mode):
    try:
        if mode == "acoes":
            with jobs_lock:
                jobs[job_id]["total"] = len(ACOES_LIST)
            rows = build_rows(job_id, ACOES_LIST, "acoes")
            finish_job(job_id, rows, "Top 5 Acoes por Dividend Yield do Mes")

        elif mode == "fiis":
            with jobs_lock:
                jobs[job_id]["total"] = len(FIIS_LIST)
            rows = build_rows(job_id, FIIS_LIST, "FIIs")
            finish_job(job_id, rows, "Top 5 FIIs por Dividend Yield do Mes")

        else:
            with jobs_lock:
                jobs[job_id]["total"] = len(ACOES_LIST) + len(FIIS_LIST)

            stocks = build_rows(job_id, ACOES_LIST, "acoes")
            funds = build_rows(job_id, FIIS_LIST, "FIIs")

            combined = []
            for row in stocks:
                combined.append({"kind": "Acao", **row})
            for row in funds:
                combined.append({"kind": "FII", **row})

            combined.sort(key=lambda item: item["monthly_yield_percent"], reverse=True)
            combined = combined[:TOP_N]
            finish_job(job_id, combined, "Top 5 Geral (Acoes + FIIs) do Mes", with_kind=True)

    except Exception as exc:
        fail_job(job_id, f"Erro: {exc}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def api_start():
    payload = request.get_json(silent=True) or {}
    mode = payload.get("mode", "").strip().lower()

    if mode not in {"acoes", "fiis", "geral"}:
        return jsonify({"error": "Modo invalido."}), 400

    job_id = str(uuid.uuid4())
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with jobs_lock:
        jobs[job_id] = {
            "status": "running",
            "mode": mode,
            "done": 0,
            "total": 0,
            "logs": [f"Execucao iniciada em {now}"],
            "result": None,
            "error": None,
        }

    thread = threading.Thread(target=run_mode, args=(job_id, mode), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def api_status(job_id):
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job nao encontrado."}), 404

    percent = 0
    if job["total"] > 0:
        percent = round((job["done"] / job["total"]) * 100, 1)

    return jsonify(
        {
            "status": job["status"],
            "done": job["done"],
            "total": job["total"],
            "percent": percent,
            "logs": job["logs"],
            "result": job["result"],
            "error": job.get("error"),
        }
    )


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Top Dividendos B3 - Dia 17 (Web)")
    print("  Servidor iniciado com sucesso!")
    print("  Acesse no navegador: http://127.0.0.1:5000")
    print("  Pressione Ctrl+C para encerrar")
    print("=" * 50 + "\n")
    app.run(debug=True)
