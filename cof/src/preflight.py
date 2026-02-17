import logging
import random

import httpx

from src.config import API_BASE

logger = logging.getLogger("cof.preflight")

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]



def get_random_ua() -> str:
    """Retorna um User-Agent aleatório do pool."""
    return random.choice(USER_AGENTS)


def _auth_headers(token: str) -> dict[str, str]:
    """Retorna headers de autenticação com JWT."""
    return {
        "Authorization": f"JWT {token}",
        "User-Agent": get_random_ua(),
    }


async def preflight_check(token: str) -> bool:
    """Executa verificações pré-voo antes de iniciar um batch."""
    checks = {
        "token_valid": False,
        "not_rate_limited": False,
        "content_accessible": False,
    }

    headers = _auth_headers(token)

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            # Verificar token via endpoint de conta
            r = await client.get(f"{API_BASE}/accounts/", timeout=30.0)
            checks["token_valid"] = r.status_code == 200
            checks["not_rate_limited"] = "retry-after" not in r.headers

            # Verificar acesso ao conteúdo do curso
            r2 = await client.get(f"{API_BASE}/courses/", timeout=30.0)
            checks["content_accessible"] = r2.status_code == 200
        except httpx.HTTPError as e:
            logger.error("Erro no preflight: %s", e)
            return False

    all_ok = all(checks.values())
    if all_ok:
        logger.info("Preflight OK: %s", checks)
    else:
        logger.warning("Preflight FALHOU: %s", checks)
    return all_ok
