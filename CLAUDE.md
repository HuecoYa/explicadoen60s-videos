# explicadoen60s: producción automática de vídeos

Cuenta @explicadoen60s (TikTok, Instagram, YouTube «explicadoen60s_shorts»). Vídeos verticales de ~60-75 s que explican cómo funcionan las cosas, en castellano de España. El dueño revisa y aprueba desde el panel: https://explicadoen60s.github.io/

## Cómo fluye un vídeo (`produccion/estado.json`)
| estado | quién lo mueve | qué significa |
|---|---|---|
| `propuesto` | **Claude** (pasada diaria) | guion propuesto, esperando al usuario |
| `aprobado` | usuario (panel) | la acción «Generar voces» crea `escenas/<id>.mp3` con la voz del dueño (Qwen3-TTS, `produccion/voz.py`) |
| `voz` | GitHub | hay voz; **Claude** debe escribir la escena 3D |
| `escena` | **Claude** | escena escrita y revisada; al hacer push se lanza «Renderizar vídeos» |
| `revision` | GitHub | vídeo en el release `videos`; el usuario lo ve en el panel |
| `rehacer` | usuario | ha pedido cambios en `nota`: **Claude** corrige la escena y vuelve a `escena` |
| `programado` / `rechazado` | usuario | terminado |

Claude **nunca** aprueba vídeos ni los programa: eso lo hace el usuario en el panel.

## Pasada diaria de Claude (por este orden)
1. `git pull`. Lee `produccion/estado.json`.
2. **`rehacer`**: lee `nota`, corrige `escenas/<id>_scene.py` / `_ov.py`, revísalo (ver «Revisar antes de entregar») y ponlo en `escena`. Borra `nota`.
3. **`voz`** (máx. 5 por pasada, los más antiguos primero): escribe `escenas/<id>_scene.py` y `escenas/<id>_ov.py`, revísalos y pon `escena`. Haz un commit y un push por vídeo, para que el render empiece cuanto antes (cada push lanza el render de todos los que están en `escena`).
4. **Propuestas**: que haya siempre unos **8** vídeos entre `propuesto`, `aprobado`, `voz` y `escena`. Añade los que falten como `propuesto`.
5. Si una entrada tiene `error`, intenta resolverlo. Si no puedes (falta un secreto, por ejemplo), déjalo anotado en `error` en palabras sencillas.

## Guiones (propuestas)
Campos de cada entrada nueva en `estado.json`:
- `id`: corto, ASCII y único, por ejemplo `piscina`.
- `formato`: `A`, `B` o `C`.
- `titulo`: hasta 100 caracteres, con emoji.
- `guion`: solo el texto que se locuta.
- `texto`: el pie del post, 1-2 frases que terminen en pregunta o 👇.
- `tags`: 5 temas sin `#`.
- `estado: "propuesto"` y `creado` (la fecha).

Formatos (mezclarlos; uno de cada tres, más o menos):
- **A · «Así funciona»**: un objeto cotidiano en corte (*cutaway*); se ve el mecanismo por dentro y se explica paso a paso. Ejemplos: `cisterna`, `semaforo`, `airbag`.
- **B · «Si tuvieras que inventar…»**: construir el objeto pieza a pieza, cada pieza resuelve un problema. Ejemplos: `termo`, `mechero`, `cremallera`.
- **C · «¿Y si construyes…?»**: construcción grande en corte bajo tierra o en sección. Cada paso crea un problema («pero…») y el siguiente lo soluciona («así que…»). Ejemplos de temas: piscina, rascacielos, túnel bajo un río, pozo, presa.

Reglas del guion:
- **Longitud:** 205-245 palabras (≈60-72 s: la voz va a unas 3,4 palabras por segundo). Escribe con gancho: preguntas, exclamaciones (¡…!) y puntos suspensivos antes de los datos sorprendentes; la puntuación da la entonación.
- **Estilo:** tuteo, vocabulario de España, frases de 6-12 palabras, sin relleno. Números en letra.
- **Estructura:** gancho en la primera frase (dato chocante o pregunta); un dato sorprendente en mitad del vídeo; cierre con «Sígueme para más.».
- **Datos:** comprueba con búsqueda web cada dato técnico, cifra o récord antes de proponerlo.
- **Temas:** no repitas nada que ya esté en `estado.json` ni en `produccion/escenas/`. Nada de casinos ni apuestas, nada de marcas reales en pantalla.

