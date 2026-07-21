# Configuracoes Dia 29 — Radar + base do Dia 28
# Em producao (Dia 30): defina SECRET_KEY e opcionalmente RADAR_CRON=0/1
#
# TIMEZONE: America/Sao_Paulo (UTC-3). O servidor de deploy fica em -3;
# o app NAO usa o fuso do sistema operacional — sempre este.

import os

SECRET_KEY = os.environ.get("SECRET_KEY", "altere-esta-chave-em-producao-dia29")

# Fuso fixo Brasil (UTC-3) — cron, status do radar, ano do footer
TIMEZONE = os.environ.get("TIMEZONE", "America/Sao_Paulo")

DATABASE_PATH = "database/app.db"

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024

PAGE_DELAY_SECONDS = 1
RANKING_TOTAL_PAGES = 4
TOP_N_POR_TIPO = 5

# Cron Radar: 1 = ligado (padrao), 0 = desliga
RADAR_CRON = os.environ.get("RADAR_CRON", "1") == "1"

from ativos_lista import ACOES, ATIVOS, FIIS  # noqa: E402,F401
