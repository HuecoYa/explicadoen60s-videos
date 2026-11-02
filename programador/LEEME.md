# Programador explicadoen60s

Sustituto gratuito de Metricool. GitHub publica solo los vídeos a su hora, sin límite al mes.

- **Calendario:** [`CALENDARIO.md`](../CALENDARIO.md) (se actualiza solo cada 10 minutos).
- **Vídeos:** se guardan en el release [`videos`](https://github.com/HuecoYa/explicadoen60s-videos/releases/tag/videos) para no llenar el repositorio.
- **Avisos:** cuando hay que hacer algo (un TikTok listo en tu bandeja o un error), se abre un *issue* y te llega una notificación de GitHub.
- **YouTube e Instagram:** publicación automática.
- **TikTok:** a su hora, el vídeo llega a tu bandeja de TikTok y el aviso trae el texto para pegar. Publicas con un toque. Cuando TikTok apruebe la app, pasará a ser automático.

## Configuración (una sola vez)

Necesitas crear una «app» en cada red. Es gratis y solo la usas tú. En todas, la dirección de retorno (*redirect URI*) es:

```
https://huecoya.github.io/explicadoen60s-videos/callback.html
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

### 2. Instagram (Meta), unos 7 minutos
Tu Instagram tiene que ser cuenta **profesional** (Creador o Empresa). No hace falta página de Facebook.
1. Entra en <https://developers.facebook.com/apps> y pulsa **Crear app**:
   - Caso de uso: **Administrar mensajes y contenido en Instagram**.
   - Nombre: `Programador explicadoen60s`.
2. En el caso de uso de Instagram, ve a **API con inicio de sesión de Instagram**:
   - En **Configurar inicio de sesión de la empresa**, añade la dirección de retorno.
   - Guarda el **ID de la app de Instagram** y la **Clave secreta de la app de Instagram**. No son los de Facebook.
3. En **Roles de la app → Roles → Evaluadores de Instagram**, añade tu cuenta.
4. Acepta la invitación en Instagram: **Configuración → Apps y sitios web → Invitaciones de evaluador**.

### 3. TikTok, unos 10 minutos (+ revisión de TikTok)
1. Entra en <https://developers.tiktok.com/> y ve a **Manage apps → Connect an app**. Rellena:
   - Nombre: `Programador explicadoen60s`, con icono y descripción.
   - Web: `https://huecoya.github.io/explicadoen60s-videos/`
   - Términos: `…/terminos.html`; Privacidad: `…/privacidad.html`
2. Añade los productos **Login Kit**, con la dirección de retorno, y **Content Posting API**.
3. Permisos (*scopes*): `user.info.basic` y `video.upload`.
4. Pulsa **Submit for review**. Mientras lo revisan, puedes usar el **Sandbox** añadiendo tu cuenta en *Target users*.
5. Guarda el **Client key** y el **Client secret**.

### 4. Pasar las claves a GitHub
Ponlas en GitHub:
**Settings → Secrets and variables → Actions → New repository secret** con estos nombres:

`CLAVE_TOKENS`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `IG_APP_ID`, `IG_APP_SECRET`, `TT_CLIENT_KEY`, `TT_CLIENT_SECRET`

`CLAVE_TOKENS` es una contraseña larga que te inventas (mínimo 20 caracteres) y que no hace falta recordar: cifra los permisos de las cuentas. Si algún día la cambias, tendrás que volver a conectar las tres redes.

Además, el ID de cliente de YouTube, el ID de la app de Instagram y el client key de TikTok van en `docs/conectar.html`. No son secretos.

### 5. Conectar las cuentas
1. Abre <https://huecoya.github.io/explicadoen60s-videos/conectar.html> y pulsa una red.
2. Acepta los permisos y copia el código que aparece.
3. Ve a **Actions → Conectar red social → Run workflow**, elige la red, pega el código y ejecútalo.

Repite los pasos con las tres redes.

## Uso diario (lo hace Claude)
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
