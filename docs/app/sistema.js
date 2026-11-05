// ═══════════ Avisos, conexiones y ajustes ═══════════
async function vistaAvisos(){
  const iss=(await gh("/issues?state=open&per_page=50")).filter(i=>!i.pull_request);
  contarSeccion("avisos",iss.length);
  if(!iss.length){app.innerHTML=`<div class="card">${vacio("check","No hay avisos pendientes","Cuando algo necesite tu atención (un borrador de TikTok, un error) aparecerá aquí.")}</div>`;return}
  TEXTOS=[];
  app.innerHTML=iss.map(i=>{const m=(i.body||"").match(/```\n?([\s\S]*?)```/),txt=m?m[1].trim():"",k=TEXTOS.push(txt)-1,tt=/tiktok/i.test(i.title);
    return `<div class="card fade"><div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">${tt?redPill("tiktok"):`<span class="pill warn">${ic("alert","s")}Aviso</span>`}<b>${esc(i.title)}</b><span class="mut peq" style="margin-left:auto">${hace(i.created_at)}</span></div>
    ${txt?`<pre>${esc(txt)}</pre>`:`<p class="mut peq">${esc((i.body||"").replace(/@\w+/g,"").slice(0,400))}</p>`}
    <div style="display:flex;gap:8px;flex-wrap:wrap">${txt?`<button class="btn sec" onclick="copiar(TEXTOS[${k}])">${ic("copy","s")}Copiar texto</button>`:""}<button class="btn" onclick="cerrarAviso(${i.number})">${ic("check","s")}Hecho</button></div></div>`}).join("");
}
const FLUJOS=[["publicar.yml","Publicar","Cada 10 min",20],["estadisticas.yml","Estadísticas y comentarios","Cada hora",90],["tendencias.yml","Tendencias","7:40 y 18:40",14*60],["voz.yml","Voces","Al aprobar un guion",null],["render.yml","Renderizar vídeos","Al entregar una escena",null]];
async function vistaConex(){
  let txt="";try{txt=await leerCrudo("CONEXIONES.md")}catch(e){txt=""}
  const filas=txt.split("\n").filter(l=>l.startsWith("- ")).map(l=>{const ok=/✅|ok|conectad/i.test(l)&&!/❌|error|falta/i.test(l);return `<div class="fila">${ic(ok?"check":"alert")}<span class="t">${esc(l.slice(2)).replace(/\*\*(.*?)\*\*/g,"<b>$1</b>")}</span></div>`}).join("");
  const fecha=(txt.match(/_Comprobado: (.*?)_/)||[])[1];
  let salud=[];
  try{const runs=(await gh("/actions/runs?per_page=60")).workflow_runs;
    salud=FLUJOS.map(([f,n,cada,max])=>{const r=runs.find(x=>x.path.endsWith(f));const edad=r?(Date.now()-new Date(r.updated_at))/60000:null;
      const estado=!r?"gris":r.status!=="completed"?"acc":r.conclusion==="success"?(max&&edad>max*2?"warn":"ok"):r.conclusion==="cancelled"?"warn":"err";
      return {n,cada,r,estado,edad}})}catch(e){}
  app.innerHTML=`<div class="grid g2"><div class="card fade"><div class="h3">${ic("zap")}Salud del sistema<span class="sub">última ejecución de cada proceso</span></div>
   ${salud.length?salud.map(s=>`<div class="fila"><span class="regla ${s.estado==="acc"?"warn":s.estado}" style="padding:0;background:none"><i></i></span><span class="t"><b>${s.n}</b><small>${s.cada} · ${s.r?(s.r.status!=="completed"?"en curso ahora":(s.r.conclusion==="success"?"bien":s.r.conclusion==="cancelled"?"cancelada":"falló")+" "+hace(s.r.updated_at)):"sin ejecuciones"}</small></span>${s.r?`<a class="ib" href="${esc(s.r.html_url)}" target="_blank" title="Ver en GitHub">${ic("ext","s")}</a>`:""}</div>`).join(""):`<p class="mut peq">No se pudo consultar GitHub Actions.</p>`}</div>
   <div class="card fade"><div class="h3">${ic("plug")}Redes sociales<span class="sub">${fecha?"comprobado "+esc(fecha):""}</span></div>${filas||`<p class="mut">Aún no se ha hecho ninguna comprobación.</p>`}
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px"><button class="btn" id="comp">${ic("refresh","s")}Comprobar ahora</button><a class="btn sec" href="conectar.html" target="_blank">${ic("plug","s")}Conectar una red</a></div></div></div>
  <div class="card plano fade"><div class="h3">${ic("info")}Si algo falla</div><p class="mut peq" style="margin:0">TikTok o YouTube: pulsa «Conectar una red», autoriza y pega el código en «Conectar red social» de GitHub. YouTube necesita reconectarse una vez para leer comentarios. Instagram: revisa el usuario del sistema de Meta (IG_TOKEN).</p></div>`;
  $("#comp").onclick=async()=>{$("#comp").disabled=true;try{await lanzar(true);toast("Comprobando… se actualiza en 1-2 minutos.","info");setTimeout(()=>RUTA.s==="conex"&&ir("conex",null,true),90000)}catch(e){toast(esc(e.message),"err");$("#comp").disabled=false}};
}
function vistaAjustes(){
  app.innerHTML=`<div class="grid g2"><div class="card fade"><div class="h3">${ic("clock")}Horario habitual</div>${REDES.map(r=>`<div class="fila">${redPill(r)}<span class="t">${HUECOS[r].map(h=>`<span class="pill" style="margin:2px">${h}:00</span>`).join("")}</span></div>`).join("")}<p class="mut peq">Hora de Madrid. Se usa para proponer el siguiente hueco libre. Mira «Estadísticas → Mejor hora» para saber si conviene cambiarlo.</p></div>
  <div class="card fade"><div class="h3">${ic("user")}Sesión</div><p class="mut">Has entrado como <b style="color:var(--fg)">${esc(usuario.replace("_"," "))}</b> en este navegador.</p><button class="btn sec" onclick="salir()">${ic("out","s")}Cerrar sesión</button>
   <div class="sep"></div><div class="h3">${ic("ext")}Enlaces</div><p class="peq"><a href="https://github.com/${O}/${R}/actions" target="_blank">Ejecuciones en GitHub</a> · <a href="https://github.com/${O}/${R}/releases/tag/videos" target="_blank">Vídeos guardados</a> · <a href="https://github.com/${O}/${R}/blob/main/CLAUDE.md" target="_blank">Reglas de producción</a></p>
   <p class="faint peq">Atajo: <b>Ctrl K</b> abre el buscador de secciones y acciones.</p></div></div>`;
}
