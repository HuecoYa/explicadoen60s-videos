// Directo «Duelos de objetos» de @explicadoen60s.
// Lee los regalos y comentarios de tu directo de TikTok y mueve la pantalla 3D (pantalla/index.html).
// Uso:  node servidor.js            (usa el usuario de config.json)
//       node servidor.js otro_user  (otro usuario)
//       node servidor.js --simular  (sin TikTok: regalos y comentarios de prueba)
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { WebSocketServer } from "ws";

const DIR = path.dirname(fileURLToPath(import.meta.url));
const CONFIG = JSON.parse(fs.readFileSync(path.join(DIR, "config.json"), "utf8"));
if (process.env.VOTACION) CONFIG.segundos_votacion = +process.env.VOTACION;   // para pruebas
const DUELOS = JSON.parse(fs.readFileSync(path.join(DIR, "duelos.json"), "utf8")).duelos;
const args = process.argv.slice(2);
let simular = args.includes("--simular");
const usuarioTikTok = (args.find(a => !a.startsWith("--")) || CONFIG.usuario || "").replace(/^@/, "");
const PUERTO = CONFIG.puerto || 3060;
const MINIMO = CONFIG.minimo_espectadores ?? 10;

// registro en archivo (registro.txt) para poder ver qué pasó si algo falla en el directo
const REG = path.join(DIR, "registro.txt");
try { if (fs.existsSync(REG) && fs.statSync(REG).size > 2e6) fs.renameSync(REG, REG + ".antiguo"); } catch {}
const logOrig = console.log;
console.log = (...a) => { logOrig(...a); try { fs.appendFileSync(REG, `[${new Date().toLocaleString("es-ES")}] ${a.join(" ")}\n`); } catch {} };
process.on("uncaughtException", e => console.log("ERROR:", e?.stack || e));
process.on("unhandledRejection", e => console.log("ERROR (promesa):", e?.stack || e));

// ───────────── Estado del duelo (aquí manda el servidor; la pantalla solo lo dibuja) ─────────────
const S = {
  fase: "espera",          // espera → votacion → prensa → resultado → (siguiente duelo)
  indice: (+process.env.INICIO || 0) - 1, numero: 0, duelo: null,   // INICIO: para pruebas
  puntos: { a: 0, b: 0 },
  fin: 0,                  // hora (ms) a la que acaba la fase actual
  pausa: false, restante: 0,
  aplastado: null,         // "a" o "b"
  apoyos: {},              // usuario → { nombre, foto, lado, puntos }
  pendientes: {},          // usuario → { nombre, foto, puntos } (regaló antes de elegir equipo)
  auto: CONFIG.automatico !== false,
  simulacion: simular,
  conectado: false, mensaje: "",
  espectadores: null,      // gente viendo el directo ahora (lo manda TikTok)
  relleno: false,          // true = se ven vídeos del canal hasta que haya MINIMO espectadores
  rellenoActivo: CONFIG.relleno !== false,
  pausaPorRelleno: false,
};

const clientes = new Set();
function enviar(obj) { const s = JSON.stringify(obj); for (const c of clientes) if (c.readyState === 1) c.send(s); }
function top(lado, n = 3) {
  return Object.entries(S.apoyos).filter(([, v]) => v.lado === lado && v.puntos > 0)
    .sort((x, y) => y[1].puntos - x[1].puntos).slice(0, n).map(([u, v]) => ({ usuario: u, nombre: v.nombre, foto: v.foto, puntos: v.puntos }));
}
function estado() {
  return { tipo: "estado", fase: S.fase, numero: S.numero, duelo: S.duelo, puntos: S.puntos, fin: S.fin, ahora: Date.now(),
    pausa: S.pausa, restante: S.restante, aplastado: S.aplastado, top: { a: top("a"), b: top("b") }, auto: S.auto,
    simulacion: S.simulacion, conectado: S.conectado, mensaje: S.mensaje, usuario: usuarioTikTok,
    espectadores: S.espectadores, minimo: MINIMO, relleno: S.relleno, rellenoActivo: S.rellenoActivo,
    reglas: { comentario: CONFIG.puntos_comentario, moneda: CONFIG.puntos_por_moneda, prensa: CONFIG.segundos_prensa } };
}
const publicar = () => enviar(estado());