## Escenas 3D (`escenas/<id>_scene.py` + `<id>_ov.py`)
Motor en `produccion/motor/`. Copia los patrones de las escenas existentes: es la mejor documentación.
- **Render:** Blender 5 (`bpy`) con Workbench, estilo 3D estilizado con colores planos y sombras suaves. 1080×1920, 30 fps.
- **Funciones de `lib3d`:**
  - Primitivas: `box`, `cyl`, `sph`, `torus`, `rounded_slab`, `text3d`, `bar_obj`/`bar_set`, `set_color`.
  - Animación: `seg(t,a,b)` (0→1 suavizado), `keyed(t,[(t,v),…])`, `mix`.
  - Cámara: `cam_state(t, CAM, drift)` con claves Catmull-Rom `(t, (pos), (target), lens)` y `apply_cam`.
  - Rendimiento: `join_static(dinamicos)` une todo lo estático para ir más rápido. **Todo lo que se mueve, cambia de color o tiene modificadores (booleanas, solidify) va en la lista de dinámicos**; si no, se pierde.
  - Cortes: modificador SOLIDIFY (interior más claro con `material_offset`) + BOOLEAN DIFFERENCE con un cubo cortador oculto.
  - `run(nombre, build, pose, anchors)` renderiza; `anchors` devuelve puntos 3D proyectados a pantalla para colocar etiquetas.
- **`_ov.py` (capa 2D):** `SUB_Y`, `KEYWORDS` (palabras del subtítulo en amarillo), `overlay(ctx,t,A,C)` y `sfx_events(C)`. Ayudas: `C.badge`, `C.callout`, `C.s_whoosh`, `C.s_pop`, `C.s_thud`, `C.s_clank`, `C.s_win`, `C.s_fail`… El subtítulo de una palabra lo pone `comp.py` solo.
- **Sincronizar con la voz:** `produccion/producir.sh <id>` alinea la voz y crea `trabajo/<id>/<id>_words.json`. Con `python3 trabajo/<id>/phr.py <id>`, ejecutado dentro de esa carpeta, se ven las frases con sus tiempos. Cada acción visual debe coincidir con lo que dice la voz en ese momento.

Calidad que exige el usuario:
- Escenas realistas y con sentido común; el objeto se reconoce a la primera.
- Vídeo continuo, sin imágenes fijas; algo se mueve siempre.
- Un único estilo; texto en pantalla solo para palabras clave o cifras, **sin repetir lo que dice el subtítulo**.
- La cámara nunca atraviesa objetos y lo importante siempre está dentro del encuadre. Respeta las zonas seguras: los 150 px de arriba, los 420 px de abajo y los 140 px de la derecha quedan libres de cosas importantes.
- El primer segundo ya muestra el objeto completo; nada de pantallas vacías.
- No repitas siempre los mismos elementos de un vídeo a otro.

## Revisar antes de entregar (obligatorio)
1. Instala si falta: `pip install --break-system-packages bpy==5.2.3 numpy pycairo`, `ffmpeg`, y las fuentes de `produccion/fuentes/` en `~/.fonts`.
2. Vista previa barata: `RANGO="0 <N> 15" produccion/producir.sh <id>` (un fotograma de cada 15), donde N = duración × 30.
3. Hoja de contactos de `produccion/trabajo/<id>/frames/<id>_prev/*.png` con ffmpeg (`tile`) y **mírala con Read**. Comprueba que se ve lo que dice la voz en cada momento, que nada se sale del encuadre, que la cámara no atraviesa nada y que los cortes muestran el interior.
4. Corrige y repite hasta que esté bien. Solo entonces: `estado: "escena"`, commit y push. `produccion/trabajo/` no se sube (está en `.gitignore`).

## Publicación (no la toques salvo que se pida)
- `programador/` + `.github/workflows/publicar.yml` publican cada 10 min lo que está en `programador/calendario.json`.
- El panel (`docs/index.html`) añade publicaciones al aprobar un vídeo.
- Vídeos: release `videos`. `<id>.mp4` va a Instagram y YouTube; `<id>_tiktok.mp4` (con música) va a TikTok.
- Horario: TikTok 10, 13, 16, 18 y 21 h; Instagram 10 y 18 h; YouTube 12 y 16 h (hora de Madrid).

## Commits
Autor `explicadoen60s <explicadoen60s.cxn@gmail.com>`. Mensajes en español.
