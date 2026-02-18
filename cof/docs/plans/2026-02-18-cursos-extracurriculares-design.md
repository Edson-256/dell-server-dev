# Design: Download de Cursos Extracurriculares

**Data:** 2026-02-18
**Status:** Aprovado

## Contexto

O projeto COF já baixa as aulas regulares (id=1 COF Original, id=30 COF Remasterizado).
Existem mais **26 cursos extracurriculares** na plataforma que precisam ser organizados e baixados.

## Inventário dos Cursos Extracurriculares

| ID | Título | Aulas | Sources |
|----|--------|-------|---------|
| 2  | Metafísica: A Estrutura do Ser | 6 | 0 (vazio) |
| 3  | Conceitos fundamentais de psicologia | 6 | 22 PDFs + 1 SC |
| 4  | A formação da personalidade | 6 | 1 SC |
| 5  | A crise da inteligência segundo Roger Scruton | 6 | 2 SC |
| 6  | Sociologia da filosofia | 7 | 1 SC |
| 7  | Simbolismo e ordem cósmica: ontem e hoje | 5 | 1 direto + 1 SC |
| 8  | Ser e Poder: Princípios e Métodos da Ciência Política | 5 | 1 SC |
| 9  | Princípios e métodos da auto-educação | 6 | 1 SC |
| 10 | Política e Cultura no Brasil: história e perspectivas | 6 | 1 SC |
| 11 | Mário Ferreira dos Santos: Guia para o estudo de sua obra | 5 | 1 SC |
| 12 | Introdução ao método filosófico | 6 | 1 SC |
| 13 | Introdução à filosofia de Louis Lavelle | 6 | 1 SC |
| 14 | Introdução à filosofia de Eric Voegelin | 6 | 1 SC |
| 15 | II Encontro de Escritores Brasileiros na Virginia | 4 | 1 SC |
| 16 | Guerra Cultural: história e estratégias | 4 | 1 SC |
| 17 | Filosofia da ciência | 6 | 1 SC |
| 18 | Esoterismo na História e hoje em dia | 5 | 1 SC |
| 19 | Consciência de imortalidade | 6 | 1 SC |
| 20 | Conhecimento e moralidade | 6 | 1 SC |
| 21 | Como tornar-se um leitor inteligente | 6 | 1 SC |
| 22 | A Guerra Contra a Inteligência | 5 | 1 SC |
| 23 | As raízes da modernidade | 6 | 1 SC |
| 24 | Teoria Geral do Estado | 11 | 1 SC |
| 25 | Ciência Política: Saber, Prever e Poder | 5 | 3 diretos + 2 SC |
| 27 | Educação pelos Clássicos | 15 | 0 (vazio) |
| 28 | Introdução à Filosofia de Olavo de Carvalho | 10 | 7 diretos |
| 31 | História Essencial da Filosofia (Curitiba 2003-2004) | 28 | 0 (vazio) |

**SC** = link SoundCloud (playlist)

## Estrutura de Pastas

```
data/extracurriculares/
  <Nome do Curso>/
    audios/           ← faixas SoundCloud ou arquivos diretos de áudio
    apostilas/        ← PDFs de leitura/materiais (category_key=books)
    transcricoes/     ← transcrições das aulas (se/quando disponíveis)

INVENTÁRIO.md         ← checklist de status de todos os cursos
```

## Abordagem de Implementação

**Script:** `scripts/download_extracurriculares.py` (independente do agente principal)

**Dependências novas:** `yt-dlp` (para SoundCloud)

### Fluxo

1. Auth via `data/token.json` existente
2. `GET /v1/user/courses/` → lista 26 cursos extras (excluindo id 1 e 30)
3. Para cada curso: `GET /v1/courses/sources/{course_id}` → lista sources
4. Gera/atualiza `data/extracurriculares/INVENTÁRIO.md`
5. Download:
   - `file != null` → httpx streaming para `audios/` ou `apostilas/`
   - `link` com SoundCloud → extrai URL da playlist → `yt-dlp` para `audios/`
6. Marca itens como baixados no INVENTÁRIO.md

### Flags CLI

```bash
.venv/bin/python3 scripts/download_extracurriculares.py            # inventário + download
.venv/bin/python3 scripts/download_extracurriculares.py --dry-run  # só inventário, sem baixar
.venv/bin/python3 scripts/download_extracurriculares.py --curso 6  # só um curso específico
```

### Formato do INVENTÁRIO.md

```markdown
# Inventário de Cursos Extracurriculares
Atualizado: 2026-02-18

## [x] Sociologia da Filosofia (id=6) — 7 aulas
- [x] audios/Sociologia da Filosofia - Playlist (SoundCloud)
- [ ] transcricoes/ — indisponível

## [ ] Conceitos fundamentais de psicologia (id=3) — 6 aulas
- [ ] audios/Conceitos Fundamentais de Psicologia (SoundCloud)
- [x] apostilas/ — 22 PDFs disponíveis
  - [x] A Criminalidade em Ascensão.pdf
  - ...
```

## Decisões Tomadas

- **Granularidade de áudio:** playlist completa por curso (não por aula individual)
- **PDFs:** pasta `/apostilas/` separada de `/transcricoes/`
- **Isolamento:** script separado, não interfere no agente principal rodando em paralelo
- **Estado:** INVENTÁRIO.md como fonte de verdade (não o state.json do agente)
