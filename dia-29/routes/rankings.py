# Rotas: rankings + APIs top10

import requests
from flask import flash, jsonify, redirect, render_template, url_for

from services.top_dividendos import build_ranking_completo, build_top10
from web.helpers import login_required


def register(app):
    @app.route("/api/top10")
    @login_required
    def api_top10():
        try:
            return jsonify(build_top10())
        except requests.RequestException as exc:
            return jsonify({"erro": f"Falha ao consultar o site: {exc}"}), 502
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 500

    @app.route("/api/rankings/<tipo>")
    @login_required
    def api_rankings(tipo):
        if tipo not in ("fiis", "acoes"):
            return jsonify({"erro": "Tipo invalido. Use fiis ou acoes."}), 400
        try:
            return jsonify(build_ranking_completo(tipo))
        except requests.RequestException as exc:
            return jsonify({"erro": f"Falha ao consultar o site: {exc}"}), 502
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 500

    @app.route("/rankings/<tipo>")
    @login_required
    def rankings(tipo):
        if tipo not in ("fiis", "acoes"):
            flash("Ranking invalido.", "warning")
            return redirect(url_for("painel"))
        titulo = "FIIs" if tipo == "fiis" else "Ações"
        return render_template("rankings.html", tipo=tipo, titulo=titulo)