function siguienteDuelo() {
  S.indice = (S.indice + 1) % DUELOS.length; S.numero++;
  S.duelo = DUELOS[S.indice]; S.puntos = { a: 0, b: 0 }; S.apoyos = {}; S.pendientes = {}; S.aplastado = null;
  S.fase = "votacion"; S.pausa = false; S.fin = Date.now() + CONFIG.segundos_votacion * 1000;
  console.log(`\n▶ Duelo ${S.numero}: ${S.duelo.a.nombre} vs ${S.duelo.b.nombre}`);
  publicar();
}
function aPrensa() {
  const { a, b } = S.puntos;
  if (a === b) { // empate: 15 s más (sin azar)
    S.fin = Date.now() + 15000; S.mensaje = a === 0 ? "¡Nadie ha votado! Escribe A o B" : "¡EMPATE! 15 segundos más"; publicar();
    setTimeout(() => { S.mensaje = ""; publicar(); }, 4000); return;
  }
  S.aplastado = a > b ? "a" : "b"; S.fase = "prensa"; S.fin = Date.now() + CONFIG.segundos_prensa * 1000;
  console.log(`  ⬇ A la prensa: ${S.duelo[S.aplastado].nombre} (${a} – ${b})`);
  publicar();
}
function aResultado() { S.fase = "resultado"; S.fin = Date.now() + CONFIG.segundos_resultado * 1000; publicar(); }

setInterval(() => {
  if (S.pausa || S.fase === "espera" || Date.now() < S.fin) return;
  if (S.fase === "votacion") aPrensa();
  else if (S.fase === "prensa") aResultado();
  else if (S.fase === "resultado") { if (S.auto && !S.relleno) siguienteDuelo(); else { S.fase = "espera"; publicar(); } }
}, 250);

// ───────────── Relleno: vídeos del canal mientras haya menos de MINIMO espectadores ─────────────
let pocosDesde = 0;
function ponerRelleno(on) {
  if (S.relleno === on) return;
  S.relleno = on; console.log(on ? `📺 Relleno: hay ${S.espectadores} espectadores (mínimo ${MINIMO})` : `🎮 Volvemos al duelo (${S.espectadores} espectadores)`);
  if (on && S.fase === "votacion" && !S.pausa) { S.restante = Math.max(15000, S.fin - Date.now()); S.pausa = true; S.pausaPorRelleno = true; }
  if (!on) {
    if (S.pausaPorRelleno) { S.fin = Date.now() + S.restante; S.pausa = false; S.pausaPorRelleno = false; }
    else if (S.fase === "espera" && S.numero > 0 && S.auto) siguienteDuelo();
  }
  publicar();
}
setInterval(() => {
  const n = S.espectadores;
  const pocos = S.rellenoActivo && !S.simulacion && S.conectado && n !== null && n < MINIMO;
  if (pocos) { if (!pocosDesde) pocosDesde = Date.now(); if (Date.now() - pocosDesde > 15000) ponerRelleno(true); }
  else { pocosDesde = 0; ponerRelleno(false); }
}, 1000);
function espectadores(n) { if (n !== S.espectadores) { S.espectadores = n; publicar(); } }

