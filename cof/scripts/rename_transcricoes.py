#!/usr/bin/env python3
"""Renomeia transcrições do COF para o padrão Aula_XXX-YYYY-MM-DD.ext

Uso:
    python scripts/rename_transcricoes.py            # dry-run (só mostra)
    python scripts/rename_transcricoes.py --executar  # renomeia de fato
"""

import re
import sys
import unicodedata
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERRO: pymupdf não instalado. Execute: pip install pymupdf")
    sys.exit(1)

try:
    from docx import Document
except ImportError:
    print("ERRO: python-docx não instalado. Execute: pip install python-docx")
    sys.exit(1)


MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

BASE = Path(__file__).resolve().parent.parent
DIRS = [
    BASE / "data" / "COF Original" / "transcricoes",
    BASE / "data" / "COF Remasterizado" / "transcricoes",
]


# ---------------------------------------------------------------------------
# Detecção de tipo real via magic bytes
# ---------------------------------------------------------------------------

def detectar_tipo_real(path: Path) -> str:
    with open(path, "rb") as f:
        header = f.read(8)
    if header[:4] == b"%PDF":
        return ".pdf"
    if header[:2] == b"PK":
        return ".docx"
    if header[:4] == b"\xd0\xcf\x11\xe0":
        return ".doc"
    return path.suffix


# ---------------------------------------------------------------------------
# Extração do número da aula
# ---------------------------------------------------------------------------

def extrair_numero_aula(nome: str) -> int | None:
    """Extrai o número real da aula (não o prefixo de ordenação)."""
    if "_-_" in nome:
        parte_direita = nome.split("_-_", 1)[1]
        m = re.search(r"[Aa]ula\s*(\d+)", parte_direita)
        if m:
            return int(m.group(1))
        m = re.search(r"(\d+)", parte_direita)
        if m:
            return int(m.group(1))
    m = re.search(r"[Aa]ula[_ ]?(\d+)", nome)
    if m:
        return int(m.group(1))
    return None


# ---------------------------------------------------------------------------
# Extração de data
# ---------------------------------------------------------------------------

# "14 de março de 2009", "1º de setembro de 2018", "21de dezembro de2019",
# "04 abril de 2009", "18 de julho 2020"
REGEX_DATA_PT = re.compile(
    r"(\d{1,2})[ºª°]?\s*(?:de\s+)?(\w+)\s+(?:de\s*)?(\d{4})"
)
# "07/07/2018"
REGEX_DATA_SLASH = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
# "Novembro de 2009" (só mês e ano → dia=1)
REGEX_MES_ANO = re.compile(r"([A-Z][a-zçãõé]+)\s+de\s+(\d{4})")
# DD_MM_YYYY no nome do arquivo
REGEX_DATA_NOME = re.compile(r"(\d{2})_(\d{2})_(\d{4})")


def _data_do_texto(texto: str) -> str | None:
    """Busca data em português nas primeiras 8 linhas não-vazias."""
    linhas = [l.strip() for l in texto.split("\n") if l.strip()][:8]
    for linha in linhas:
        # Padrão completo: dia + mês por extenso + ano
        m = REGEX_DATA_PT.search(linha)
        if m:
            dia, mes_nome, ano = int(m.group(1)), m.group(2).lower(), int(m.group(3))
            mes = MESES.get(mes_nome)
            if mes:
                return f"{ano:04d}-{mes:02d}-{dia:02d}"
        # DD/MM/YYYY
        m = REGEX_DATA_SLASH.search(linha)
        if m:
            dia, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if 1 <= mes <= 12 and 1 <= dia <= 31:
                return f"{ano:04d}-{mes:02d}-{dia:02d}"
    # Fallback: só mês e ano (sem dia) → usar dia=1
    for linha in linhas:
        m = REGEX_MES_ANO.search(linha)
        if m:
            mes_nome, ano = m.group(1).lower(), int(m.group(2))
            mes = MESES.get(mes_nome)
            if mes:
                return f"{ano:04d}-{mes:02d}-01"
    return None


def extrair_data_pdf(path: Path) -> str | None:
    try:
        doc = fitz.open(path)
        if len(doc) == 0:
            doc.close()
            return None
        texto = doc[0].get_text()
        doc.close()
        return _data_do_texto(texto)
    except Exception as e:
        print(f"  AVISO: Erro ao ler PDF {path.name}: {e}")
        return None


def extrair_data_docx(path: Path) -> str | None:
    try:
        doc = Document(path)
        paragrafos = []
        for p in doc.paragraphs[:12]:
            if p.text.strip():
                paragrafos.append(p.text.strip())
            if len(paragrafos) >= 8:
                break
        return _data_do_texto("\n".join(paragrafos))
    except Exception as e:
        print(f"  AVISO: Erro ao ler DOCX {path.name}: {e}")
        return None


def extrair_data_nome(nome: str) -> str | None:
    m = REGEX_DATA_NOME.search(nome)
    if m:
        dia, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mes <= 12 and 1 <= dia <= 31:
            return f"{ano:04d}-{mes:02d}-{dia:02d}"
    return None


# ---------------------------------------------------------------------------
# Geração do novo nome
# ---------------------------------------------------------------------------

