import asyncio
import json
import logging
import random
from pathlib import Path

import httpx

from src.config import THROTTLE_SECONDS, BATCH_SIZE, STATE_FILE
from src.naming import generate_filename
from src.preflight import get_random_ua

logger = logging.getLogger("cof.downloader")


def load_state() -> dict:
    """Carrega estado persistente do disco."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            data = json.load(f)
        data["downloaded"] = set(data.get("downloaded", []))
        return data
    return {"downloaded": set()}


def save_state(state: dict) -> None:
    """Salva estado persistente em disco."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    serializable = {**state, "downloaded": list(state["downloaded"])}
    with open(STATE_FILE, "w") as f:
        json.dump(serializable, f, indent=2)


async def _download_file(client: httpx.AsyncClient, url: str, dest: Path) -> None:
    """Download com streaming para arquivos grandes."""
    async with client.stream("GET", url) as resp:
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            async for chunk in resp.aiter_bytes(chunk_size=8192):
                f.write(chunk)

    size_mb = dest.stat().st_size / (1024 * 1024)
    logger.debug("Arquivo salvo: %s (%.1f MB)", dest.name, size_mb)


async def download_batch(items: list, token: str, dry_run: bool = False) -> list[Path]:
    """Baixa um lote de arquivos respeitando throttle e limites.

    Args:
        items: Lista de MediaItem para download.
        token: Token JWT de autenticação.
        dry_run: Se True, apenas lista os arquivos sem baixar.

    Returns:
        Lista de paths dos arquivos baixados.
    """
    state = load_state()
    pending = [i for i in items if i.media_url not in state["downloaded"]]

    if not pending:
        logger.info("Nenhum arquivo pendente para download.")
        return []

    batch_size = random.randint(*BATCH_SIZE)
    batch = pending[:batch_size]
    logger.info(
        "%d pendentes, batch de %d selecionado (%d restantes após batch)",
        len(pending), len(batch), len(pending) - len(batch),
    )

    if dry_run:
        for item in batch:
            dest = generate_filename(item)
            logger.info("[DRY RUN] Seria baixado: %s -> %s", item.title, dest.name)
        return []

    downloaded: list[Path] = []
    headers = {
        "Authorization": f"JWT {token}",
        "User-Agent": get_random_ua(),
    }

    async with httpx.AsyncClient(
        headers=headers, follow_redirects=True, timeout=300.0
    ) as client:
        for i, item in enumerate(batch):
            dest = generate_filename(item)
            try:
                await _download_file(client, item.media_url, dest)
                state["downloaded"].add(item.media_url)
                save_state(state)
                downloaded.append(dest)
                logger.info("Baixado (%d/%d): %s", i + 1, len(batch), dest.name)
            except Exception as e:
                logger.error("Falha no download de '%s': %s", item.title, e)

            # Throttle entre downloads (exceto após o último)
            if i < len(batch) - 1:
                logger.debug("Aguardando %ds antes do próximo download...", THROTTLE_SECONDS)
                await asyncio.sleep(THROTTLE_SECONDS)

    return downloaded