// ───────────── Votos y regalos ─────────────
function ladoDeTexto(t) {
  const s = (t || "").trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  if (!S.duelo) return null;
  if (/^(a|1|equipo a|team a)[!. ]*$/.test(s)) return "a";
  if (/^(b|2|equipo b|team b)[!. ]*$/.test(s)) return "b";
  const na = S.duelo.a.nombre.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  const nb = S.duelo.b.nombre.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  if (s === na) return "a"; if (s === nb) return "b";
  return null;
}
function comentario(usuario, nombre, foto, texto) {
  if (S.fase !== "votacion" || S.pausa) return;
  const lado = ladoDeTexto(texto); if (!lado) return;
  const ap = S.apoyos[usuario];
  if (ap && ap.lado) return;                       // un equipo por persona y duelo
  S.apoyos[usuario] = { nombre, foto, lado, puntos: CONFIG.puntos_comentario };
  S.puntos[lado] += CONFIG.puntos_comentario;
  const pend = S.pendientes[usuario];
  if (pend) { S.apoyos[usuario].puntos += pend.puntos; S.puntos[lado] += pend.puntos; delete S.pendientes[usuario]; }
  enviar({ tipo: "voto", usuario, nombre, foto, lado, puntos: CONFIG.puntos_comentario + (pend ? pend.puntos : 0) });
  publicar();
}
function regalo(usuario, nombre, foto, nombreRegalo, monedas, imagen) {
  const puntos = Math.max(1, monedas) * CONFIG.puntos_por_moneda;
  console.log(`  🎁 ${nombre}: ${nombreRegalo} (${monedas} monedas)`);
  if (S.fase !== "votacion" || S.pausa) {        // fuera de la votación: solo el efecto en pantalla
    enviar({ tipo: "regalo", usuario, nombre, foto, regalo: nombreRegalo, imagen, monedas, lado: null, puntos: 0, cuenta: false }); return;
  }
  const ap = S.apoyos[usuario];
  if (ap && ap.lado) { ap.puntos += puntos; S.puntos[ap.lado] += puntos; }
  else { const p = S.pendientes[usuario] || { nombre, foto, puntos: 0 }; p.puntos += puntos; S.pendientes[usuario] = p; }
  enviar({ tipo: "regalo", usuario, nombre, foto, regalo: nombreRegalo, imagen, monedas, lado: ap?.lado || null, puntos, cuenta: true });
  publicar();
}

// ───────────── Conexión con TikTok ─────────────
async function conectarTikTok() {
  if (!usuarioTikTok) { S.mensaje = "Pon tu usuario en config.json"; publicar(); return; }
  if ((CONFIG.modo || "navegador") === "navegador") {
    // Modo gratis: lee el directo desde una ventana de Edge/Chrome (sin servicios de pago)
    const { leerConNavegador } = await import("./lector-navegador.js");
    let antes = null;
    return leerConNavegador({
      usuario: usuarioTikTok, carpeta: DIR,
      alComentario: (u, texto) => comentario(u.id, u.nombre, u.foto, texto),
      alRegalo: (u, nombre, monedas, img) => regalo(u.id, u.nombre, u.foto, nombre, monedas, img),
      alSeguidor: u => enviar({ tipo: "seguidor", nombre: u.nombre }),
      alEspectadores: espectadores,
      alEstado: (ok, msg) => {
        if (S.simulacion) return;
        if (ok !== antes) console.log(ok ? `✔ Leyendo el directo de @${usuarioTikTok}` : `… ${msg}`);
        antes = ok; if (S.conectado !== ok || S.mensaje !== msg) { S.conectado = ok; S.mensaje = msg; publicar(); }
      },
    });
  }
  // Modo «libreria»: conexión directa con tiktok-live-connector (puede pedir plan de pago a su servidor de firmas)
  const { TikTokLiveConnection, WebcastEvent } = await import("tiktok-live-connector");
  const con = new TikTokLiveConnection(usuarioTikTok, { enableExtendedGiftInfo: false });
  const usr = d => ({ id: d.user?.displayId || d.user?.uniqueId || "anonimo", nombre: d.user?.nickname || d.user?.displayId || d.user?.uniqueId || "alguien",
    foto: d.user?.avatarThumb?.urlList?.[0] || d.user?.profilePicture?.url?.[0] || "" });
  con.on(WebcastEvent.CHAT, d => { const u = usr(d); comentario(u.id, u.nombre, u.foto, d.content ?? d.comment ?? ""); });
  con.on(WebcastEvent.GIFT, d => {
    const det = d.gift || d.giftDetails || {};
    if ((det.combo === true || (det.type ?? det.giftType) === 1) && !d.repeatEnd) return;   // racha en curso: se cuenta al terminar
    const u = usr(d);
    const unit = Number(det.diamondCount ?? 1) || 1;
    const img = det.image?.urlList?.[0] || det.giftImage?.url?.[0] || "";
    regalo(u.id, u.nombre, u.foto, det.name || det.giftName || "Regalo", unit * (Number(d.repeatCount) || 1), img);
  });
  con.on(WebcastEvent.FOLLOW, d => { const u = usr(d); enviar({ tipo: "seguidor", nombre: u.nombre }); });
  con.on(WebcastEvent.STREAM_END, () => { S.conectado = false; S.mensaje = "El directo ha terminado"; publicar(); });
  const intentar = async () => {
    try {
      const st = await con.connect(); S.conectado = true; S.mensaje = "";
      console.log(`✔ Conectado al directo de @${usuarioTikTok} (sala ${st.roomId})`); publicar();
    } catch (e) {
      S.conectado = false; S.mensaje = "Esperando a que empiece tu directo…"; publicar();
      console.log(`… No hay directo de @${usuarioTikTok} todavía (${e.message || e}). Reintento en 15 s.`);
      setTimeout(intentar, 15000);
    }
  };
  con.on("disconnected", () => { if (!S.simulacion) { S.conectado = false; publicar(); setTimeout(intentar, 5000); } });
  intentar();
}

