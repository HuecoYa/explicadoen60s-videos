"""Genera la voz de un guion con la voz del dueño del canal (clon de timbre con Qwen3-TTS, gratis y local).

Uso:  python3 produccion/voz.py <nombre> [<nombre> …]
Lee   produccion/escenas/<nombre>.txt   (solo el texto que se locuta)
Crea  produccion/escenas/<nombre>.mp3

Referencia de la voz: produccion/voz/referencia_larga.wav (40 s de la voz del dueño).
Modo «x-vector»: copia el timbre, y el modelo pone una pronunciación de castellano natural.
"""
import re, subprocess, sys, tempfile
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent
ESCENAS = RAIZ / "escenas"
REF = RAIZ / "voz" / "referencia_larga.wav"
MODELO = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
PAUSA = 0.22          # segundos de silencio entre trozos
MAX_CHARS = 260       # tamaño de cada trozo (frases completas)

_modelo = _prompt = None


def _cargar():
    global _modelo, _prompt
    if _modelo is None:
        import torch
        from qwen_tts import Qwen3TTSModel
        torch.set_num_threads(max(1, (torch.get_num_threads())))
        _modelo = Qwen3TTSModel.from_pretrained(MODELO, device_map="cpu", dtype=torch.float32)
        _prompt = _modelo.create_voice_clone_prompt(ref_audio=str(REF), x_vector_only_mode=True)
    return _modelo, _prompt


def trozos(texto):
    frases = [f.strip() for f in re.split(r"(?<=[.?!…:])\s+", texto.strip()) if f.strip()]
    out, actual = [], ""
    for f in frases:
        if actual and len(actual) + len(f) + 1 > MAX_CHARS:
            out.append(actual); actual = f
        else:
            actual = f"{actual} {f}".strip()
    if actual:
        out.append(actual)
    return out


def generar(nombre):
    texto = (ESCENAS / f"{nombre}.txt").read_text(encoding="utf-8").strip()
    m, prompt = _cargar()
    partes, sr = [], 24000
    for t in trozos(texto):
        wavs, sr = m.generate_voice_clone(text=t, language="Spanish", voice_clone_prompt=prompt)
        a = np.asarray(wavs[0], dtype="float32").squeeze()
        partes += [a, np.zeros(int(PAUSA * sr), dtype="float32")]
    audio = np.concatenate(partes[:-1])
    import soundfile as sf
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sf.write(tmp.name, audio, sr)
        salida = ESCENAS / f"{nombre}.mp3"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp.name, "-af", "loudnorm=I=-16:TP=-1.5",
                        "-ar", "44100", "-b:a", "160k", str(salida)], check=True)
    print(f"voz {nombre}: {len(audio) / sr:.1f} s")
    return salida


if __name__ == "__main__":
    for n in sys.argv[1:]:
        generar(n)
