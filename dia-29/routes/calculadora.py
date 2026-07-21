# Rotas: calculadora de dividendos

import requests
from flask import jsonify, render_template, request

from scraper.ipca import scrape_ipca
from services.calculadora_dividendos import PERIODOS_MESES, TAXA_REAL_DEFAULT, build_simulacao
from services.detalhe_ativo import TIPOS_DETALHE, limpar_ticker
from web.helpers import ATIVOS_POR_TICKER, login_required


def register(app):
    @app.route("/calculadora")
    @login_required
    def calculadora():
        ticker = limpar_ticker(request.args.get("ticker", ""))
        tipo = (request.args.get("tipo") or "").strip().lower()
        if ticker and tipo not in TIPOS_DETALHE:
            item = ATIVOS_POR_TICKER.get(ticker)
            if item:
                tipo = item["tipo"]
        if tipo not in TIPOS_DETALHE:
            tipo = ""
            ticker = ticker if ticker in ATIVOS_POR_TICKER else ""

        ipca_12m = None
        ipca_erro = None
        try:
            ipca_12m = scrape_ipca()["ipca_12m"]
        except Exception as exc:
            ipca_erro = str(exc)

        return render_template(
            "calculadora.html",
            periodos=PERIODOS_MESES,
            preselect_ticker=ticker,
            preselect_tipo=tipo,
            ipca_12m=ipca_12m,
            ipca_erro=ipca_erro,
            taxa_real_default=TAXA_REAL_DEFAULT,
        )

    @app.route("/api/calculadora", methods=["POST"])
    @login_required
    def api_calculadora():
        data = request.get_json(silent=True) or {}
        try:
            tipo = (data.get("tipo") or "").strip().lower()
            ticker = limpar_ticker(data.get("ticker", ""))
            if tipo not in TIPOS_DETALHE:
                item = ATIVOS_POR_TICKER.get(ticker)
                if not item:
                    return jsonify(
                        {"erro": "Ativo nao esta na lista fixa. Escolha um da busca."}
                    ), 400
                tipo = item["tipo"]

            taxa_real = data.get("taxa_real_aa", None)
            if taxa_real is None and data.get("ipca_mais_aa") is not None:
                resultado = build_simulacao(
                    tipo=tipo,
                    ticker=ticker,
                    aporte_inicial=float(data.get("aporte_inicial") or 0),
                    aporte_mensal=float(data.get("aporte_mensal") or 0),
                    meses=int(data.get("meses") or 12),
                    reinvestir=bool(data.get("reinvestir", True)),
                    ipca_mais_aa=float(data.get("ipca_mais_aa")),
                )
            else:
                resultado = build_simulacao(
                    tipo=tipo,
                    ticker=ticker,
                    aporte_inicial=float(data.get("aporte_inicial") or 0),
                    aporte_mensal=float(data.get("aporte_mensal") or 0),
                    meses=int(data.get("meses") or 12),
                    reinvestir=bool(data.get("reinvestir", True)),
                    taxa_real_aa=float(
                        taxa_real if taxa_real is not None else TAXA_REAL_DEFAULT
                    ),
                )
            return jsonify(resultado)
        except ValueError as exc:
            return jsonify({"erro": str(exc)}), 400
        except requests.RequestException as exc:
            return jsonify({"erro": f"Falha ao consultar o site: {exc}"}), 502
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 500
