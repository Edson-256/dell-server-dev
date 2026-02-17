from pathlib import Path

from src.config import DATA_DIR


def _sanitize(name: str) -> str:
    """Remove caracteres inválidos para nomes de arquivo."""
    return "".join(c if c.isalnum() or c in "-_ " else "_" for c in name).strip("_ ")


def generate_filename(item) -> Path:
    """Gera path completo com nome padronizado.

    Organização:
      data/<curso>/<categoria>/Aula_001_-_Titulo.pdf
    """
    category_dirs = {
        "transcription": "transcricoes",
        "audios": "audios",
        "videos": "videos",
        "books": "livros",
    }

    course_dir = _sanitize(item.course_name or "Outros")
    subdir = category_dirs.get(item.item_type, "outros")
    dest_dir = DATA_DIR / course_dir / subdir

    title = _sanitize(item.title)

    if item.lesson_number:
        name = f"Aula_{item.lesson_number:03d}_-_{title}.{item.extension}"
    else:
        name = f"{title}.{item.extension}"

    return dest_dir / name
