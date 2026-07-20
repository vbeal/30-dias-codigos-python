# Configuracoes Dia 23 — login + rankings em tempo real (scraper)

# Chave secreta do Flask — altere em producao
SECRET_KEY = "altere-esta-chave-em-producao-dia23"

# Banco SQLite (usuarios / perfil — rankings NAO sao salvos)
DATABASE_PATH = "database/app.db"

# Upload de foto (Dia 22)
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024

# --- Novidade Dia 23: scraper de rankings ---
PAGE_DELAY_SECONDS = 1
RANKING_TOTAL_PAGES = 4
# Top misto: 5 FIIs + 5 Ações = 10 itens ordenados por DY
TOP_N_POR_TIPO = 5
