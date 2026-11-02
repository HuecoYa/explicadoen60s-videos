"""Conecta una red: cambia el código de autorización por tokens y los guarda cifrados.
Uso (lo ejecuta el workflow «Conectar red»):  python conectar.py <youtube|instagram|tiktok> <codigo>"""
import sys

from comun import leer_tokens, guardar_tokens
from redes import REDES

red, codigo = sys.argv[1], sys.argv[2].strip()
tokens = leer_tokens()
tokens[red] = REDES[red].conectar(codigo)
guardar_tokens(tokens)
extra = tokens[red].get("usuario") or ""
print(f"✅ {red} conectado {extra}".strip())
