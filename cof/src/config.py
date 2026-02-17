import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# --- Credenciais ---
EMAIL = os.environ["COF_EMAIL"]
PASSWORD = os.environ["COF_PASSWORD"]

# --- URLs ---
BASE_URL = "https://app.seminariodefilosofia.org"
LOGIN_URL = f"{BASE_URL}/login"
API_BASE = "https://api.seminariodefilosofia.org/v1"

# Cursos a monitorar (id, nome)
COURSES = [
    (1, "COF Original"),
    (30, "COF Remasterizado"),
]

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
AULAS_DIR = DATA_DIR / "aulas"
EXTRA_DIR = DATA_DIR / "extracurriculares"
STATE_FILE = DATA_DIR / "state.json"
COOKIE_FILE = DATA_DIR / "cookies.json"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "agent.log"

# --- Limites ---
BATCH_SIZE = (10, 15)
THROTTLE_SECONDS = 10
EXECUTION_WINDOWS = [("02:00", "04:00"), ("10:00", "12:00")]

# --- Logging ---
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3


def setup_logging() -> logging.Logger:
    """Configura logging rotativo para o projeto."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("cof")
    logger.setLevel(logging.DEBUG)

    # Handler para arquivo (rotativo)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
