# ###################################################################
#          🎯 Projeto: Top Dividendos B3 Windows (Dia 16)          #
# ###################################################################
# 📁 Caminho: dia-16/dia16_top_dividendos_b3_windows.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: tkinter (interface), yfinance (dados)
# 🔗 Instalação: pip install yfinance tkinter
# ###################################################################

import contextlib
import io
import logging
import queue
import threading
from datetime import datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import ttk

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


def build_rows(symbols, label, emit_log, update_progress, state):
    emit_log(f"Buscando resultados para {label}")
    rows = []
    total = len(symbols)

    for index, symbol in enumerate(symbols, start=1):
        emit_log(f"[{index}/{total}] {symbol}...")
        try:
            ticker = yf.Ticker(y_symbol(symbol))

            price = get_price(ticker)
            if price <= 0:
                emit_log(f"[{symbol}] sem preco")
                continue

            month_dividend = get_estimated_month_dividend(ticker)
            if month_dividend <= 0:
                emit_log(f"[{symbol}] sem dividendos 12m")
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
            emit_log(f"[{symbol}] ok (DYm {month_yield_percent:.2f}%)")
        except Exception as exc:
            emit_log(f"[{symbol}] erro: {exc}")
        finally:
            state["done"] += 1
            update_progress(state["done"], state["total"])

    rows.sort(key=lambda item: item["monthly_yield_percent"], reverse=True)
    emit_log(f"Busca de {label} finalizada.")
    return rows[:TOP_N]


