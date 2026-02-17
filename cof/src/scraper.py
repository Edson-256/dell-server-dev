import logging
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from src.config import API_BASE, COURSES
from src.preflight import get_random_ua

logger = logging.getLogger("cof.scraper")


@dataclass
class MediaItem:
    title: str
    lesson_number: int
    media_url: str
    extension: str
    item_type: str  # "transcription" | "audios" | "videos" | "books"
    course_name: str | None = None
    category: str | None = None


def _extract_extension(url: str) -> str:
    """Extrai extensão do arquivo a partir da URL."""
    path = urlparse(url).path
    if "." in path:
        return path.rsplit(".", 1)[-1].lower()
    return "bin"


async def _fetch_paginated(client: httpx.AsyncClient, url: str, params: dict | None = None) -> list[dict]:
    """Busca todos os resultados de um endpoint paginado."""
    all_results = []
    params = dict(params or {})
    params.setdefault("limit", 100)
    params.setdefault("offset", 0)

    while True:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        all_results.extend(results)

        if not data.get("next"):
            break
        params["offset"] += params["limit"]

    return all_results


async def _discover_course(client: httpx.AsyncClient, course_id: int, course_name: str) -> list[MediaItem]:
    """Descobre itens de mídia com download direto para um curso."""
    items: list[MediaItem] = []

    # Buscar lessons (para mapear lesson_id -> número)
    lessons = await _fetch_paginated(
        client, f"{API_BASE}/courses/lessons/{course_id}", {"sort": "asc"}
    )
    lesson_map = {l["id"]: l for l in lessons}
    logger.info("  %s: %d aulas", course_name, len(lessons))

    # Buscar sources
    sources = await _fetch_paginated(
        client, f"{API_BASE}/courses/sources/{course_id}"
    )
    logger.info("  %s: %d sources", course_name, len(sources))

    for source in sources:
        # Apenas itens com download direto (file preenchido)
        file_url = source.get("file")
        if not file_url:
            continue

        category_key = source.get("category_key", "other")
        name = source.get("name", "Sem título")
        lesson_id = source.get("lesson")
        lesson_info = lesson_map.get(lesson_id, {})
        lesson_number = lesson_info.get("number", 0)

        items.append(MediaItem(
            title=name,
            lesson_number=lesson_number,
            media_url=file_url,
            extension=_extract_extension(file_url),
            item_type=category_key,
            course_name=course_name,
            category=source.get("category"),
        ))

    return items


async def discover_media(token: str) -> list[MediaItem]:
    """Descobre URLs de mídia disponíveis via API REST para todos os cursos."""
    all_items: list[MediaItem] = []

    headers = {
        "Authorization": f"JWT {token}",
        "User-Agent": get_random_ua(),
    }

    logger.info("Iniciando descoberta de conteúdo (%d cursos)", len(COURSES))

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        for course_id, course_name in COURSES:
            try:
                items = await _discover_course(client, course_id, course_name)
                all_items.extend(items)
            except Exception as e:
                logger.error("Erro ao descobrir curso %s (id=%d): %s", course_name, course_id, e)

    # Deduplicar por URL
    seen = set()
    unique_items = []
    for item in all_items:
        if item.media_url not in seen:
            seen.add(item.media_url)
            unique_items.append(item)

    # Estatísticas
    by_type = {}
    for item in unique_items:
        by_type.setdefault(item.item_type, 0)
        by_type[item.item_type] += 1
    logger.info("Descoberta concluída: %d itens com download direto — %s", len(unique_items), by_type)

    return unique_items
