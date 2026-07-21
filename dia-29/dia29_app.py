# ###################################################################
#   🎯 Projeto: InvestidorWeb - Radar (Dia 29)                        #
# ###################################################################
# 📁 Caminho: dia-29/dia29_app.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# Continua o Dia 28 e adiciona:
#
# - Radar: periodo + compra/venda + zonas + historico 15m/1d + grafico
# - Cron APScheduler: seg–sex 10h–18h America/Sao_Paulo (UTC-3)
# - Pronto para deploy (Dia 30): host 0.0.0.0 + PORT / DEBUG / SECRET_KEY
# ###################################################################
# 📚 Bibliotecas: flask, requests, beautifulsoup4, yfinance, APScheduler
# 🔗 Instalação: pip install -r requirements.txt
# 🌐 Frontend: Bootstrap 5, Icons, Chart.js
# 💾 Banco: database/app.db
# 🕐 Fuso: America/Sao_Paulo (UTC-3) — config TIMEZONE / web/timezone_util.py
# ###################################################################
# REFATORACAO (modulos):
#   web/__init__.py          → create_app()
#   web/helpers.py           → login, upload, mapa de ativos
#   web/timezone_util.py     → agora/hoje em UTC-3
#   routes/__init__.py       → register_all()
#   routes/auth.py           → login / cadastro / logout
#   routes/painel.py         → painel
#   routes/rankings.py       → rankings + APIs top10
#   routes/ativos.py         → busca / detalhe
#   routes/calculadora.py    → calculadora
#   routes/radar.py          → Radar CRUD + APIs
#   routes/carteiras.py      → carteiras / lancamentos
#   routes/perfil.py         → perfil / uploads
#   db_radar.py | services/radar_*.py | templates radar_*
# ###################################################################

import os

from db import init_db
from config import ATIVOS, RADAR_CRON
from web import create_app
from web.helpers import ensure_upload_dir

app = create_app()


if __name__ == "__main__":
    init_db()
    ensure_upload_dir()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "0") == "1"

    iniciar_cron = RADAR_CRON and os.environ.get("WERKZEUG_RUN_MAIN") != "false"
    if debug:
        iniciar_cron = RADAR_CRON and os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    if iniciar_cron:
        from services.radar_cron import iniciar_scheduler

        iniciar_scheduler()
        cron_msg = "Cron Radar: ON (seg-sex 10h-18h SP UTC-3 / 15 min)"
    else:
        cron_msg = "Cron Radar: OFF" if not RADAR_CRON else "Cron Radar: aguardando worker"

    print("\n" + "=" * 50)
    print("  InvestidorWeb - Dia 29 (Radar)")
    print(f"  Acesse: http://0.0.0.0:{port}/")
    print(f"  Busca: lista fixa com {len(ATIVOS)} ativos")
    print("  Fuso: America/Sao_Paulo (UTC-3)")
    print(f"  {cron_msg}")
    print("  Ctrl+C para encerrar")
    print("=" * 50 + "\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
