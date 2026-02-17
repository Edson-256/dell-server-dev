import json
import logging

from playwright.async_api import async_playwright

from src.config import EMAIL, PASSWORD, LOGIN_URL, COOKIE_FILE, API_BASE

logger = logging.getLogger("cof.auth")

# Reutilizamos COOKIE_FILE para armazenar o token (compat com nome existente)
TOKEN_FILE = COOKIE_FILE.with_name("token.json")


def _save_token(token: str) -> None:
    """Persiste token JWT em disco."""
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token}, f)
    logger.debug("Token salvo em %s", TOKEN_FILE)


def _load_token() -> str | None:
    """Carrega token JWT do disco, se existir."""
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    token = data.get("token")
    logger.debug("Token carregado de %s", TOKEN_FILE)
    return token


async def _validate_token(token: str) -> bool:
    """Verifica se o token JWT ainda é válido via API."""
    import httpx

    headers = {
        "Authorization": f"JWT {token}",
    }
    try:
        async with httpx.AsyncClient(headers=headers) as client:
            r = await client.get(
                f"{API_BASE}/accounts/",
                timeout=15.0,
            )
            valid = r.status_code == 200
    except Exception:
        valid = False

    logger.debug("Validação de token: %s", "OK" if valid else "EXPIRADO")
    return valid


async def login() -> str:
    """Realiza login via Playwright e retorna token JWT."""
    logger.info("Realizando login em %s", LOGIN_URL)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        await page.fill('input[type="email"]', EMAIL)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        # Aguardar redirecionamento pós-login
        await page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
        await page.wait_for_load_state("networkidle")

        # Extrair token JWT do localStorage
        token = await page.evaluate("() => localStorage.getItem('_apiToken')")
        await browser.close()

    if not token:
        raise RuntimeError("Token JWT não encontrado no localStorage após login")

    _save_token(token)
    logger.info("Login realizado com sucesso (token JWT obtido)")
    return token


async def get_authenticated_session() -> str:
    """Retorna token JWT válido, fazendo re-login se necessário."""
    token = _load_token()
    if token and await _validate_token(token):
        logger.info("Token existente ainda é válido")
        return token
    logger.info("Token expirado ou inexistente, realizando novo login")
    return await login()
