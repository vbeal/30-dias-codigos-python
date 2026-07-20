# Configuracoes Dia 28 — proventos, cache, painel com carteira, atalho lancamento

SECRET_KEY = "altere-esta-chave-em-producao-dia28"

DATABASE_PATH = "database/app.db"

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024

PAGE_DELAY_SECONDS = 1
RANKING_TOTAL_PAGES = 4
TOP_N_POR_TIPO = 5

from ativos_lista import ACOES, ATIVOS, FIIS  # noqa: E402,F401