def _normalizar_titulo(texto: str) -> str:
    """Remove acentos e caracteres especiais para uso em nome de arquivo."""
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    resultado = re.sub(r"[^a-zA-Z0-9]", "_", sem_acento)
    resultado = re.sub(r"_+", "_", resultado)
    return resultado.strip("_")


def gerar_novo_nome(
    path: Path, num_aula: int, data: str | None, tipo_real: str
) -> str | None:
    if data:
        return f"Aula_{num_aula:03d}-{data}{tipo_real}"

    # Sem data: somente Aula 000 tem tratamento especial
    if num_aula == 0:
        nome = path.stem
        if "Apresentação" in nome or "Apresentacao" in nome:
            return f"Aula_000-Apresentacao_do_COF{tipo_real}"
        if "Questões Preliminares" in nome or "Questoes Preliminares" in nome:
            return f"Aula_000-Questoes_Preliminares_do_COF{tipo_real}"
        # Fallback: usar título extraído do nome
        parte = nome.split("_-_", 1)[1] if "_-_" in nome else nome
        titulo = _normalizar_titulo(parte)
        return f"Aula_000-{titulo}{tipo_real}"

    # Outros sem data → não renomear
    return None


# ---------------------------------------------------------------------------
# Processamento
# ---------------------------------------------------------------------------

def processar_diretorio(diretorio: Path):
    if not diretorio.exists():
        print(f"Diretório não encontrado: {diretorio}")
        return [], []

    arquivos = sorted(f for f in diretorio.iterdir() if f.is_file())
    renomeacoes = []  # (path_original, novo_nome)
    falhas = []  # (path_original, motivo)

    for path in arquivos:
        nome = path.name

        # Ignorar metadados do macOS
        if nome.startswith("._"):
            continue

        # 1. Número da aula
        num_aula = extrair_numero_aula(nome)
        if num_aula is None:
            falhas.append((path, "Número da aula não encontrado"))
            continue

        # 2. Tipo real via magic bytes
        tipo_real = detectar_tipo_real(path)

        # 3. Data — tentar conteúdo primeiro, depois nome
        data = None
        if tipo_real == ".pdf":
            data = extrair_data_pdf(path)
        elif tipo_real == ".docx":
            data = extrair_data_docx(path)

        if data is None:
            data = extrair_data_nome(nome)

        # 4. Novo nome
        novo_nome = gerar_novo_nome(path, num_aula, data, tipo_real)
        if novo_nome is None:
            falhas.append((path, "Data não encontrada"))
            continue

        if nome == novo_nome:
            continue

        renomeacoes.append((path, novo_nome))

    return renomeacoes, falhas


def resolver_colisoes(renomeacoes: list) -> list:
    """Detecta e resolve colisões adicionando sufixo _2, _3, etc."""
    destinos: dict[str, Path] = {}
    resultado = []

    for path, novo_nome in renomeacoes:
        chave = str(path.parent / novo_nome)

        if chave not in destinos:
            destinos[chave] = path
            resultado.append((path, novo_nome))
        else:
            stem, ext = novo_nome.rsplit(".", 1)
            contador = 2
            while True:
                nome_alt = f"{stem}_{contador}.{ext}"
                chave_alt = str(path.parent / nome_alt)
                if chave_alt not in destinos:
                    destinos[chave_alt] = path
                    resultado.append((path, nome_alt))
                    print(f"  COLISÃO: {path.name} → {nome_alt} (conflito com {destinos[chave].name})")
                    break
                contador += 1

    return resultado


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    executar = "--executar" in sys.argv

    if not executar:
        print("=== MODO DRY-RUN (use --executar para renomear de fato) ===\n")
    else:
        print("=== EXECUTANDO RENOMEAÇÃO ===\n")

    total_renomeados = 0
    total_falhas = 0

    for diretorio in DIRS:
        print(f"\n--- {diretorio.relative_to(BASE)} ---")
        arquivos_antes = list(diretorio.iterdir()) if diretorio.exists() else []
        print(f"Arquivos: {len(arquivos_antes)}")

        renomeacoes, falhas = processar_diretorio(diretorio)
        renomeacoes = resolver_colisoes(renomeacoes)

        for path, novo_nome in renomeacoes:
            print(f"  {path.name}")
            print(f"    → {novo_nome}")

        for path, motivo in falhas:
            print(f"  FALHA: {path.name} ({motivo})")

        if executar and renomeacoes:
            for path, novo_nome in renomeacoes:
                destino = path.parent / novo_nome
                path.rename(destino)
            arquivos_depois = list(diretorio.iterdir())
            print(f"Arquivos depois: {len(arquivos_depois)}")
            if len(arquivos_antes) != len(arquivos_depois):
                print(
                    f"  ATENÇÃO: contagem mudou de "
                    f"{len(arquivos_antes)} para {len(arquivos_depois)}!"
                )

        total_renomeados += len(renomeacoes)
        total_falhas += len(falhas)

    print(f"\n=== RESUMO ===")
    print(f"Renomeações: {total_renomeados}")
    print(f"Falhas: {total_falhas}")


if __name__ == "__main__":
    main()
