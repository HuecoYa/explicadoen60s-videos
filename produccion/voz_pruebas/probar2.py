"""Pruebas de voz con acento peninsular. Uso: python probar2.py <paso> ..."""
import sys, re, json
TEXTO = ("¿Sabías que un termo puede mantener tu café caliente durante doce horas? "
         "El secreto no es lo que lleva dentro, sino lo que no lleva: nada. "
         "Entre sus dos paredes hay vacío, y sin aire, el calor no tiene por dónde escapar.")
DISENO = ("Hombre joven de España, castellano peninsular de Madrid, pronunciación clara con la ce y la zeta, "
          "tono cercano y natural de divulgador de vídeos cortos, energía media, ritmo ágil.")
paso = sys.argv[1]

def guardar(audio, sr, salida):
    import numpy as np, soundfile as sf
    sf.write(salida, np.asarray(audio, dtype="float32").squeeze(), sr)

if paso == "transcribir":
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(sys.argv[2], language="es")
    t = " ".join(s.text.strip() for s in segs)
    open(sys.argv[3], "w").write(t); print("TRANSCRIPCION:", t)
elif paso in ("qwen_icl", "qwen_xvec"):
    import torch
    from qwen_tts import Qwen3TTSModel
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32)
    ref, salida = sys.argv[2], sys.argv[3]
    if paso == "qwen_icl":
        wavs, sr = m.generate_voice_clone(text=TEXTO, language="Spanish", ref_audio=ref, ref_text=open(sys.argv[4]).read().strip())
    else:
        wavs, sr = m.generate_voice_clone(text=TEXTO, language="Spanish", ref_audio=ref, x_vector_only_mode=True)
    guardar(wavs[0], sr, salida)
elif paso == "qwen_diseno":
    import torch
    from qwen_tts import Qwen3TTSModel
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.float32)
    wavs, sr = m.generate_voice_design(text=TEXTO, language="Spanish", instruct=DISENO)
    guardar(wavs[0], sr, sys.argv[2])
elif paso == "piper":
    import wave
    from piper import PiperVoice
    v = PiperVoice.load(sys.argv[2])
    with wave.open(sys.argv[3], "wb") as wf:
        v.synthesize_wav(TEXTO, wf) if hasattr(v, "synthesize_wav") else v.synthesize(TEXTO, wf)
elif paso == "vc":
    from chatterbox.vc import ChatterboxVC
    m = ChatterboxVC.from_pretrained(device="cpu")
    wav = m.generate(sys.argv[2], target_voice_path=sys.argv[3])
    guardar(wav.cpu().numpy(), m.sr, sys.argv[4])
print("ok", paso)
