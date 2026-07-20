# ###################################################################
#        🎯 Projeto: API Investidor10 Scraper (Dia 20)              #
# ###################################################################
# 📁 Caminho: dia-20/dia20_api_investidor10.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: flask, requests, beautifulsoup4
# 🔗 Instalação: pip install flask requests beautifulsoup4
# 🔑 Autenticação: ?key=SUA_CHAVE em todas as rotas /api/*
# 🌐 Dados em tempo real: scrape ao vivo a cada consulta
# ###################################################################

from datetime import datetime

import requests
from flask import Flask, jsonify, render_template, request

from config import API_KEY
from scraper.detalhe_acao import scrape_acao_detail
from scraper.detalhe_fii import scrape_fii_detail
from scraper.rankings import scrape_ranking

app = Flask(__name__)


# Valida a chave enviada na URL (?key=). Retorna erro 401 se estiver errada.
def check_api_key():
    key = request.args.get("key", "").strip()
    if key != API_KEY:
        return jsonify(
            {
                "erro": "API key invalida ou ausente.",
                "dica": "Configure a chave em config.py e use ?key=SUA_CHAVE na URL.",
            }
        ), 401
    return None


# Metadados comuns em todas as respostas de ranking
def meta_response():
    return {
        "consultado_em": datetime.now().isoformat(timespec="seconds"),
        "fonte": "investidor10.com.br",
        "aviso": "Dados coletados em tempo real a cada consulta.",
    }


# Pagina inicial com links para testar os endpoints
@app.route("/")
def index():
    return render_template("index.html", api_key=API_KEY)


# Ranking completo de FIIs (varias paginas — pode demorar)
@app.route("/api/fiis")
def api_fiis():
    denied = check_api_key()
    if denied:
        return denied

    try:
        fiis = scrape_ranking("fiis")
        return jsonify({**meta_response(), "total": len(fiis), "fiis": fiis})
    except requests.RequestException as exc:
        return jsonify({"erro": f"Falha ao acessar o site: {exc}"}), 502


# Ranking completo de Acoes (varias paginas — pode demorar)
@app.route("/api/acoes")
def api_acoes():
    denied = check_api_key()
    if denied:
        return denied

    try:
        acoes = scrape_ranking("acoes")
        return jsonify({**meta_response(), "total": len(acoes), "acoes": acoes})
    except requests.RequestException as exc:
        return jsonify({"erro": f"Falha ao acessar o site: {exc}"}), 502


# FIIs + Acoes em uma unica resposta
@app.route("/api/rankings")
def api_rankings():
    denied = check_api_key()
    if denied:
        return denied

    try:
        fiis = scrape_ranking("fiis")
        acoes = scrape_ranking("acoes")
        return jsonify(
            {
                **meta_response(),
                "total_fiis": len(fiis),
                "total_acoes": len(acoes),
                "fiis": fiis,
                "acoes": acoes,
            }
        )
    except requests.RequestException as exc:
        return jsonify({"erro": f"Falha ao acessar o site: {exc}"}), 502


# Detalhe de um FII (ex: /api/fii/CACR11) — uma pagina, resposta rapida
@app.route("/api/fii/<ticker>")
def api_fii_detail(ticker):
    denied = check_api_key()
    if denied:
        return denied

    try:
        return jsonify(scrape_fii_detail(ticker))
    except requests.RequestException as exc:
        return jsonify({"erro": f"Falha ao acessar o site: {exc}"}), 502


# Detalhe de uma Acao (ex: /api/acao/SCAR3) — uma pagina, resposta rapida
@app.route("/api/acao/<ticker>")
def api_acao_detail(ticker):
    denied = check_api_key()
    if denied:
        return denied

    try:
        return jsonify(scrape_acao_detail(ticker))
    except requests.RequestException as exc:
        return jsonify({"erro": f"Falha ao acessar o site: {exc}"}), 502


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  API Investidor10 - Dia 20")
    print("  Acesse: http://localhost:5000/")
    print("  API key: altere em config.py")
    print("  Ctrl+C para encerrar")
    print("=" * 50 + "\n")
    app.run(debug=True)
