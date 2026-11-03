"""Genera la misma frase con varios motores de voz libres para compararlos. Uso: python probar.py <motor> <salida.wav>"""
import sys, wave, re
TEXTO = ("¿Sabías que un termo puede mantener tu café caliente durante doce horas? "
         "El secreto no es lo que lleva dentro, sino lo que no lleva: nada. "
         "Entre sus dos paredes hay vacío, y sin aire, el calor no tiene por dónde escapar.")
motor, salida = sys.argv[1], sys.argv[2]

def guardar(audio, sr):
    import numpy as np, soundfile as sf
    sf.write(salida, np.asarray(audio, dtype="float32"), sr)

if motor.startswith("piper"):
    from piper import PiperVoice
    v = PiperVoice.load(sys.argv[3])
    with wave.open(salida, "wb") as wf:
        if hasattr(v, "synthesize_wav"): v.synthesize_wav(TEXTO, wf)
        else: v.synthesize(TEXTO, wf)
elif motor.startswith("kokoro"):
    import numpy as np
    from kokoro import KPipeline
    p = KPipeline(lang_code="e")
    voz = sys.argv[3]
    guardar(np.concatenate([np.asarray(a) for _, _, a in p(TEXTO, voice=voz, speed=1.0)]), 24000)
elif motor == "chatterbox":
    import torch, numpy as np
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    partes = [s for s in re.split(r"(?<=[.?!:])\s+", TEXTO) if s]
    audio = np.concatenate([m.generate(s, language_id="es").squeeze().cpu().numpy() for s in partes])
    guardar(audio, m.sr)
elif motor == "qwen":
    import torch
    from qwen_tts import Qwen3TTSModel
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.float32)
    wavs, sr = m.generate_voice_design(text=TEXTO, language="Spanish",
        instruct="Voz masculina joven de España, castellano peninsular con acento de Madrid, cálida, segura y enérgica, como un divulgador de vídeos cortos.")
    guardar(wavs[0], sr)
print("ok", motor)