def format_rows_text(title, rows, with_kind=False):
    lines = [title, "=" * len(title)]

    if not rows:
        lines.append("Nenhum dado encontrado.")
        return "\n".join(lines)

    if with_kind:
        lines.append(f"{'#':<3} {'Tipo':<6} {'Ticker':<8} {'DYm%':>8} {'Preco':>10} {'Div Mes':>10} Nome")
        for index, row in enumerate(rows, start=1):
            lines.append(
                f"{index:<3} {row['kind']:<6} {row['symbol']:<8} {row['monthly_yield_percent']:>8.2f} "
                f"{row['price']:>10.2f} {row['monthly_payment']:>10.2f} {row['name']}"
            )
    else:
        lines.append(f"{'#':<3} {'Ticker':<8} {'DYm%':>8} {'Preco':>10} {'Div Mes':>10} Nome")
        for index, row in enumerate(rows, start=1):
            lines.append(
                f"{index:<3} {row['symbol']:<8} {row['monthly_yield_percent']:>8.2f} "
                f"{row['price']:>10.2f} {row['monthly_payment']:>10.2f} {row['name']}"
            )

    return "\n".join(lines)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Top Dividendos B3 - Dia 16 (Windows)")
        self.root.geometry("1100x720")

        style = ttk.Style()
        style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=(18, 10))

        self.events = queue.Queue()

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Top Dividendos B3 - Versao Windows", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        buttons = ttk.Frame(top)
        buttons.pack(anchor="w", pady=(8, 0))

        self.btn_acoes = ttk.Button(buttons, text="Top 5 Acoes", style="Action.TButton", width=16, command=lambda: self.start("acoes"))
        self.btn_fiis = ttk.Button(buttons, text="Top 5 FIIs", style="Action.TButton", width=16, command=lambda: self.start("fiis"))
        self.btn_geral = ttk.Button(buttons, text="Top 5 Geral", style="Action.TButton", width=16, command=lambda: self.start("geral"))

        self.btn_acoes.grid(row=0, column=0, padx=(0, 6))
        self.btn_fiis.grid(row=0, column=1, padx=(0, 6))
        self.btn_geral.grid(row=0, column=2)

        middle = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        middle.pack(fill="both", expand=True, padx=10, pady=10)

        logs_frame = ttk.Labelframe(middle, text="Logs")
        result_frame = ttk.Labelframe(middle, text="Resultado")
        middle.add(logs_frame, weight=1)
        middle.add(result_frame, weight=1)

        self.logs = tk.Text(logs_frame, height=20, wrap="word")
        self.logs.pack(fill="both", expand=True)

        self.result = tk.Text(result_frame, height=20, wrap="none")
        self.result.pack(fill="both", expand=True)

        bottom = ttk.Frame(root, padding=(10, 0, 10, 10))
        bottom.pack(fill="x")

        self.status_var = tk.StringVar(value="Pronto")
        ttk.Label(bottom, textvariable=self.status_var).pack(anchor="w")

        self.progress = ttk.Progressbar(bottom, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(6, 0))

        self.root.after(100, self.process_events)

    def log(self, message):
        self.events.put(("log", message))

    def set_progress(self, done, total):
        self.events.put(("progress", done, total))

    def set_result(self, text):
        self.events.put(("result", text))

    def mode_title(self, mode):
        if mode == "acoes":
            return "Top 5 Acoes"
        if mode == "fiis":
            return "Top 5 FIIs"
        return "Top 5 Geral"

    def set_running(self, running):
        state = "disabled" if running else "normal"
        self.btn_acoes.config(state=state)
        self.btn_fiis.config(state=state)
        self.btn_geral.config(state=state)

    def start(self, mode):
        self.progress["value"] = 0
        self.status_var.set("Processando...")
        self.set_running(True)

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        header = f"\n{'-' * 70}\nExecucao: {self.mode_title(mode)} | {now}\n{'-' * 70}\n"
        self.logs.insert(tk.END, header)
        self.logs.see(tk.END)

        thread = threading.Thread(target=self.run_mode, args=(mode,), daemon=True)
        thread.start()

    def run_mode(self, mode):
        try:
            if mode == "acoes":
                state = {"done": 0, "total": len(ACOES_LIST)}
                rows = build_rows(ACOES_LIST, "acoes", self.log, self.set_progress, state)
                text = format_rows_text("Top 5 Acoes por Dividend Yield do Mes", rows)
                self.set_result(text)

            elif mode == "fiis":
                state = {"done": 0, "total": len(FIIS_LIST)}
                rows = build_rows(FIIS_LIST, "FIIs", self.log, self.set_progress, state)
                text = format_rows_text("Top 5 FIIs por Dividend Yield do Mes", rows)
                self.set_result(text)

            else:
                state = {"done": 0, "total": len(ACOES_LIST) + len(FIIS_LIST)}
                stocks = build_rows(ACOES_LIST, "acoes", self.log, self.set_progress, state)
                funds = build_rows(FIIS_LIST, "FIIs", self.log, self.set_progress, state)

                combined = []
                for row in stocks:
                    combined.append({"kind": "Acao", **row})
                for row in funds:
                    combined.append({"kind": "FII", **row})

                combined.sort(key=lambda item: item["monthly_yield_percent"], reverse=True)
                combined = combined[:TOP_N]
                text = format_rows_text("Top 5 Geral (Acoes + FIIs) do Mes", combined, with_kind=True)
                self.set_result(text)

            self.events.put(("done", "Concluido"))
        except Exception as exc:
            self.events.put(("error", f"Erro: {exc}"))

    def process_events(self):
        while True:
            try:
                item = self.events.get_nowait()
            except queue.Empty:
                break

            kind = item[0]

            if kind == "log":
                self.logs.insert(tk.END, item[1] + "\n")
                self.logs.see(tk.END)
            elif kind == "progress":
                done, total = item[1], item[2]
                percent = (done / total) * 100 if total else 0
                self.progress["value"] = percent
                self.status_var.set(f"Processando... {done}/{total} ({percent:.1f}%)")
            elif kind == "result":
                if self.result.index("end-1c") != "1.0":
                    self.result.insert(tk.END, "\n\n")
                self.result.insert(tk.END, item[1])
                self.result.see(tk.END)
            elif kind == "done":
                self.progress["value"] = 100
                self.status_var.set(item[1])
                self.set_running(False)
            elif kind == "error":
                self.status_var.set(item[1])
                self.log(item[1])
                self.set_running(False)

        self.root.after(100, self.process_events)


def main():
    root = tk.Tk()
    # Adicionei a configuração do ícone da janela para o aplicativo Windows
    # coloque a sua logo em PNG sem fundo se
    logo_path = Path(__file__).with_name("logo_escura.png")
    if logo_path.exists():
        try:
            root._icon_image = tk.PhotoImage(file=str(logo_path))
            root.iconphoto(True, root._icon_image)
        except tk.TclError:
            pass

    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
