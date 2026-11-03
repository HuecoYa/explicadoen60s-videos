"""Pruebas de voz expresiva («adictiva») manteniendo el timbre del dueño. Uso: python probar3.py <variante> <salida.wav>"""
import sys, re
import numpy as np, soundfile as sf
TEXTO = ("¿Sabías que un termo puede mantener tu café caliente… ¡durante doce horas! "
         "El secreto no es lo que lleva dentro. ¡Es lo que no lleva! Nada. "
         "Entre sus dos paredes hay vacío. Y sin aire… el calor no tiene por dónde escapar. ¿A que no te lo esperabas?")
REF_TXT = ("¿Sabías que para adelantar a un camión pasas 22 segundos en el carril contrario? Y antes de abrirte tienes que ver más de un "
           "kilómetro de carretera vacía, porque le tienes que ganar unos 60 metros, tu hueco detrás, el camión, tu coche y otro hueco delante para volver.")
INSTR = ("Narrador joven de España, castellano peninsular, muy expresivo y enérgico, como un creador de TikTok que engancha: "
         "enfatiza las palabras clave, sube y baja la entonación, hace pausas dramáticas antes de los datos sorprendentes y suena entusiasmado.")
var, salida = sys.argv[1], sys.argv[2]
frases = [f for f in re.split(r"(?<=[.?!…])\s+", TEXTO) if f]

def qwen(nombre):
    import torch
    from qwen_tts import Qwen3TTSModel
    return Qwen3TTSModel.from_pretrained(nombre, device_map="cpu", dtype=torch.float32)

def juntar(trozos, sr, pausa=0.12):
    out = []
    for a in trozos:
        out += [np.asarray(a, dtype="float32").squeeze(), np.zeros(int(pausa * sr), dtype="float32")]
    return np.concatenate(out[:-1])

if var in ("xvec_t11", "xvec_t125"):
    m = qwen("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    p = m.create_voice_clone_prompt(ref_audio=sys.argv[3], x_vector_only_mode=True)
    t, tp = (1.1, 1.0) if var == "xvec_t11" else (1.25, 0.95)
    tr = []
    for f in frases:
        w, sr = m.generate_voice_clone(text=f, language="Spanish", voice_clone_prompt=p, temperature=t, top_p=tp, subtalker_temperature=t)
        tr.append(w[0])
    sf.write(salida, juntar(tr, sr), sr)
elif var == "icl":
    m = qwen("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    p = m.create_voice_clone_prompt(ref_audio=sys.argv[3], ref_text=REF_TXT, x_vector_only_mode=False)
    w, sr = m.generate_voice_clone(text=TEXTO, language="Spanish", voice_clone_prompt=p, temperature=1.0)
    sf.write(salida, np.asarray(w[0]).squeeze(), sr)
elif var == "diseno":
    m = qwen("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
    w, sr = m.generate_voice_design(text=TEXTO, language="Spanish", instruct=INSTR)
    sf.write(salida, np.asarray(w[0]).squeeze(), sr)
elif var == "vc":
    from chatterbox.vc import ChatterboxVC
    m = ChatterboxVC.from_pretrained(device="cpu")
    w = m.generate(sys.argv[3], target_voice_path=sys.argv[4])  # salida=argv[2], origen=argv[3], objetivo=argv[4]
    sf.write(salida, w.cpu().numpy().squeeze(), m.sr)
print("ok", var)
