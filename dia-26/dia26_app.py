# ###################################################################
#   🎯 Projeto: InvestidorWeb - Carteira (Dia 26)                     #
# ###################################################################
# 📁 Caminho: dia-26/dia26_app.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# Continua o Dia 25 (busca + calculadora) e adiciona a CARTEIRA.
#
# Carteira (CRUD = Create, Read, Update, Delete):
# - Varias carteiras por usuario; UMA marcada como PADRAO
# - /carteiras abre a padrao (ou tela para criar a 1a)
# - Lancamentos compra/venda: data, qtd, preco (mascara R$), custos
# - Ativo da lista fixa (sem escolher FII/Acao — tipo vem da lista)
# - Preco na data via Yahoo (/api/preco-ativo + services/preco_yahoo.py)
# - Ainda SEM grafico de patrimonio / proventos / % ideal (proxima etapa)
#
# UX padrao do site (base.html):
# - Titulo: InvestidorWeb - {pagina}
# - Toasts 5s | loading global | modal confirmar (sem alert/confirm JS)
#
# Herdado do Dia 25:
# - Lista fixa + busca navbar + calculadora + rankings + detalhe
# ###################################################################
# 📚 Bibliotecas: flask, requests, beautifulsoup4, yfinance, sqlite3,
#    werkzeug
# 🔗 Instalação: pip install flask requests beautifulsoup4 yfinance
# 🌐 Frontend (CDN): Bootstrap 5, Bootstrap Icons, Chart.js
# 💾 Banco: database/app.db | Fotos: static/uploads/
# ###################################################################
# Arquivos NOVOS / ALTERADOS neste dia (principais):
#
# NOVOS:
# - dia-26/db_carteira.py
# - dia-26/services/preco_yahoo.py
# - dia-26/templates/carteiras.html
# - dia-26/templates/carteira_detalhe.html
#
# ALTERADOS:
# - dia-26/dia26_app.py          (este arquivo — rotas carteira + API preco)
# - dia-26/db.py                 (init chama tabelas da carteira)
# - dia-26/config.py
# - dia-26/templates/base.html   (titulo, loading, toast 5s, modal confirm)
# - dia-26/templates/painel.html (atalho Carteiras)
# - dia-26/static/css/app.css    (overlay loading)
# - README.md                    (secao Dia 26)
# ###################################################################

import json
from datetime import datetime
from functools import wraps
from pathlib import Path

import requests
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from config import (
    ALLOWED_EXTENSIONS,
    ATIVOS,
    MAX_CONTENT_LENGTH,
    SECRET_KEY,
    UPLOAD_FOLDER,
)
from db import (
    clear_foto,
    create_user,
    get_user_by_id,
    init_db,
    update_foto,
    update_password,
    update_profile,
    verify_user,
)
from db_carteira import (
    adicionar_lancamento,
    apagar_carteira,
    apagar_lancamento,
    criar_carteira,
    definir_carteira_padrao,
    get_carteira,
    get_carteira_padrao,
    listar_carteiras,
    listar_lancamentos,
    renomear_carteira,
)
from services.calculadora_dividendos import PERIODOS_MESES, TAXA_REAL_DEFAULT, build_simulacao
from services.detalhe_ativo import TIPOS_DETALHE, build_detalhe, limpar_ticker
from services.preco_yahoo import preco_no_dia
from services.top_dividendos import build_ranking_completo, build_top10
from scraper.ipca import scrape_ipca

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / UPLOAD_FOLDER

# Mapa ticker -> tipo para a busca (lista fixa)
ATIVOS_POR_TICKER = {a["ticker"].upper(): a for a in ATIVOS}


# Ano dinamico + lista de ativos (busca navbar) em todos os templates
@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "ativos_json": json.dumps(ATIVOS, ensure_ascii=False),
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Faca login para acessar esta pagina.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def redirect_if_logged_in():
    if "user_id" in session:
        return redirect(url_for("painel"))
    return None


def refresh_session(user):
    session["user_id"] = user["id"]
    session["user_nome"] = user["nome"]
    session["user_email"] = user["email"]
    session["user_foto"] = user["foto"] if user["foto"] else None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_foto_file(filename):
    if not filename:
        return
    path = UPLOAD_DIR / filename
    if path.is_file():
        path.unlink()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("painel"))
    return redirect(url_for("login"))


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    redirect_response = redirect_if_logged_in()
    if redirect_response:
        return redirect_response

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar", "")

        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "danger")
        elif len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
        elif senha != confirmar:
            flash("As senhas nao conferem.", "danger")
        else:
            ok, message = create_user(nome, email, senha)
            flash(message, "success" if ok else "danger")
            if ok:
                return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    redirect_response = redirect_if_logged_in()
    if redirect_response:
        return redirect_response

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        if not email or not senha:
            flash("Preencha e-mail e senha.", "danger")
        else:
            ok, user, message = verify_user(email, senha)
            if ok:
                refresh_session(user)
                flash(message, "success")
                return redirect(url_for("painel"))
            flash(message, "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Voce saiu da sua conta.", "info")
    return redirect(url_for("login"))


