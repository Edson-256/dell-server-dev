# Sumário do Download — Cursos Extracurriculares

**Data:** 2026-02-18
**Total baixado:** 138 arquivos — 105 áudios (mp3/m4a/opus) + 33 PDFs

---

## ✅ Baixados com sucesso (21 cursos)

| Curso | Aulas | Arquivos | Tipo |
|-------|-------|----------|------|
| A crise da inteligência segundo Roger Scruton (id=5) | 6 | 6 | 🎵 áudio |
| A formação da personalidade (id=4) | 6 | 6 | 🎵 áudio |
| As raízes da modernidade (id=23) | 6 | 6 | 🎵 áudio |
| Ciência Política: Saber, Prever e Poder (id=25) | 5 | 5 áudios + 3 PDFs | 🎵 + 📄 |
| Como tornar-se um leitor inteligente (id=21) | 6 | 6 | 🎵 áudio |
| Conceitos fundamentais de psicologia (id=3) | 6 | 6 áudios + 22 PDFs | 🎵 + 📄 |
| Consciência de imortalidade (id=19) | 6 | 6 | 🎵 áudio |
| Conhecimento e moralidade (id=20) | 6 | 6 | 🎵 áudio |
| Esoterismo na História e hoje em dia (id=18) | 5 | 5 | 🎵 áudio |
| Filosofia da ciência (id=17) | 6 | 6 | 🎵 áudio |
| Guerra Cultural: história e estratégias (id=16) | 4 | 4 | 🎵 áudio |
| II Encontro de Escritores Brasileiros na Virginia (id=15) | 4 | 4 | 🎵 áudio |
| Introdução à filosofia de Eric Voegelin (id=14) | 6 | 6 | 🎵 áudio |
| Introdução à filosofia de Louis Lavelle (id=13) | 6 | 6 | 🎵 áudio |
| Introdução à Filosofia de Olavo de Carvalho (id=28) | 10 | 7 PDFs | 📄 |
| Mário Ferreira dos Santos: Guia para o estudo (id=11) | 5 | 5 | 🎵 áudio |
| Princípios e métodos da auto-educação (id=9) | 6 | 6 | 🎵 áudio |
| Ser e Poder: Princípios e Métodos da Ciência Política (id=8) | 5 | 5 | 🎵 áudio |
| Simbolismo e ordem cósmica: ontem e hoje (id=7) | 5 | 5 áudios + 1 PDF | 🎵 + 📄 |
| Sociologia da filosofia (id=6) | 7 | 6 | 🎵 áudio |
| Mário Ferreira dos Santos: Guia para o estudo de sua obra (id=11) | 5 | 5 | 🎵 áudio |

---

## ❌ Falha no download — Playlist SoundCloud removida (3 cursos)

**Causa:** As playlists foram deletadas do SoundCloud. O yt-dlp retorna HTTP 404 ao tentar acessá-las. Os links estão desatualizados na API do Seminário.

**Solução possível:** Acessar manualmente a página de cada curso no site e verificar se o áudio foi migrado para outro serviço ou republicado.

| Curso | ID | URL da playlist (morta) |
|-------|----|-------------------------|
| Política e Cultura no Brasil: história e perspectivas | 10 | `https://api.soundcloud.com/playlists/215601166` |
| Introdução ao método filosófico | 12 | `https://api.soundcloud.com/playlists/126053706` |
| A Guerra Contra a Inteligência | 22 | `https://api.soundcloud.com/playlists/467075442` |

---

## ⚠️ Sem conteúdo disponível na API (4 cursos)

**Causa:** A API retornou zero fontes para esses cursos. O conteúdo pode ainda não ter sido publicado na plataforma.

| Curso | ID | Aulas |
|-------|----|-------|
| Metafísica: A Estrutura do Ser | 2 | 6 |
| Teoria Geral do Estado | 24 | 11 |
| Educação pelos Clássicos | 27 | 15 |
| História Essencial da Filosofia — Curitiba 2003-2004 | 31 | 28 |

---

## 🔄 Como retentar / atualizar

```bash
# Baixar tudo novamente (pula o que já existe no disco)
.venv/bin/python3 scripts/download_extracurriculares.py

# Só um curso específico pelo ID
.venv/bin/python3 scripts/download_extracurriculares.py --curso 10

# Gerar inventário atualizado sem baixar
.venv/bin/python3 scripts/download_extracurriculares.py --dry-run
```

## Notas técnicas

- Áudios SoundCloud baixados com `yt-dlp` + `ffmpeg` (localizado automaticamente via `shutil.which`)
- PDFs baixados via `httpx` streaming
- Estado persistido em `downloaded.json` (ignorado pelo git)
- Formatos de áudio: mp3, m4a, opus (conforme disponibilidade no SoundCloud)
