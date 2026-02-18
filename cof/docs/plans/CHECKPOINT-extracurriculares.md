# Checkpoint — Download Extracurriculares

**Data:** 2026-02-18
**Status:** Em execução (subagent-driven)

## Como retomar esta sessão

Se a sessão cair, abra nova janela no diretório `/home/edson/dev/cof` e diga:

> "Retome o plano de implementação do script de cursos extracurriculares. O checkpoint está em `docs/plans/CHECKPOINT-extracurriculares.md` e o plano completo em `docs/plans/2026-02-18-download-extracurriculares.md`. Use `superpowers:executing-plans` para continuar de onde parou."

## Contexto

- **Objetivo:** `scripts/download_extracurriculares.py` — baixa os 26 cursos extras
- **Estrutura:** `data/extracurriculares/<nome>/{audios,apostilas,transcricoes}/` + `INVENTÁRIO.md`
- **Download:** httpx para arquivos diretos, yt-dlp para playlists SoundCloud
- **Venv:** `.venv/bin/python3` e `.venv/bin/yt-dlp`
- **Token:** `data/token.json` (já existe)
- **Cursos regulares a ignorar:** id=1 (COF Original) e id=30 (COF Remasterizado)

## Tasks (marcar conforme completadas)

- [ ] **Task 1:** Instalar yt-dlp + atualizar pyproject.toml
- [ ] **Task 2:** Funções utilitárias + descoberta via API (estrutura base do script)
- [ ] **Task 3:** Geração do INVENTÁRIO.md
- [ ] **Task 4:** Download de arquivos diretos via httpx
- [ ] **Task 5:** Download de playlists SoundCloud via yt-dlp
- [ ] **Task 6:** CLI principal (`--dry-run`, `--curso ID`) + integração completa
- [ ] **Task 7:** Execução completa + commit final

## Arquivos criados até agora

- `docs/plans/2026-02-18-cursos-extracurriculares-design.md` ✅
- `docs/plans/2026-02-18-download-extracurriculares.md` ✅
- `docs/plans/CHECKPOINT-extracurriculares.md` (este arquivo) ✅
- `scripts/download_extracurriculares.py` — **a criar**
- `data/extracurriculares/INVENTÁRIO.md` — **a criar**

## Decisões já tomadas

- Áudio: playlist completa por curso (não por aula individual)
- PDFs: pasta `/apostilas/` separada de `/transcricoes/`
- Estado local: `data/extracurriculares/downloaded.json` (no .gitignore)
- INVENTÁRIO.md: commitado ao repositório