# Painel: UI rapida; dados do Top 10 vem via AJAX (/api/top10)
@app.route("/painel")
@login_required
def painel():
    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        flash("Usuario nao encontrado.", "danger")
        return redirect(url_for("login"))
    refresh_session(user)
    return render_template("painel.html", user=user)


# --- Novidade Dia 23: APIs JSON para o frontend (scrape ao vivo) ---
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


# Paginas "Ver todos" — loading no front + fetch do ranking completo
@app.route("/rankings/<tipo>")
@login_required
def rankings(tipo):
    if tipo not in ("fiis", "acoes"):
        flash("Ranking invalido.", "warning")
        return redirect(url_for("painel"))
    titulo = "FIIs" if tipo == "fiis" else "Ações"
    return render_template("rankings.html", tipo=tipo, titulo=titulo)


# --- Busca e detalhe (Dia 24) + resolve tipo pela lista fixa (Dia 25) ---
@app.route("/buscar")
@login_required
def buscar_ativo():
    ticker = limpar_ticker(request.args.get("ticker", ""))
    tipo = request.args.get("tipo", "").strip().lower()
    if not ticker:
        flash("Informe o ticker para buscar.", "warning")
        return redirect(url_for("painel"))

    # Se tipo nao veio, tenta descobrir pela lista fixa
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


# --- Novidade Dia 25: calculadora de dividendos (Brapi light) ---
@app.route("/calculadora")
@login_required
def calculadora():
    # Pode abrir ja com ativo: /calculadora?ticker=MXRF11&tipo=fii
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
        # Se tipo nao veio, resolve pela lista fixa
        if tipo not in TIPOS_DETALHE:
            item = ATIVOS_POR_TICKER.get(ticker)
            if not item:
                return jsonify({"erro": "Ativo nao esta na lista fixa. Escolha um da busca."}), 400
            tipo = item["tipo"]

        taxa_real = data.get("taxa_real_aa", None)
        if taxa_real is None and data.get("ipca_mais_aa") is not None:
            # legado: campo unico
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
                taxa_real_aa=float(taxa_real if taxa_real is not None else TAXA_REAL_DEFAULT),
            )
        return jsonify(resultado)
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 400
    except requests.RequestException as exc:
        return jsonify({"erro": f"Falha ao consultar o site: {exc}"}), 502
    except Exception as exc:
        return jsonify({"erro": str(exc)}), 500


# --- Novidade Dia 26: carteiras + lancamentos (CRUD) ---
@app.route("/carteiras")
@login_required
def carteiras():
    # Abre direto a carteira padrao; se nao houver, tela de criar a primeira
    padrao = get_carteira_padrao(session["user_id"])
    if padrao:
        return redirect(url_for("carteira_detalhe", carteira_id=padrao["id"]))
    return render_template("carteiras.html", carteiras=[])


@app.route("/carteiras/criar", methods=["POST"])
@login_required
def carteiras_criar():
    ok, carteira_id, msg = criar_carteira(session["user_id"], request.form.get("nome", ""))
    flash(msg, "success" if ok else "danger")
    if ok and carteira_id:
        return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))
    return redirect(url_for("carteiras"))


@app.route("/carteiras/<int:carteira_id>")
@login_required
def carteira_detalhe(carteira_id):
    uid = session["user_id"]
    carteira = get_carteira(carteira_id, uid)
    if not carteira:
        flash("Carteira nao encontrada.", "danger")
        return redirect(url_for("carteiras"))
    return render_template(
        "carteira_detalhe.html",
        carteira=carteira,
        carteiras=listar_carteiras(uid),
        lancamentos=listar_lancamentos(carteira_id),
    )


@app.route("/carteiras/<int:carteira_id>/padrao", methods=["POST"])
@login_required
def carteira_definir_padrao(carteira_id):
    ok, msg = definir_carteira_padrao(carteira_id, session["user_id"])
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))


@app.route("/carteiras/<int:carteira_id>/renomear", methods=["POST"])
@login_required
def carteira_renomear(carteira_id):
    ok, msg = renomear_carteira(carteira_id, session["user_id"], request.form.get("nome", ""))
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))


@app.route("/carteiras/<int:carteira_id>/apagar", methods=["POST"])
@login_required
def carteira_apagar(carteira_id):
    ok, msg = apagar_carteira(carteira_id, session["user_id"])
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("carteiras"))