// ───────────── Simulador (solo para probar sin directo) ─────────────
const NOMBRES = ["lucia_99", "marcos.gm", "Ana Tech", "pablito", "Sara🌸", "DaniGamer", "nerea", "jorge_r", "Irene", "Toni"];
const REGALOS = [["Rosa", 1], ["Rosa", 1], ["Corazón", 5], ["Dedo", 1], ["Gafas", 99], ["Corona", 199], ["Universo", 500], ["Rosa", 1]];
let tSim = null;
function simulador(on) {
  S.simulacion = on; clearInterval(tSim); publicar();
  if (!on) return;
  let k = 0;
  tSim = setInterval(() => {
    k++; const u = NOMBRES[k * 7 % NOMBRES.length];
    if (k % 3) comentario(u, u, "", ["A", "B", "a", "2", "1"][k % 5]);
    else { const [g, m] = REGALOS[k % REGALOS.length]; regalo(u, u, "", g, m, ""); }
  }, 900);
}

// ───────────── Web: pantalla + órdenes del teclado ─────────────
const TIPOS = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".ttf": "font/ttf", ".json": "application/json", ".png": "image/png" };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0]);
  let f;
  let base = path.join(DIR, "pantalla");
  if (p === "/" || p === "/index.html") f = path.join(DIR, "pantalla", "index.html");
  else if (p === "/control") f = path.join(DIR, "pantalla", "control.html");
  else if (p === "/duelos.json") { f = path.join(DIR, "duelos.json"); base = DIR; }
  else if (p.startsWith("/three/")) { base = path.join(DIR, "node_modules", "three"); f = path.join(base, p.slice(7)); }
  else f = path.join(DIR, "pantalla", p);
  if (!path.resolve(f).startsWith(base) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end("No encontrado"); return; }
  res.writeHead(200, { "Content-Type": TIPOS[path.extname(f)] || "application/octet-stream", "Cache-Control": "no-store" });
  fs.createReadStream(f).pipe(res);
});
const wss = new WebSocketServer({ server, path: "/eventos" });
wss.on("connection", ws => {
  clientes.add(ws); ws.send(JSON.stringify(estado()));
  ws.on("close", () => clientes.delete(ws));
  ws.on("message", m => {
    let o; try { o = JSON.parse(m); } catch { return; }
    switch (o.orden) {
      case "empezar": case "siguiente": siguienteDuelo(); break;
      case "pausa":
        if (!S.pausa) { S.restante = Math.max(0, S.fin - Date.now()); S.pausa = true; }
        else { S.fin = Date.now() + S.restante; S.pausa = false; }
        publicar(); break;
      case "prensa": if (S.fase === "votacion") aPrensa(); break;
      case "mas": if (S.fase === "votacion") { S.fin += 30000; publicar(); } break;
      case "menos": if (S.fase === "votacion") { S.fin = Math.max(Date.now() + 5000, S.fin - 30000); publicar(); } break;
      case "auto": S.auto = !S.auto; publicar(); break;
      case "simular": simulador(!S.simulacion); break;
      case "relleno": S.rellenoActivo = !S.rellenoActivo; if (!S.rellenoActivo) ponerRelleno(false); publicar(); break;
    }
  });
});
server.listen(PUERTO, () => {
  console.log(`\n  Pantalla del directo: http://localhost:${PUERTO}\n`);
  if (process.env.PRUEBA_ESPECTADORES) { S.conectado = true; S.espectadores = +process.env.PRUEBA_ESPECTADORES; return; }   // solo para pruebas
  if (simular) simulador(true); else conectarTikTok();
});
