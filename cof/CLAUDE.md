# COF — Agente de Download Automatizado

## Sobre o Projeto

Agente automatizado para download de material do Seminário de Filosofia (`seminariodefilosofia.org`).
Stack: Python 3.11+, asyncio, Playwright, httpx, python-dotenv, schedule.

## Skills Disponíveis (Antigravity Awesome Skills)

**ANTES de iniciar qualquer tarefa**, consulte o repositório de skills em `~/dev/ai-skills/skills/` para verificar se existe alguma skill relevante. Se encontrar, instale-a com:

```bash
# Listar skills disponíveis
ls ~/dev/ai-skills/skills/

# Buscar skills por palavra-chave
ls ~/dev/ai-skills/skills/ | grep -i <palavra-chave>

# Instalar uma skill (copiar para o projeto)
cp -r ~/dev/ai-skills/skills/<nome-da-skill>/SKILL.md .claude/skills/<nome-da-skill>.md
```

### Skills relevantes para este projeto

| Skill | Quando usar |
|-------|-------------|
| `async-python-patterns` | Trabalho com asyncio, concorrência, I/O assíncrono |
| `playwright-skill` | Automação de browser, login, scraping |
| `browser-automation` | Padrões de anti-detecção, seletores, waits |
| `python-pro` | Padrões modernos Python 3.12+, otimização |
| `python-patterns` | Padrões gerais de Python |
| `python-testing-patterns` | Escrita de testes |
| `auth-implementation-patterns` | Padrões de autenticação (JWT) |
| `firecrawl-scraper` | Scraping avançado |

### Como buscar novas skills

Para tarefas que envolvam tecnologias ou padrões não listados acima:

```bash
ls ~/dev/ai-skills/skills/ | grep -iE '<termos-relevantes>'
```

Leia o `SKILL.md` da skill encontrada para entender se se aplica ao contexto.

## Estrutura do Projeto

```
src/
  main.py          — CLI e orquestração (4 etapas: auth -> preflight -> discover -> download)
  config.py        — Configuração, caminhos, credenciais, logging
  auth.py          — Login via Playwright + JWT token management
  preflight.py     — Verificações pré-execução
  scraper.py       — Descoberta de mídia via API REST paginada
  downloader.py    — Download streaming com throttle e estado persistente
  naming.py        — Nomes padronizados (Aula_NNN_-_Titulo.ext)
  scheduler.py     — Agendador com janelas de execução
data/              — Arquivos baixados + estado (state.json, token.json)
logs/              — Logs rotativos
```

## Convenções

- Linguagem do código: português (logs, nomes de variáveis descritivas)
- Async-first: todas as operações de I/O usam async/await
- Estado persistente em JSON (`data/state.json`)
- Credenciais via `.env` (COF_EMAIL, COF_PASSWORD)
- Entry point: `cof = "src.main:cli"`
