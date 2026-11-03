# Directo «¿Qué aguanta más?» · Duelos de objetos

Pantalla 3D para tus directos de TikTok. Dos objetos se enfrentan, el público vota y el más votado va a la prensa hidráulica.
Tú lo explicas en directo con tu voz. El programa hace el resto: cuenta los votos y los regalos, mueve la prensa,
lanza los efectos y muestra quién lo ha mandado a la prensa.

## Cómo se vota
- **Gratis:** escribiendo **A** o **B** en el chat (también vale 1/2 o el nombre del objeto). Es 1 voto y cada persona elige un equipo por duelo.
- **Con regalos:** cada moneda del regalo son **10 votos** para el equipo de quien lo manda. Si aún no ha elegido, sale un aviso
  («escribe A o B para sumar +N») y los votos se suman en cuanto escribe A o B.
- Gana el que tenga más votos: **sin azar, sin sorteos y sin premios**. Si hay empate, se añaden 15 segundos.
- Los regalos de 99 monedas o más lanzan un «¡MEGA REGALO!» con lluvia de monedas.

## Primera vez (10 minutos)
1. Instala **Node.js** (versión LTS) desde https://nodejs.org.
2. Copia la carpeta `directo` a tu ordenador (si ya tienes el repositorio clonado, basta con `git pull`).
3. En `config.json`, comprueba tu usuario de TikTok (`"usuario"`) y, si quieres, los tiempos:
   - `segundos_votacion`: cuánto dura cada votación (120 por defecto).
   - `puntos_por_moneda`: cuántos votos vale cada moneda (10).
   - `automatico`: si es `true`, al acabar un duelo empieza el siguiente solo.
4. Doble clic en **`iniciar.bat`** (Windows) o **`iniciar.command`** (Mac). La primera vez instala lo necesario.

Se abren dos ventanas:
- **La pantalla** (`http://localhost:3060`): es la que capturas en el directo.
- **El control** (`http://localhost:3060/control`): solo la ves tú. Tiene los botones, el marcador y tu **chuleta** con lo que puedes explicar de cada duelo.

## En TikTok LIVE Studio
1. Pon el directo en **vertical**.
2. Añade una fuente:
   - Si tu versión tiene una fuente de tipo **navegador/enlace**, pon `http://localhost:3060` con un tamaño de 1080×1920.
   - Si no, usa **Captura de ventana** y elige la ventana de la pantalla (la de 540×960). Ajústala para que ocupe toda la imagen.
3. Pon tu cámara pequeña en una esquina de arriba o abajo, sin tapar el marcador ni los objetos.
4. Para que se oigan los efectos, activa el **audio del sistema** en LIVE Studio y haz un clic una vez en la ventana de la pantalla:
   los navegadores no dejan sonar nada hasta el primer clic.

El programa se conecta solo cuando empieza tu directo. En el control sale 🟢 cuando ya está leyendo el chat y los regalos.

## Durante el directo
| Botón del control | Tecla en la pantalla | Qué hace |
|---|---|---|
| Empezar / Siguiente duelo | N | Arranca el primer duelo o pasa al siguiente |
| Pausa | Espacio | Para el reloj; los votos no cuentan mientras está en pausa |
| Prensa ya | P | Acaba la votación ahora |
| +30 s / −30 s | ↑ / ↓ | Alarga o acorta la votación |
| Automático | A | Encadena los duelos solo o espera a que pulses |
| Simulador | S | Votos y regalos **falsos** para probar. Nunca lo actives en directo |

Para probar sin estar en directo: `npm run simular` o `iniciar.bat --simular`.

## Cambiar los duelos
Edita `duelos.json`. Cada duelo lleva dos objetos (`modelo` + `nombre`) y tu `nota`.
Objetos disponibles: `huevo`, `bombilla`, `lata`, `botella`, `sandia`, `pelota`, `movil`, `mando`, `tomate`, `donut`, `cubo`, `vela`.
Para añadir objetos nuevos, pídeselo a Claude (están en `pantalla/objetos.js`).

## A tener en cuenta
- Para leer el chat y los regalos se usa una librería **no oficial** (`tiktok-live-connector`) porque TikTok no ofrece una forma oficial.
  Funciona sin tu contraseña, pero si TikTok cambia algo puede dejar de funcionar unos días hasta que la actualicen (`npm update`).
- Para tener regalos en el directo, la cuenta debe cumplir los requisitos de TikTok: ser mayor de edad y tener un mínimo de seguidores.
- Las normas de TikTok exigen que hables tú en directo. El programa no pone voces: la voz eres tú.
- No prometas nada a cambio de regalos fuera de lo que se ve en pantalla.
