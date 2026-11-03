# Programador explicadoen60s

Sustituto gratuito de Metricool. GitHub publica solo los vídeos a su hora, sin límite al mes.

- **Calendario:** [`CALENDARIO.md`](../CALENDARIO.md) (se actualiza solo cada 10 minutos).
- **Vídeos:** se guardan en el release [`videos`](https://github.com/explicadoen60s/explicadoen60s.github.io/releases/tag/videos) para no llenar el repositorio.
- **Avisos:** cuando hay que hacer algo (un TikTok listo en tu bandeja o un error), se abre un *issue* y te llega una notificación de GitHub.
- **YouTube e Instagram:** publicación automática.
- **TikTok:** a su hora, el vídeo llega a tu bandeja de TikTok y el aviso trae el texto para pegar. Publicas con un toque. Cuando TikTok apruebe la app, pasará a ser automático.

## Configuración (una sola vez)

### 0. Activar la web del programador, 1 minuto
En el repositorio, ve a **Settings → Pages**:
- En **Build and deployment → Source**, elige **Deploy from a branch**.
- Rama `main`, carpeta `/docs`, y pulsa **Save**.

En un par de minutos estará en <https://explicadoen60s.github.io/>.

Después necesitas crear una «app» en cada red. Es gratis y solo la usas tú. En todas, la dirección de retorno (*redirect URI*) es:

```
https://explicadoen60s.github.io/callback.html
```

### 1. YouTube (Google Cloud), unos 7 minutos
1. Entra en <https://console.cloud.google.com/> con la cuenta del canal y crea un proyecto llamado `explicadoen60s`.
2. En **APIs y servicios → Biblioteca**, busca **YouTube Data API v3** y pulsa **Habilitar**.
3. En **Pantalla de consentimiento de OAuth / Google Auth Platform**:
   - Tipo **Externo**, nombre `Programador explicadoen60s` y tu email.
   - En **Público**, pulsa **Publicar app** (modo producción). Así el permiso no caduca a los 7 días.
4. En **Clientes (Credenciales) → Crear cliente OAuth**:
   - Tipo **Aplicación web**.
   - En «URI de redirección autorizados» pon la dirección de arriba.
   - Guarda el **ID de cliente** y el **Secreto de cliente**.
5. Al conectar verás «Google no ha verificado esta app». Es normal porque es tu propia app: pulsa **Avanzado → Ir a…**.

### 2. Instagram (Meta), unos 10 minutos
Las apps nuevas de Meta obligan a usar un **portfolio comercial**. Se usa un «usuario del sistema» cuyo permiso **no caduca nunca**, así que no hace falta conectar con código. Requisitos: Instagram en modo profesional y **vinculado a una página de Facebook**.
1. En la app de Meta, añade los permisos de **Administrar contenido en Instagram** desde «API de Instagram → Configuración de la API con inicio de sesión con Facebook».
2. En <https://business.facebook.com/settings> (tu portfolio), ve a **Cuentas**:
   - **Páginas:** añade la página de Facebook.
   - **Cuentas de Instagram:** añade @explicadoen60s.
   - **Apps:** comprueba que está la app.
3. En **Usuarios → Usuarios del sistema → Añadir**:
   - Nombre `programador`, rol **Administrador**.
   - Pulsa **Asignar activos** y dale control total de la app, la página y la cuenta de Instagram.
4. Pulsa **Generar identificador**. Elige la app, caducidad **Nunca** y estos permisos: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management`.
5. Copia el identificador y guárdalo en GitHub como secreto `IG_TOKEN`. No hacen falta `IG_APP_ID` ni `IG_APP_SECRET`.

### 3. TikTok, unos 10 minutos (+ revisión de TikTok)
1. Entra en <https://developers.tiktok.com/> y ve a **Manage apps → Connect an app**. Rellena:
   - Nombre: `Programador explicadoen60s`, con icono y descripción.
   - Web: `https://explicadoen60s.github.io/`
   - Términos: `…/terminos.html`; Privacidad: `…/privacidad.html`
2. Añade los productos **Login Kit**, con la dirección de retorno, y **Content Posting API**.
3. Permisos (*scopes*): `user.info.basic` y `video.upload`.
4. Pulsa **Submit for review**. Mientras lo revisan, puedes usar el **Sandbox** añadiendo tu cuenta en *Target users*.
5. Guarda el **Client key** y el **Client secret**.

### 4. Pasar las claves a GitHub
Ponlas en GitHub:
**Settings → Secrets and variables → Actions → New repository secret** con estos nombres:

`CLAVE_TOKENS`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `IG_TOKEN`, `TT_CLIENT_KEY`, `TT_CLIENT_SECRET`

`CLAVE_TOKENS` es una contraseña larga que te inventas (mínimo 20 caracteres) y que no hace falta recordar: cifra los permisos de las cuentas. Si algún día la cambias, tendrás que volver a conectar las tres redes.

Además, el ID de cliente de YouTube, el ID de la app de Instagram y el client key de TikTok van en `docs/conectar.html`. No son secretos.

### 5. Conectar las cuentas
1. Abre <https://explicadoen60s.github.io/conectar.html> y pulsa una red.
2. Acepta los permisos y copia el código que aparece.
3. Ve a **Actions → Conectar red social → Run workflow**, elige la red, pega el código y ejecútalo.

Repite los pasos con las tres redes.

## Panel web
Todo se gestiona desde **<https://explicadoen60s.github.io/>**, también desde el móvil:
- **Calendario:** cambiar hora, publicar ya o quitar.
- **Nuevo vídeo:** subir el vídeo y elegir redes y horas. Propone el siguiente hueco libre.
- **Avisos:** los borradores de TikTok con su texto para copiar, y los errores.
- **Conexiones:** estado de cada red y botón para comprobarlas.

La primera vez pide un *token* de GitHub (fine-grained, solo este repositorio, con permisos Contents, Actions e Issues en lectura y escritura). Se guarda solo en ese navegador.

## Uso diario desde la terminal (lo hace Claude)
```bash
python3 programador/cola.py nuevo termo --mp4 termo.mp4 --mp4-tiktok termo_tiktok.mp4 \
  --titulo "…" --texto "…" --tags "termo,física" \
  --tiktok "2026-11-03 10:00" --instagram "2026-11-05 18:00" --youtube "2026-11-05 16:00"
python3 programador/cola.py lista                          # ver lo programado
python3 programador/cola.py mover termo-youtube "2026-11-06 12:00"
python3 programador/cola.py quitar termo-youtube
git add programador/calendario.json && git commit -m "Programar" && git push
```

Para publicar ya, sin esperar los 10 minutos: **Actions → Publicar vídeos programados → Run workflow**.

## Límites
- **Retraso:** GitHub puede retrasar la ejecución unos minutos en horas punta.
- **Instagram:** tiene un límite diario de publicaciones por API, de sobra para 2 al día.
- **YouTube:** como mucho 100 subidas al día.
