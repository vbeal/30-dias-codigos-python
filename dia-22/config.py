# Configuracoes do sistema de login (Dia 22 — continua o Dia 21)

# Chave secreta do Flask — altere em producao (usada nas sessoes de login)
SECRET_KEY = "altere-esta-chave-em-producao-dia22"

# Caminho do banco SQLite (arquivo criado automaticamente na primeira execucao)
DATABASE_PATH = "database/app.db"

# --- Novidade Dia 22: pasta e regras para foto de perfil ---
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
# Limite de tamanho do upload (2 MB)
MAX_CONTENT_LENGTH = 2 * 1024 * 1024
