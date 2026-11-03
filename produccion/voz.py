"""Genera la voz de un guion con ElevenLabs (voz «Jaime») y la deja lista para el montaje.

Uso:  python3 produccion/voz.py <nombre>
Lee   produccion/escenas/<nombre>.txt   (guion limpio, solo el texto que se locuta)
Crea  produccion/escenas/<nombre>.mp3

Necesita la variable ELEVENLABS_API_KEY (en GitHub: secreto con ese nombre).
Opcionales: ELEVEN_VOICE_ID (si no, busca una voz llamada «Jaime» en tu cuenta) y ELEVEN_MODEL.
Ajustes por defecto copiados de los audios del usuario: velocidad 0,95, estabilidad 0,42, similitud 0,62.
"""
import os, sys, json
from pathlib import Path

import requests

API = "https://api.elevenlabs.io/v1"
AJUSTES = {"stability": 0.42, "similarity_boost": 0.62, "speed": 0.95}
MODELOS_PREFERIDOS = ["eleven_v4", "eleven_multilingual_v2"]
ESCENAS = Path(__file__).resolve().parent / "escenas"


def _h():
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not k:
        sys.exit("Falta ELEVENLABS_API_KEY")
    return {"xi-api-key": k}


def voz_id():
    if os.environ.get("ELEVEN_VOICE_ID"):
        return os.environ["ELEVEN_VOICE_ID"].strip()
    r = requests.get(f"{API}/voices", headers=_h(), timeout=60)
    r.raise_for_status()
    for v in r.json().get("voices", []):
        if "jaime" in v.get("name", "").lower():
            return v["voice_id"]
    sys.exit("No encuentro la voz «Jaime» en tu cuenta de ElevenLabs: añádela a «Mis voces» o pon ELEVEN_VOICE_ID")


def modelo():
    if os.environ.get("ELEVEN_MODEL"):
        return os.environ["ELEVEN_MODEL"].strip()
    try:
        r = requests.get(f"{API}/models", headers=_h(), timeout=60)
        ids = {m["model_id"] for m in r.json() if m.get("can_do_text_to_speech", True)}
        for m in MODELOS_PREFERIDOS:
            if m in ids:
                return m
    except Exception:
        pass
    return MODELOS_PREFERIDOS[-1]


def generar(nombre):
    texto = (ESCENAS / f"{nombre}.txt").read_text(encoding="utf-8").strip()
    vid, mod = voz_id(), modelo()
    cuerpo = {"text": texto, "model_id": mod, "voice_settings": AJUSTES, "language_code": "es"}
    r = requests.post(f"{API}/text-to-speech/{vid}?output_format=mp3_44100_128", headers=_h(), json=cuerpo, timeout=300)
    if r.status_code == 400 and "language_code" in r.text:  # algunos modelos no aceptan language_code
        cuerpo.pop("language_code")
        r = requests.post(f"{API}/text-to-speech/{vid}?output_format=mp3_44100_128", headers=_h(), json=cuerpo, timeout=300)
    if r.status_code >= 400:
        sys.exit(f"ElevenLabs {r.status_code}: {r.text[:300]}")
    salida = ESCENAS / f"{nombre}.mp3"
    salida.write_bytes(r.content)
    print(json.dumps({"voz": nombre, "modelo": mod, "bytes": len(r.content)}, ensure_ascii=False))
    return salida


if __name__ == "__main__":
    for n in sys.argv[1:]:
        generar(n)
