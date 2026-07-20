# Configuracoes Dia 24 — login + rankings + detalhe de ativo (scraper)

# Chave secreta do Flask — altere em producao
SECRET_KEY = "altere-esta-chave-em-producao-dia24"

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
