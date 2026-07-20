# Configuracoes Dia 25 — login + rankings + detalhe + busca com lista fixa

# Chave secreta do Flask — altere em producao
SECRET_KEY = "altere-esta-chave-em-producao-dia25"

# Banco SQLite (usuarios / perfil — rankings e detalhes NAO sao salvos)
DATABASE_PATH = "database/app.db"

# Upload de foto (Dia 22)
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024

# Scraper de rankings (Dia 23)
PAGE_DELAY_SECONDS = 1
RANKING_TOTAL_PAGES = 4
TOP_N_POR_TIPO = 5

# --- Novidade Dia 25: lista FIXA de ativos (Investidor10, 4 pags cada) ---
# Gerada em ativos_lista.py — nao scrapa na busca em runtime
from ativos_lista import ACOES, ATIVOS, FIIS  # noqa: E402,F401
