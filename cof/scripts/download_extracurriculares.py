#!/usr/bin/env python3
"""Download de cursos extracurriculares do Seminário de Filosofia."""

import asyncio
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import httpx

# --- Configuração ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TOKEN_FILE = DATA_DIR / "token.json"
EXTRA_DIR = DATA_DIR / "extracurriculares"
INVENTARIO_FILE = EXTRA_DIR / "INVENTÁRIO.md"
DOWNLOADED_STATE_FILE = EXTRA_DIR / "downloaded.json"

API_BASE = "https://api.seminariodefilosofia.org/v1"
CURSOS_REGULARES = {1, 30}  # COF Original e COF Remasterizado

CATEGORY_TO_DIR = {
    "audios": "audios",
    "books": "apostilas",
    "transcription": "transcricoes",
}


@dataclass
class Source:
    name: str
    course_id: int
    course_name: str
    category_key: str
    file_url: str | None = None
    soundcloud_url: str | None = None


@dataclass
class CourseInfo:
    id: int
    title: str
    count_lessons: int
    sources: list[Source] = field(default_factory=list)


def extract_soundcloud_url(embed_link: str) -> str | None:
    """Extrai URL real da playlist SoundCloud a partir do link de embed."""
    parsed = urlparse(embed_link)
    params = parse_qs(parsed.query)
    url_list = params.get("url", [])
    if not url_list:
        return None
    return unquote(url_list[0])


def sanitize_dirname(name: str) -> str:
    """Cria nome de diretório seguro a partir do título do curso."""
    safe = re.sub(r'[<>:"/\\|?*]', '', name)
    safe = safe.strip(". ")
    return safe or "Sem_Titulo"


async def fetch_all_pages(client: httpx.AsyncClient, url: str) -> list[dict]:
    """Busca todas as páginas de um endpoint paginado."""
    results = []
    params = {"limit": 100, "offset": 0}
    while True:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        page = data.get("results", [])
        results.extend(page)
        if not data.get("next"):
            break
        params["offset"] += 100
    return results


async def discover_courses(token: str) -> list[CourseInfo]:
    """Retorna todos os cursos extracurriculares com seus sources."""
    headers = {"Authorization": f"JWT {token}"}
    courses: list[CourseInfo] = []

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30) as client:
        raw_courses = await fetch_all_pages(client, f"{API_BASE}/user/courses/")

        for c in raw_courses:
            if c["id"] in CURSOS_REGULARES:
                continue
            info = CourseInfo(id=c["id"], title=c["title"], count_lessons=c["count_lessons"])

            raw_sources = await fetch_all_pages(client, f"{API_BASE}/courses/sources/{c['id']}")

            for s in raw_sources:
                sc_url = None
                if s.get("link") and "soundcloud.com" in s.get("link", ""):
                    sc_url = extract_soundcloud_url(s["link"])

                source = Source(
                    name=s.get("name", "Sem título"),
                    course_id=c["id"],
                    course_name=c["title"],
                    category_key=s.get("category_key", "outros"),
                    file_url=s.get("file"),
                    soundcloud_url=sc_url,
                )
                info.sources.append(source)

            courses.append(info)

    return sorted(courses, key=lambda c: c.id)


def generate_inventario(courses: list[CourseInfo], downloaded: set[str]) -> str:
    """Gera conteúdo Markdown do inventário com checklist."""
    lines = [
        "# Inventário de Cursos Extracurriculares",
        f"\nAtualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"\nTotal de cursos: {len(courses)}\n",
        "---\n",
    ]

    for course in courses:
        dir_name = sanitize_dirname(course.title)
        course_dir = EXTRA_DIR / dir_name

        direct_files = [s for s in course.sources if s.file_url]
        sc_links = [s for s in course.sources if s.soundcloud_url]
        has_anything = direct_files or sc_links

        course_done = course_dir.exists() and any(course_dir.rglob("*"))
        mark = "x" if course_done else " "

        lines.append(f"## [{mark}] {course.title} (id={course.id}) — {course.count_lessons} aulas\n")

        if not has_anything:
            lines.append("- ⚠️ Sem conteúdo disponível para download ainda\n")
        else:
            for s in sc_links:
                done = s.soundcloud_url in downloaded
                m = "x" if done else " "
                lines.append(f"- [{m}] 🎵 audios/ — {s.name} (SoundCloud playlist)\n")
                if s.soundcloud_url:
                    lines.append(f"  - URL: `{s.soundcloud_url}`\n")

            by_cat: dict[str, list[Source]] = {}
            for s in direct_files:
                by_cat.setdefault(s.category_key, []).append(s)

            for cat, sources in sorted(by_cat.items()):
                subdir = CATEGORY_TO_DIR.get(cat, cat)
                lines.append(f"- {subdir}/ ({len(sources)} arquivo(s)):\n")
                for s in sources:
                    done = (s.file_url or "") in downloaded
                    m = "x" if done else " "
                    lines.append(f"  - [{m}] {s.name}\n")

        lines.append("\n")

    return "".join(lines)


def save_inventario(content: str) -> None:
    """Salva o INVENTÁRIO.md em data/extracurriculares/."""
    EXTRA_DIR.mkdir(parents=True, exist_ok=True)
    INVENTARIO_FILE.write_text(content, encoding="utf-8")
    print(f"Inventário salvo em: {INVENTARIO_FILE}")


def load_downloaded() -> set[str]:
    """Carrega URLs já baixadas do arquivo de estado."""
    if DOWNLOADED_STATE_FILE.exists():
        return set(json.loads(DOWNLOADED_STATE_FILE.read_text()))
    return set()


def save_downloaded(downloaded: set[str]) -> None:
    """Persiste URLs baixadas."""
    DOWNLOADED_STATE_FILE.write_text(
        json.dumps(sorted(downloaded), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


async def download_file(client: httpx.AsyncClient, url: str, dest: Path) -> bool:
    """Download streaming de um arquivo. Retorna True se bem-sucedido."""
    if dest.exists():
        print(f"  [JÁ EXISTE] {dest.name}")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                async for chunk in resp.aiter_bytes(8192):
                    f.write(chunk)
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"  [OK] {dest.name} ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"  [ERRO] {dest.name}: {e}")
        if dest.exists():
            dest.unlink()
        return False


async def download_direct_files(courses: list[CourseInfo], token: str, downloaded: set[str]) -> set[str]:
    """Baixa todos os arquivos com download direto."""
    headers = {"Authorization": f"JWT {token}"}
    newly_downloaded = set()

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=300) as client:
        for course in courses:
            direct = [s for s in course.sources if s.file_url and s.file_url not in downloaded]
            if not direct:
                continue

            course_dir = EXTRA_DIR / sanitize_dirname(course.title)
            print(f"\n[{course.title}] — {len(direct)} arquivo(s) para baixar")

            for source in direct:
                subdir = CATEGORY_TO_DIR.get(source.category_key, "outros")
                dest_dir = course_dir / subdir
                fname = re.sub(r'[<>:"/\\|?*]', '_', source.name).strip()
                if not Path(fname).suffix:
                    ext = source.file_url.rsplit(".", 1)[-1].split("?")[0]
                    fname = f"{fname}.{ext}"
                dest = dest_dir / fname

                ok = await download_file(client, source.file_url, dest)
                if ok:
                    newly_downloaded.add(source.file_url)

    return newly_downloaded
