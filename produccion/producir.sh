#!/bin/bash
# Produce un vídeo completo a partir de produccion/escenas/<nombre>_{scene,ov}.py, <nombre>.txt y <nombre>.mp3.
# Uso: produccion/producir.sh <nombre> [estilo_musica 0-5]
# Salida: produccion/trabajo/<nombre>/<nombre>_final_c.mp4 (IG/YT) y <nombre>_tiktok_final_c.mp4 (con música)
# Para renderizar solo un tramo: RANGO="f0 f1" (y luego vuelve a lanzar sin RANGO para el resto; reanuda).
set -euo pipefail
n="$1"; estilo="${2:-$(( $(echo -n "$n" | cksum | cut -d' ' -f1) % 6 ))}"
R="$(cd "$(dirname "$0")" && pwd)"; W="$R/trabajo/$n"
mkdir -p "$W"
cp "$R"/motor/*.py "$W"/
cp "$R/escenas/${n}_scene.py" "$R/escenas/${n}_ov.py" "$R/escenas/${n}.txt" "$R/escenas/${n}.mp3" "$W"/
cd "$W"
[ -f "${n}_words.json" ] || python3 align.py "${n}.mp3" "${n}.txt" "$n"
N=$(python3 -c "import json;print(int((json.load(open('${n}_words.json'))['dur']+0.4)*30))")
if [ -n "${RANGO:-}" ]; then python3 "${n}_scene.py" $RANGO; exit 0; fi
have=$(ls frames/$n/*.png 2>/dev/null | wc -l)
[ "$have" -ge "$((N+1))" ] || python3 "${n}_scene.py" 0 "$N"
rm -f frames/anchors_${n}_*_1.json; ANCHORS_ONLY=1 python3 "${n}_scene.py" 0 "$N"
python3 comp.py "$n"
python3 music.py "${n}_final.mp4" "${n}_tiktok_final.mp4" "$estilo" > /dev/null
for v in "${n}_final" "${n}_tiktok_final"; do
  ffmpeg -loglevel error -y -i "$v.mp4" -c:v libx264 -preset medium -crf 25 -pix_fmt yuv420p -c:a copy -movflags +faststart "${v}_c.mp4"
done
ffmpeg -loglevel error -y -i "${n}_final_c.mp4" -vf "fps=1/3,scale=216:384,tile=8x3" -frames:v 1 "${n}_hoja.png"
echo "LISTO $n $(ffprobe -v error -show_entries format=duration -of csv=p=0 ${n}_final_c.mp4)s"
