# Rotas: carteiras + lancamentos + API preco

from flask import flash, jsonify, redirect, render_template, request, session, url_for

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
from services.carteira_resumo import montar_acompanhamento
from services.detalhe_ativo import limpar_ticker
from services.preco_yahoo import preco_no_dia
from web.helpers import ATIVOS_POR_TICKER, login_required


def register(app):
    @app.route("/carteiras")
    @login_required
    def carteiras():
        padrao = get_carteira_padrao(session["user_id"])
        if padrao:
            return redirect(url_for("carteira_detalhe", carteira_id=padrao["id"]))
        return render_template("carteiras.html", carteiras=[])

    @app.route("/carteiras/criar", methods=["POST"])
    @login_required
    def carteiras_criar():
        ok, carteira_id, msg = criar_carteira(
            session["user_id"], request.form.get("nome", "")
        )
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
        ok, msg = renomear_carteira(
            carteira_id, session["user_id"], request.form.get("nome", "")
        )
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))

    @app.route("/carteiras/<int:carteira_id>/apagar", methods=["POST"])
    @login_required
    def carteira_apagar(carteira_id):
        ok, msg = apagar_carteira(carteira_id, session["user_id"])
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("carteiras"))

    @app.route("/api/carteiras/<int:carteira_id>/acompanhamento")
    @login_required
    def api_carteira_acompanhamento(carteira_id):
        carteira = get_carteira(carteira_id, session["user_id"])
        if not carteira:
            return jsonify({"erro": "Carteira nao encontrada."}), 404
        forcar = request.args.get("forcar", "").lower() in ("1", "true", "sim", "yes")
        try:
            dados = montar_acompanhamento(
                listar_lancamentos(carteira_id),
                meses_grafico=12,
                forcar=forcar,
            )
            dados["carteira"] = {"id": carteira["id"], "nome": carteira["nome"]}
            return jsonify(dados)
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 502

    @app.route("/carteiras/<int:carteira_id>/lancamentos", methods=["POST"])
    @login_required
    def lancamento_criar(carteira_id):
        ticker = limpar_ticker(request.form.get("ticker", ""))
        item = ATIVOS_POR_TICKER.get(ticker)
        if not item:
            flash("Ativo nao esta na lista fixa.", "danger")
            return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))

        ok, msg = adicionar_lancamento(
            carteira_id=carteira_id,
            usuario_id=session["user_id"],
            operacao=request.form.get("operacao"),
            ticker=ticker,
            tipo_ativo=item["tipo"],
            data_transacao=request.form.get("data_transacao"),
            quantidade=request.form.get("quantidade"),
            preco=request.form.get("preco"),
            outros_custos=request.form.get("outros_custos") or 0,
        )
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))

    @app.route("/carteiras/lancamento-rapido", methods=["POST"])
    @login_required
    def lancamento_rapido():
        uid = session["user_id"]
        carteiras_user = listar_carteiras(uid)
        if not carteiras_user:
            flash("Crie uma carteira antes de adicionar ativos.", "warning")
            return redirect(url_for("carteiras"))

        carteira_id = request.form.get("carteira_id", type=int)
        if not carteira_id:
            padrao = get_carteira_padrao(uid)
            carteira_id = padrao["id"] if padrao else carteiras_user[0]["id"]

        if not get_carteira(carteira_id, uid):
            flash("Carteira invalida.", "danger")
            return redirect(url_for("carteiras"))

        ticker = limpar_ticker(request.form.get("ticker", ""))
        item = ATIVOS_POR_TICKER.get(ticker)
        if not item:
            flash("Ativo nao esta na lista fixa.", "danger")
            return redirect(request.referrer or url_for("painel"))

        ok, msg = adicionar_lancamento(
            carteira_id=carteira_id,
            usuario_id=uid,
            operacao="compra",
            ticker=ticker,
            tipo_ativo=item["tipo"],
            data_transacao=request.form.get("data_transacao"),
            quantidade=request.form.get("quantidade"),
            preco=request.form.get("preco"),
            outros_custos=request.form.get("outros_custos") or 0,
        )
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))

    @app.route(
        "/carteiras/<int:carteira_id>/lancamentos/<int:lancamento_id>/apagar",
        methods=["POST"],
    )
    @login_required
    def lancamento_apagar(carteira_id, lancamento_id):
        ok, msg = apagar_lancamento(lancamento_id, carteira_id, session["user_id"])
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("carteira_detalhe", carteira_id=carteira_id))

    @app.route("/api/preco-ativo")
    @login_required
    def api_preco_ativo():
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
