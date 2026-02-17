import logging
import time
from datetime import datetime

import schedule

from src.config import EXECUTION_WINDOWS

logger = logging.getLogger("cof.scheduler")


def is_within_window() -> bool:
    """Verifica se o horário atual está dentro de uma janela de execução."""
    now = datetime.now().time()
    for start_str, end_str in EXECUTION_WINDOWS:
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()
        if start <= now <= end:
            return True
    return False


def run_scheduler(execute_fn) -> None:
    """Executa o agendador que chama execute_fn dentro das janelas permitidas.

    Args:
        execute_fn: Função síncrona que executa um batch (deve chamar asyncio.run internamente).
    """
    def _check_and_run():
        if is_within_window():
            logger.info("Dentro da janela de execução, iniciando batch...")
            try:
                execute_fn()
            except Exception as e:
                logger.error("Erro durante execução do batch: %s", e)
        else:
            logger.debug("Fora da janela de execução, aguardando...")

    schedule.every(5).minutes.do(_check_and_run)

    logger.info(
        "Scheduler iniciado. Janelas de execução: %s",
        [f"{s}-{e}" for s, e in EXECUTION_WINDOWS],
    )

    while True:
        schedule.run_pending()
        time.sleep(60)