@app.route("/carteiras/<int:carteira_id>/lancamentos", methods=["POST"])
@login_required
def lancamento_criar(carteira_id):
    ticker = limpar_ticker(request.form.get("ticker", ""))
    item = ATIVOS_POR_TICKER.get(ticker)
    if not item:
        flash("Ativo nao esta na lista fixa.", "danger")
        return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))

    # Tipo vem da lista (nao do formulario)
    tipo = item["tipo"]

    ok, msg = adicionar_lancamento(
        carteira_id=carteira_id,
        usuario_id=session["user_id"],
        operacao=request.form.get("operacao"),
        ticker=ticker,
        tipo_ativo=tipo,
        data_transacao=request.form.get("data_transacao"),
        quantidade=request.form.get("quantidade"),
        preco=request.form.get("preco"),
        outros_custos=request.form.get("outros_custos") or 0,
    )
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))


@app.route("/carteiras/<int:carteira_id>/lancamentos/<int:lancamento_id>/apagar", methods=["POST"])
@login_required
def lancamento_apagar(carteira_id, lancamento_id):
    ok, msg = apagar_lancamento(lancamento_id, carteira_id, session["user_id"])
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))


@app.route("/api/preco-ativo")
@login_required
def api_preco_ativo():
    """Cotacao de fechamento (Yahoo) na data — usada no modal de lancamento."""
    ticker = limpar_ticker(request.args.get("ticker", ""))
    data = (request.args.get("data") or "").strip()
    if ticker not in ATIVOS_POR_TICKER:
        return jsonify({"erro": "Ativo nao esta na lista fixa."}), 400
    try:
        return jsonify(preco_no_dia(ticker, data))
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 400
    except Exception as exc:
        return jsonify({"erro": f"Falha ao consultar Yahoo: {exc}"}), 502


ABAS_PERFIL = {"dados", "senha", "foto"}


def aba_perfil(valor=None):
    aba = valor or request.form.get("aba") or request.args.get("aba") or "dados"
    return aba if aba in ABAS_PERFIL else "dados"


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        flash("Usuario nao encontrado.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        acao = request.form.get("acao", "")
        aba = aba_perfil()

        if acao == "dados":
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()
            if not nome or not email:
                flash("Preencha nome e e-mail.", "danger")
            else:
                ok, message = update_profile(user["id"], nome, email)
                flash(message, "success" if ok else "danger")
                if ok:
                    user = get_user_by_id(user["id"])
                    refresh_session(user)

        elif acao == "senha":
            senha_atual = request.form.get("senha_atual", "")
            senha_nova = request.form.get("senha_nova", "")
            confirmar = request.form.get("confirmar", "")
            if not senha_atual or not senha_nova or not confirmar:
                flash("Preencha todos os campos de senha.", "danger")
            elif senha_nova != confirmar:
                flash("A nova senha e a confirmacao nao conferem.", "danger")
            else:
                ok, message = update_password(user["id"], senha_atual, senha_nova)
                flash(message, "success" if ok else "danger")

        elif acao == "foto":
            arquivo = request.files.get("foto")
            if not arquivo or arquivo.filename == "":
                flash("Selecione uma imagem para enviar.", "danger")
            elif not allowed_file(arquivo.filename):
                flash("Formato invalido. Use: png, jpg, jpeg, gif ou webp.", "danger")
            else:
                UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
                ext = arquivo.filename.rsplit(".", 1)[1].lower()
                filename = secure_filename(f"user_{user['id']}.{ext}")
                delete_foto_file(user["foto"])
                arquivo.save(UPLOAD_DIR / filename)
                ok, message = update_foto(user["id"], filename)
                flash(message, "success" if ok else "danger")
                user = get_user_by_id(user["id"])
                refresh_session(user)

        elif acao == "remover_foto":
            if not user["foto"]:
                flash("Nao ha foto para remover.", "warning")
            else:
                delete_foto_file(user["foto"])
                ok, message = clear_foto(user["id"])
                flash(message, "success" if ok else "danger")
                user = get_user_by_id(user["id"])
                refresh_session(user)

        return redirect(url_for("perfil", aba=aba))

    return render_template("perfil.html", user=user, aba=aba_perfil())


@app.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == "__main__":
    init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print("\n" + "=" * 50)
    print("  Investidor Web - Dia 26")
    print("  Acesse: http://localhost:5000/")
    print(f"  Busca: lista fixa com {len(ATIVOS)} ativos")
    print("  Calculadora: /calculadora")
    print("  Carteiras: /carteiras")
    print("  (somente usuarios logados)")
    print("  Ctrl+C para encerrar")
    print("=" * 50 + "\n")
    app.run(debug=True)
