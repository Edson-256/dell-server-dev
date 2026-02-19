#!/usr/bin/env bash
# Download de áudios do COF via yt-dlp (SoundCloud)
#
# Uso:
#   ./scripts/download_audios.sh                # baixa tudo
#   ./scripts/download_audios.sh --remasterizado # só o remasterizado
#   ./scripts/download_audios.sh --original      # só o original

set -euo pipefail

YTDLP="$(dirname "$0")/../.venv/bin/yt-dlp"
BASE="$(dirname "$0")/.."

ORIG_DIR="$BASE/data/COF Original/audios"
REMASTER_DIR="$BASE/data/COF Remasterizado/audios"

# Formato: http_mp3 direto (sem HLS), fallback para qualquer mp3
FORMAT="http_mp3_0_0/hls_mp3_0_0/best"

download_original() {
    echo "=== COF Original: 6 playlists ==="
    mkdir -p "$ORIG_DIR"

    # Playlists com offset de número da aula
    declare -A PLAYLISTS=(
        ["https://api.soundcloud.com/playlists/129607784?secret_token=s-wGPZhi30ye7"]=0
        ["https://api.soundcloud.com/playlists/129576275?secret_token=s-c9lqVpEyHhO"]=100
        ["https://api.soundcloud.com/playlists/126051857?secret_token=s-345rg"]=200
        ["https://api.soundcloud.com/playlists/131412853?secret_token=s-1JOqoSGxXX6"]=300
        ["https://api.soundcloud.com/playlists/356073932?secret_token=s-w4N3D"]=400
        ["https://api.soundcloud.com/playlists/996059590?secret_token=s-HZzPv"]=500
    )

    for url in "${!PLAYLISTS[@]}"; do
        offset=${PLAYLISTS[$url]}
        echo ""
        echo "--- Playlist offset $offset ---"
        # playlist_index começa em 1, então Aula = offset + index
        # Usar autonumber com offset para gerar Aula_NNN
        "$YTDLP" \
            -f "$FORMAT" \
            --no-overwrites \
            --download-archive "$ORIG_DIR/.archive.txt" \
            -o "$ORIG_DIR/Aula_%(autonumber)03d.%(ext)s" \
            --autonumber-start $((offset + 1)) \
            --sleep-interval 2 \
            --max-sleep-interval 5 \
            "$url" || echo "AVISO: Erro na playlist offset $offset, continuando..."
    done
}

download_remasterizado() {
    echo "=== COF Remasterizado ==="
    mkdir -p "$REMASTER_DIR"

    # Extrair URLs do Remasterizado via Python
    "$BASE/.venv/bin/python3" -c "
import httpx, json
from urllib.parse import unquote, parse_qs, urlparse

with open('$BASE/data/token.json') as f:
    token = json.load(f)['token']

headers = {'Authorization': f'JWT {token}'}
client = httpx.Client(headers=headers, follow_redirects=True, timeout=30)

offset = 0
while True:
    r = client.get('https://api.seminariodefilosofia.org/v1/courses/sources/30', params={'limit': 100, 'offset': offset})
    data = r.json()
    for s in data['results']:
        if s.get('category_key') == 'audios' and s.get('link'):
            parsed = urlparse(s['link'])
            qs = parse_qs(parsed.query)
            url = unquote(qs.get('url', [''])[0])
            if url:
                print(url)
    if not data.get('next'):
        break
    offset += 100
" | while IFS= read -r url; do
        "$YTDLP" \
            -f "$FORMAT" \
            --no-overwrites \
            --download-archive "$REMASTER_DIR/.archive.txt" \
            -o "$REMASTER_DIR/%(title)s.%(ext)s" \
            --sleep-interval 2 \
            --max-sleep-interval 5 \
            "$url" || echo "AVISO: Erro em $url, continuando..."
    done
}

case "${1:-all}" in
    --original)      download_original ;;
    --remasterizado) download_remasterizado ;;
    *)               download_original; download_remasterizado ;;
esac

echo ""
echo "=== Concluído ==="
echo "Original:      $(ls "$ORIG_DIR"/*.mp3 2>/dev/null | wc -l) arquivos"
echo "Remasterizado: $(ls "$REMASTER_DIR"/*.mp3 2>/dev/null | wc -l) arquivos"
