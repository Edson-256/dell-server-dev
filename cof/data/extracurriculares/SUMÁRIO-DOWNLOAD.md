# Sumário do Download — Cursos Extracurriculares

**Data:** 2026-02-18
**Total baixado:** 139 arquivos (105 áudios + 34 PDFs)

---

## ✅ Baixados com sucesso (20 cursos)

| Curso | Aulas | Arquivos | Tipo |
|-------|-------|----------|------|
| Sociologia da filosofia (id=6) | 7 | 6 | 🎵 áudio |
| Conceitos fundamentais de psicologia (id=3) | 6 | 6 áudios + 22 PDFs | 🎵 + 📄 |
| A formação da personalidade (id=4) | 6 | 6 | 🎵 áudio |
| A crise da inteligência segundo Roger Scruton (id=5) | 6 | 6 | 🎵 áudio |
| Simbolismo e ordem cósmica: ontem e hoje (id=7) | 5 | 6 | 🎵 áudio |
| Ser e Poder: Princípios e Métodos da Ciência Política (id=8) | 5 | 5 | 🎵 áudio |
| Princípios e métodos da auto-educação (id=9) | 6 | 6 | 🎵 áudio |
| Mário Ferreira dos Santos: Guia para o estudo (id=11) | 5 | 5 | 🎵 áudio |
| Introdução à filosofia de Louis Lavelle (id=13) | 6 | 6 | 🎵 áudio |
| Introdução à filosofia de Eric Voegelin (id=14) | 6 | 6 | 🎵 áudio |
| II Encontro de Escritores Brasileiros na Virginia (id=15) | 4 | 4 | 🎵 áudio |
| Guerra Cultural: história e estratégias (id=16) | 4 | 4 | 🎵 áudio |
| Filosofia da ciência (id=17) | 6 | 6 | 🎵 áudio |
| Esoterismo na História e hoje em dia (id=18) | 5 | 5 | 🎵 áudio |
| Consciência de imortalidade (id=19) | 6 | 6 | 🎵 áudio |
| Conhecimento e moralidade (id=20) | 6 | 6 | 🎵 áudio |
| Como tornar-se um leitor inteligente (id=21) | 6 | 6 | 🎵 áudio |
| As raízes da modernidade (id=23) | 6 | 6 | 🎵 áudio |
| Ciência Política: Saber, Prever e Poder (id=25) | 5 | 5 áudios + 3 PDFs | 🎵 + 📄 |
| Introdução à Filosofia de Olavo de Carvalho (id=28) | 10 | 7 PDFs | 📄 |

---

## ❌ Falha no download — Playlist SoundCloud com erro 404 (3 cursos)

**Causa:** As URLs das playlists SoundCloud registradas na API estão desatualizadas ou foram removidas da plataforma. O yt-dlp retornou HTTP 404 ao tentar acessá-las.

**Solução possível:** Acessar manualmente a página de cada curso no site e verificar se o áudio foi migrado para outro serviço ou se há novos links disponíveis.

| Curso | Aulas | Motivo |
|-------|-------|--------|
| A Guerra Contra a Inteligência: o que estão fazendo para imbecilizar você (id=22) | 5 | Playlist SoundCloud inacessível (404) |
| Introdução ao método filosófico (id=12) | 6 | Playlist SoundCloud retornou 404 |
| Política e Cultura no Brasil: história e perspectivas (id=10) | 6 | Playlist SoundCloud retornou 404 |

---

## ⚠️ Sem conteúdo disponível na API (4 cursos)

**Causa:** A API (`/v1/courses/sources/{id}`) retornou zero fontes para esses cursos. O conteúdo pode ainda não ter sido publicado na plataforma ou pode estar em outro formato não suportado pela API atual.

| Curso | Aulas | Observação |
|-------|-------|------------|
| Metafísica: A Estrutura do Ser (id=2) | 6 | Zero sources na API |
| Teoria Geral do Estado (id=24) | 11 | Zero sources na API |
| Educação pelos Clássicos (id=27) | 15 | Zero sources na API |
| História Essencial da Filosofia — Curitiba 2003-2004 (id=31) | 28 | Zero sources na API |

---

## 🔄 Como retentar os cursos com falha

```bash
# Retentar um curso específico após corrigir o link manualmente
.venv/bin/python3 scripts/download_extracurriculares.py --curso 22

# Regenerar o inventário atualizado
.venv/bin/python3 scripts/download_extracurriculares.py --dry-run

# Baixar tudo novamente (pula o que já existe)
.venv/bin/python3 scripts/download_extracurriculares.py
```
