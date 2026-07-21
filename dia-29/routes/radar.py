# Rotas: Radar (CRUD + APIs de acompanhamento)

import json

from flask import flash, jsonify, redirect, render_template, request, session, url_for

from config import ATIVOS
from db_radar import (
    apagar_radar,
    atualizar_radar,
    criar_radar,
    get_radar,
    listar_ativos_radar,
    listar_radares,
)
from services.detalhe_ativo import limpar_ticker
from services.radar_acompanhamento import (
    logs_paginados,
    meta_acompanhamento,
    serie_grafico,
    sincronizar_radar,
)
from services.radar_form import (
    extrair_radar_do_form,
    format_preco_br,
    status_periodo,
)
from web.helpers import ATIVOS_POR_TICKER, login_required


def register(app):
    @app.route("/radar")
    @login_required
    def radares():
        uid = session["user_id"]
        return render_template(
            "radares.html",
            radares=listar_radares(uid),
            status_fn=status_periodo,
        )

    @app.route("/radar/novo", methods=["GET", "POST"])
    @login_required
    def radar_novo():
        if request.method == "POST":
            ok, erro, payload = extrair_radar_do_form(request.form, ATIVOS_POR_TICKER)
            if not ok:
                flash(erro, "danger")
                return redirect(url_for("radar_novo"))
            ok, radar_id, msg = criar_radar(
                session["user_id"],
                payload["nome"],
                payload["data_inicio"],
                payload["data_fim"],
                payload["ativos"],
            )
            flash(msg, "success" if ok else "danger")
            if ok and radar_id:
                return redirect(url_for("radar_detalhe", radar_id=radar_id))
            return redirect(url_for("radar_novo"))

        return render_template(
            "radar_form.html",
            radar=None,
            ativos_json="[]",
            ativos_lista=ATIVOS,
        )

    @app.route("/radar/<int:radar_id>")
    @login_required
    def radar_detalhe(radar_id):
        uid = session["user_id"]
        radar = get_radar(radar_id, uid)
        if not radar:
            flash("Radar nao encontrado.", "danger")
            return redirect(url_for("radares"))
        ativos = listar_ativos_radar(radar_id)
        forcar = request.args.get("forcar", "").lower() in ("1", "true", "sim", "yes")
        sync = sincronizar_radar(radar, ativos=ativos, forcar=forcar)
        if forcar:
            flash(
                sync.get("msg", "Sincronizado."),
                "success" if sync.get("ok") else "warning",
            )
        return render_template(
            "radar_detalhe.html",
            radar=radar,
            ativos=ativos,
            status=status_periodo(radar["data_inicio"], radar["data_fim"]),
            fmt=format_preco_br,
            meta=meta_acompanhamento(radar, ativos),
            sync=sync,
        )

    @app.route("/api/radar/<int:radar_id>/meta")
    @login_required
    def api_radar_meta(radar_id):
        radar = get_radar(radar_id, session["user_id"])
        if not radar:
            return jsonify({"erro": "Radar nao encontrado."}), 404
        ativos = listar_ativos_radar(radar_id)
        return jsonify(meta_acompanhamento(radar, ativos))

    @app.route("/api/radar/<int:radar_id>/serie")
    @login_required
    def api_radar_serie(radar_id):
        radar = get_radar(radar_id, session["user_id"])
        if not radar:
            return jsonify({"erro": "Radar nao encontrado."}), 404
        ticker = limpar_ticker(request.args.get("ticker", ""))
        semana_inicio = (request.args.get("inicio") or radar["data_inicio"]).strip()[:10]
        semana_fim = (request.args.get("fim") or radar["data_fim"]).strip()[:10]
        if not ticker:
            return jsonify({"erro": "Informe o ticker."}), 400
        try:
            return jsonify(serie_grafico(radar, ticker, semana_inicio, semana_fim))
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 500

    @app.route("/api/radar/<int:radar_id>/logs")
    @login_required
    def api_radar_logs(radar_id):
        radar = get_radar(radar_id, session["user_id"])
        if not radar:
            return jsonify({"erro": "Radar nao encontrado."}), 404
        page = request.args.get("page", 1)
        ticker = limpar_ticker(request.args.get("ticker", "")) or None
        try:
            return jsonify(
                logs_paginados(radar_id, page=page, per_page=50, ticker=ticker)
            )
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 500

    @app.route("/radar/<int:radar_id>/sincronizar", methods=["POST"])
    @login_required
    def radar_sincronizar(radar_id):
        radar = get_radar(radar_id, session["user_id"])
        if not radar:
            flash("Radar nao encontrado.", "danger")
            return redirect(url_for("radares"))
        sync = sincronizar_radar(radar, forcar=True)
        flash(sync.get("msg", "Sincronizado."), "success" if sync.get("ok") else "warning")
        return redirect(url_for("radar_detalhe", radar_id=radar_id))

    @app.route("/radar/<int:radar_id>/editar", methods=["GET", "POST"])
    @login_required
    def radar_editar(radar_id):
        uid = session["user_id"]
        radar = get_radar(radar_id, uid)
        if not radar:
            flash("Radar nao encontrado.", "danger")
            return redirect(url_for("radares"))

        if request.method == "POST":
            ok, erro, payload = extrair_radar_do_form(request.form, ATIVOS_POR_TICKER)
            if not ok:
                flash(erro, "danger")
                return redirect(url_for("radar_editar", radar_id=radar_id))
            ok, msg = atualizar_radar(
                radar_id,
                uid,
                payload["nome"],
                payload["data_inicio"],
                payload["data_fim"],
                payload["ativos"],
            )
            flash(msg, "success" if ok else "danger")
            if ok:
                return redirect(url_for("radar_detalhe", radar_id=radar_id))
            return redirect(url_for("radar_editar", radar_id=radar_id))

        ativos = listar_ativos_radar(radar_id)
        ativos_js = [
            {
                "ticker": a["ticker"],
                "direcao": a["direcao"],
                "preco_entrada": format_preco_br(a["preco_entrada"]),
                "preco_teto": format_preco_br(a["preco_teto"]),
                "preco_alvo": format_preco_br(a["preco_alvo"]),
                "preco_stop": format_preco_br(a["preco_stop"]),
                "preco_corte": format_preco_br(a["preco_corte"]),
            }
            for a in ativos
        ]
        return render_template(
            "radar_form.html",
            radar=radar,
            ativos_json=json.dumps(ativos_js, ensure_ascii=False),
            ativos_lista=ATIVOS,
        )

    @app.route("/radar/<int:radar_id>/apagar", methods=["POST"])
    @login_required
    def radar_apagar(radar_id):
        ok, msg = apagar_radar(radar_id, session["user_id"])
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("radares"))
