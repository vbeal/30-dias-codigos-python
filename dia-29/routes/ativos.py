# Rotas: busca e detalhe de ativo

import requests
from flask import flash, jsonify, redirect, render_template, request, url_for

from services.detalhe_ativo import TIPOS_DETALHE, build_detalhe, limpar_ticker
from web.helpers import ATIVOS_POR_TICKER, login_required


def register(app):
    @app.route("/buscar")
    @login_required
    def buscar_ativo():
        ticker = limpar_ticker(request.args.get("ticker", ""))
        tipo = request.args.get("tipo", "").strip().lower()
        if not ticker:
            flash("Informe o ticker para buscar.", "warning")
            return redirect(url_for("painel"))

        if tipo not in TIPOS_DETALHE:
            item = ATIVOS_POR_TICKER.get(ticker)
            if item:
                tipo = item["tipo"]
            else:
                flash("Ativo nao encontrado na lista. Escolha um item da busca.", "warning")
                return redirect(url_for("painel"))

        return redirect(url_for("ativo_detalhe", tipo=tipo, ticker=ticker))

    @app.route("/ativo/<tipo>/<ticker>")
    @login_required
    def ativo_detalhe(tipo, ticker):
        tipo = tipo.strip().lower()
        ticker = limpar_ticker(ticker)
        if tipo not in TIPOS_DETALHE or not ticker:
            flash("Ativo invalido.", "warning")
            return redirect(url_for("painel"))
        titulo = "FII" if tipo == "fii" else "Ação"
        return render_template(
            "ativo.html",
            tipo=tipo,
            ticker=ticker,
            titulo=titulo,
        )

    @app.route("/api/ativo/<tipo>/<ticker>")
    @login_required
    def api_ativo(tipo, ticker):
        try:
            return jsonify(build_detalhe(tipo, ticker))
        except ValueError as exc:
            return jsonify({"erro": str(exc)}), 400
        except requests.RequestException as exc:
            return jsonify({"erro": f"Falha ao consultar o site: {exc}"}), 502
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 500
