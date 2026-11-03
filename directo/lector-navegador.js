// Lector GRATIS del directo: abre tu directo en Edge o Chrome (el navegador que ya tienes) y escucha los mismos
// mensajes que recibe la página de TikTok (comentarios, regalos, seguidores). No usa servidores de pago ni claves.
// Los mensajes llegan en el formato interno de TikTok y se traducen con el decodificador de «tiktok-live-connector».
import path from "node:path";
import { deserializeWebSocketMessage, deserializeMessage } from "tiktok-live-connector";

export async function leerConNavegador({ usuario, carpeta, alComentario, alRegalo, alSeguidor, alEstado }) {
  let chromium;
  try { ({ chromium } = await import("playwright-core")); }
  catch { alEstado(false, "Falta instalar: abre iniciar.bat otra vez"); return; }

  const perfil = path.join(carpeta, ".perfil-navegador");   // así TikTok recuerda la sesión si inicias sesión una vez
  let ctx = null;
  for (const channel of ["msedge", "chrome"]) {
    try {
      ctx = await chromium.launchPersistentContext(perfil, {
        ...(process.env.LECTOR_CHROME ? { executablePath: process.env.LECTOR_CHROME } : { channel }),   // LECTOR_CHROME: solo para pruebas
        headless: !!process.env.LECTOR_OCULTO, viewport: { width: 420, height: 760 },
        args: ["--mute-audio", "--window-size=440,820", "--window-position=0,0", "--autoplay-policy=no-user-gesture-required"],
      });
      console.log(`✔ Lector abierto con ${channel === "msedge" ? "Microsoft Edge" : "Google Chrome"}`);
      break;
    } catch (e) { console.log(`  (no se pudo abrir ${channel}: ${String(e.message).split("\n")[0]})`); }
  }
  if (!ctx) { alEstado(false, "No encuentro Edge ni Chrome en este ordenador"); return; }

  const page = ctx.pages()[0] || await ctx.newPage();
  const vistos = new Set();
  let ultimo = 0;

  function tratar(lista) {
    for (const m of lista || []) {
      const d = m.decodedData; if (!d) continue;
      const id = String(m.msgId || d.data?.common?.msgId || "");
      if (id) { if (vistos.has(id)) continue; vistos.add(id); if (vistos.size > 5000) vistos.clear(); }
      ultimo = Date.now();
      const x = d.data || {};
      const u = x.user || {};
      const quien = { id: u.displayId || u.uniqueId || String(u.id || u.userId || "anonimo"), nombre: u.nickname || u.displayId || u.uniqueId || "alguien",
        foto: u.avatarThumb?.urlList?.[0] || u.profilePicture?.url?.[0] || "" };
      if (d.type === "WebcastChatMessage") alComentario(quien, x.content ?? x.comment ?? "");
      else if (d.type === "WebcastGiftMessage") {
        const det = x.gift || x.giftDetails || {};
        const racha = det.combo === true || (det.type ?? det.giftType) === 1;
        if (racha && !x.repeatEnd) continue;                 // racha en curso: se cuenta una vez, al terminar
        const unidad = Number(det.diamondCount ?? 1) || 1;
        alRegalo(quien, det.name || det.giftName || "Regalo", unidad * (Number(x.repeatCount || x.comboCount) || 1), det.image?.urlList?.[0] || det.giftImage?.url?.[0] || "");
      } else if (d.type === "WebcastSocialMessage") {
        if (String(x.action) === "1" || String(x.common?.displayText?.key || "").includes("follow")) alSeguidor(quien);
      }
    }
  }

  // 1) mensajes por WebSocket (lo normal en el directo)
  const cdp = await ctx.newCDPSession(page);
  await cdp.send("Network.enable");
  cdp.on("Network.webSocketFrameReceived", async ({ response }) => {
    if (response.opcode !== 2) return;                      // solo binarios
    try { const f = await deserializeWebSocketMessage(Buffer.from(response.payloadData, "base64")); tratar(f.protoMessageFetchResult?.messages); } catch {}
  });
  // 2) mensajes por consulta HTTP (la página lo usa al cargar y cuando el WebSocket falla)
  page.on("response", async r => {
    if (!r.url().includes("/webcast/im/fetch")) return;
    try { const b = await r.body(); tratar(deserializeMessage("ProtoMessageFetchResult", b).messages); } catch {}
  });

  const url = process.env.LECTOR_URL || `https://www.tiktok.com/@${usuario}/live`;   // LECTOR_URL: solo para pruebas
  async function abrir() {
    try { await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 }); } catch (e) { console.log("  (TikTok tarda en cargar, reintento)"); }
  }
  await abrir();
  alEstado(false, "Esperando a que empiece tu directo…");

  // vigilancia: si en 90 s no llega nada, recarga la página (por si el directo aún no había empezado)
  setInterval(async () => {
    const vivo = Date.now() - ultimo < 90000;
    alEstado(vivo, vivo ? "" : "Esperando a que empiece tu directo…");
    if (!vivo) await abrir();
  }, 30000);
  setInterval(() => alEstado(Date.now() - ultimo < 90000, Date.now() - ultimo < 90000 ? "" : "Esperando a que empiece tu directo…"), 5000);
  ctx.on("close", () => alEstado(false, "Has cerrado la ventana del lector: vuelve a abrir iniciar.bat"));
}
