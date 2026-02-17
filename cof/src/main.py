import argparse
import asyncio
import logging
import sys

from src.config import setup_logging
from src.auth import get_authenticated_session
from src.preflight import preflight_check
from src.scraper import discover_media
from src.downloader import download_batch
from src.scheduler import run_scheduler

logger: logging.Logger


async def execute_batch(dry_run: bool = False) -> None:
    """Fluxo principal de uma execução de batch."""
    logger.info("=== Iniciando batch ===")

    # 1. Autenticação
    logger.info("Etapa 1/4: Autenticação")
    token = await get_authenticated_session()

    # 2. Preflight
    logger.info("Etapa 2/4: Verificações pré-voo")
    if not await preflight_check(token):
        logger.error("Preflight falhou. Abortando batch.")
        return

    # 3. Descoberta
    logger.info("Etapa 3/4: Descoberta de conteúdo")
    items = await discover_media(token)
    logger.info("%d itens encontrados no catálogo.", len(items))

    if not items:
        logger.info("Nenhum item para processar. Encerrando.")
        return

    # 4. Download
    logger.info("Etapa 4/4: Download")
    downloaded = await download_batch(items, token, dry_run=dry_run)
    logger.info("=== Batch concluído: %d arquivos baixados ===", len(downloaded))


def _run_batch(dry_run: bool = False) -> None:
    """Wrapper síncrono para execute_batch."""
    asyncio.run(execute_batch(dry_run=dry_run))


def cli() -> None:
    """Entry point CLI."""
    global logger
    logger = setup_logging()

    parser = argparse.ArgumentParser(
        description="COF — Agente de download automatizado"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Lista arquivos sem baixar",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Executa um único batch e encerra (ignora scheduler)",
    )
    args = parser.parse_args()

    logger.info("COF iniciado (dry_run=%s, once=%s)", args.dry_run, args.once)

    if args.once:
        _run_batch(dry_run=args.dry_run)
    else:
        run_scheduler(lambda: _run_batch(dry_run=args.dry_run))


if __name__ == "__main__":
    cli()
