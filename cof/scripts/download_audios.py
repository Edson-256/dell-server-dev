#!/usr/bin/env python3
"""Download de áudios do COF via yt-dlp (SoundCloud).

Uso:
    python scripts/download_audios.py                    # baixa tudo
    python scripts/download_audios.py --original         # só COF Original
    python scripts/download_audios.py --remasterizado    # só COF Remasterizado
    python scripts/download_audios.py --dry-run          # só lista sem baixar
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import httpx

BASE = Path(__file__).resolve().parent.parent
YTDLP = str(BASE / ".venv" / "bin" / "yt-dlp")
TOKEN_FILE = BASE / "data" / "token.json"

ORIG_DIR = BASE / "data" / "COF Original" / "audios"
REMASTER_DIR = BASE / "data" / "COF Remasterizado" / "audios"

API_BASE = "https://api.seminariodefilosofia.org/v1"

# Playlists do COF Original
PLAYLISTS_ORIGINAL = [
    "https://api.soundcloud.com/playlists/129607784?secret_token=s-wGPZhi30ye7",
    "https://api.soundcloud.com/playlists/129576275?secret_token=s-c9lqVpEyHhO",
    "https://api.soundcloud.com/playlists/126051857?secret_token=s-345rg",
    "https://api.soundcloud.com/playlists/131412853?secret_token=s-1JOqoSGxXX6",
    "https://api.soundcloud.com/playlists/356073932?secret_token=s-w4N3D",
    "https://api.soundcloud.com/playlists/996059590?secret_token=s-HZzPv",
]

FORMAT = "http_mp3_0_0/http_mp3_1_0/hls_mp3_0_0/hls_mp3_1_0/best"

# Slugs com formato não-padrão → número correto da aula
SLUG_OVERRIDES = {
    "cof20110924123": 123,     # aula 123, data 2011-09-24
    "aula-4333-28072018": 433,  # aula 433 (typo), data 2018-07-28
}

# Padrões de slug do SoundCloud para extrair número da aula:
# aula-100-02042011, cof-003-20090404, aula-01-14032009,
# cof20170916a400, aual-289-18042015, aula-4333-28072018
RE_AULA_SLUG = re.compile(r"aula[_-]0*(\d{1,3})(?:\D|$)")  # aula-NNN ou aula_NNN
RE_COF_A_NUM = re.compile(r"a(\d{1,3})(?:\D|$)")  # cof20170916a400 → 400
RE_AUAL_SLUG = re.compile(r"aual[_-]0*(\d{1,3})")  # typo: aual-289


def load_token() -> str:
    with open(TOKEN_FILE) as f:
        return json.load(f)["token"]


def _extract_sc_url(embed_link: str) -> str | None:
    parsed = urlparse(embed_link)
    qs = parse_qs(parsed.query)
    url = qs.get("url", [None])[0]
    return unquote(url) if url else None


def _extract_aula_num(sc_url: str) -> int | None:
    """Extrai número da aula da URL do SoundCloud."""
    path = urlparse(sc_url).path
    # slug: último segmento antes de /s-xxx
    parts = [p for p in path.split("/") if p and not p.startswith("s-")]
    slug = parts[-1] if parts else ""

    # 0. Override manual para slugs não-padrão
    if slug in SLUG_OVERRIDES:
        return SLUG_OVERRIDES[slug]

    # 1. Padrão "aula-NNN" (mais confiável)
    m = RE_AULA_SLUG.search(slug)
    if m:
        num = int(m.group(1))
        if 1 <= num <= 600:
            return num

    # 2. Typo "aual-NNN"
    m = RE_AUAL_SLUG.search(slug)
    if m:
        return int(m.group(1))

    # 3. Padrão "cof...aNNN" (ex: cof20170916a400)
    m = RE_COF_A_NUM.search(slug)
    if m:
        num = int(m.group(1))
        if 1 <= num <= 600:
            return num

    # 4. Padrão "cof-NNN"
    m = re.search(r"cof[_-]0*(\d{1,3})(?:\D|$)", slug)
    if m:
        num = int(m.group(1))
        if 1 <= num <= 600:
            return num

    return None


def load_archive(archive_path: Path) -> set[str]:
    if not archive_path.exists():
        return set()
    return {line.strip() for line in archive_path.read_text().splitlines() if line.strip()}


def save_archive_entry(archive_path: Path, entry: str) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with open(archive_path, "a") as f:
        f.write(entry + "\n")


def download_track(url: str, output_path: Path, archive_path: Path) -> bool:
    """Baixa uma track com yt-dlp. Retorna True se sucesso."""
    if output_path.exists():
        return True

    cmd = [
        YTDLP,
        "-f", FORMAT,
        "-o", str(output_path),
        "--no-overwrites",
        "--quiet", "--no-warnings",
        "--progress",
        url,
    ]

    result = subprocess.run(cmd)
    if result.returncode == 0 and output_path.exists():
        save_archive_entry(archive_path, f"soundcloud {url}")
        return True
    return False


def download_original(dry_run: bool = False):
    print("=== COF Original: 6 playlists ===")
    ORIG_DIR.mkdir(parents=True, exist_ok=True)
    archive = ORIG_DIR / ".archive.txt"
    archived = load_archive(archive)

    # Fase 1: coletar todas as tracks de todas as playlists com dedup
    all_tracks: dict[int, tuple[int, str]] = {}  # aula_num -> (playlist_idx, track_url)

    for pl_i, playlist_url in enumerate(PLAYLISTS_ORIGINAL):
        cmd = [
            YTDLP, "--flat-playlist",
            "--print", "%(playlist_index)s %(url)s",
            playlist_url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ERRO ao listar playlist {pl_i + 1}: {result.stderr.strip()}")
            continue

        count = 0
        for line in result.stdout.strip().splitlines():
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            idx = int(parts[0])
            track_url = parts[1]
            aula_num = _extract_aula_num(track_url)
            if aula_num and aula_num not in all_tracks:
                all_tracks[aula_num] = (idx, track_url)
                count += 1

        print(f"  Playlist {pl_i + 1}: {count} aulas novas")

    print(f"\nTotal: {len(all_tracks)} aulas únicas")

    # Fase 2: baixar em ordem
    total_ok = 0
    total_skip = 0
    total_fail = 0

    for aula_num in sorted(all_tracks.keys()):
        _, track_url = all_tracks[aula_num]
        dest = ORIG_DIR / f"Aula_{aula_num:03d}.mp3"

        if dest.exists():
            total_skip += 1
            continue

        if dry_run:
            print(f"  [DRY RUN] Aula_{aula_num:03d}.mp3")
            continue

        print(f"  Baixando Aula_{aula_num:03d}.mp3 ...", end=" ", flush=True)
        if download_track(track_url, dest, archive):
            total_ok += 1
            print("OK")
        else:
            total_fail += 1
            print("FALHA")
        time.sleep(2)

    if not dry_run:
        print(f"\nOriginal: {total_ok} baixados, {total_skip} já existiam, {total_fail} falhas")


def download_remasterizado(dry_run: bool = False):
    print("\n=== COF Remasterizado ===")
    REMASTER_DIR.mkdir(parents=True, exist_ok=True)
    archive = REMASTER_DIR / ".archive.txt"
    archived = load_archive(archive)

    token = load_token()
    headers = {"Authorization": f"JWT {token}"}

    tracks = []
    offset = 0
    with httpx.Client(headers=headers, follow_redirects=True, timeout=30) as client:
        while True:
            r = client.get(
                f"{API_BASE}/courses/sources/30",
                params={"limit": 100, "offset": offset},
            )
            data = r.json()
            for s in data["results"]:
                if s.get("category_key") == "audios" and s.get("link"):
                    sc_url = _extract_sc_url(s["link"])
                    if sc_url:
                        tracks.append({"name": s.get("name", "sem_nome"), "url": sc_url})
            if not data.get("next"):
                break
            offset += 100

    print(f"  {len(tracks)} tracks encontradas")

    total_ok = 0
    total_skip = 0
    total_fail = 0

    for track in tracks:
        name = track["name"] or "sem_nome"
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name).strip("_ ")
        dest = REMASTER_DIR / f"{safe_name}.mp3"

        if dest.exists():
            total_skip += 1
            continue

        if dry_run:
            print(f"  [DRY RUN] {safe_name}.mp3")
            continue

        print(f"  Baixando {safe_name}.mp3 ...", end=" ", flush=True)
        if download_track(track["url"], dest, archive):
            total_ok += 1
            print("OK")
        else:
            total_fail += 1
            print("FALHA")
        time.sleep(2)

    if not dry_run:
        print(f"\nRemasterizado: {total_ok} baixados, {total_skip} já existiam, {total_fail} falhas")


def main():
    dry_run = "--dry-run" in sys.argv
    do_original = "--original" in sys.argv or ("--remasterizado" not in sys.argv)
    do_remaster = "--remasterizado" in sys.argv or ("--original" not in sys.argv)

    if dry_run:
        print("=== MODO DRY-RUN ===\n")

    if do_original:
        download_original(dry_run)
    if do_remaster:
        download_remasterizado(dry_run)


if __name__ == "__main__":
    main()
