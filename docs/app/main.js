// ═══════════ Navegación, paleta de comandos y arranque ═══════════
const SECCIONES=[
 {g:"General"},
 {k:"inicio",t:"Resumen",ic:"home",d:"Cómo va todo de un vistazo",fn:vistaInicio},
 {g:"Contenido"},
 {k:"prod",t:"Producción",ic:"film",d:"Guiones, borradores y vídeos en marcha",fn:vistaProd,def:"marcha"},
 {k:"tend",t:"Tendencias",ic:"flame",d:"Qué se busca hoy en España y cómo convertirlo en un vídeo",fn:vistaTend,def:"analisis"},
 {k:"pub",t:"Publicación",ic:"cal",d:"Calendario, publicar ya y borradores de TikTok",fn:vistaPub,def:innerWidth<700?"lista":"semana"},
 {g:"Audiencia"},
 {k:"stats",t:"Estadísticas",ic:"chart",d:"Qué funciona y por qué",fn:vistaStats,def:"general"},
 {k:"com",t:"Comunidad",ic:"chat",d:"Comentarios, preguntas e ideas de tus seguidores",fn:vistaCom,def:"bandeja"},
 {k:"crec",t:"Crecimiento",ic:"rocket",d:"Objetivos, vídeos que despegan y competencia",fn:vistaCrec,def:"objetivos"},
 {g:"Sistema"},
 {k:"avisos",t:"Avisos",ic:"bell",d:"Errores y tareas pendientes",fn:vistaAvisos},
 {k:"conex",t:"Conexiones",ic:"plug",d:"Estado de cada red y de cada proceso",fn:vistaConex},
 {k:"ajustes",t:"Ajustes",ic:"gear",d:"Horario, sesión y enlaces",fn:vistaAjustes},
];
const SEC=Object.fromEntries(SECCIONES.filter(s=>s.k).map(s=>[s.k,s]));
const CNT={};
let RUTA={s:"inicio",sub:null};

function pintarNav(){
  $("#nav").innerHTML=SECCIONES.map(s=>s.g?`<div class="grupo">${s.g}</div>`:`<a href="#/${s.k}" class="${RUTA.s===s.k?"on":""}">${ic(s.ic)}${s.t}${CNT[s.k]?`<span class="badge ${s.k==="avisos"?"rojo":""}">${CNT[s.k]}</span>`:""}</a>`).join("");
  const tb=["inicio","prod","pub","stats","tend"];
  $("#tabbar").innerHTML=tb.map(k=>`<a href="#/${k}" class="${RUTA.s===k?"on":""}">${ic(SEC[k].ic)}${SEC[k].t}${CNT[k]?`<span class="badge">${CNT[k]}</span>`:""}</a>`).join("");
  $("#foot").innerHTML=usuario?`<div class="avatar">${iniciales(usuario)}</div><div style="flex:1;min-width:0"><b>${esc(usuario.replace("_"," "))}</b><small>v${esc(window.VERSION)}</small></div><button class="ib" title="Cerrar sesión" onclick="salir()">${ic("out","s")}</button>`:"";
}
function contarSeccion(k,n){CNT[k]=n;pintarNav()}

async function ir(s,sub,silencioso=false){
  if(!SEC[s])s="inicio";
  const cambio=RUTA.s!==s||RUTA.sub!==(sub||SEC[s].def||null);
  RUTA={s,sub:sub||SEC[s].def||null};
  const h=`#/${s}${RUTA.sub?"/"+RUTA.sub:""}`;if(location.hash!==h)history.replaceState(null,"",h);
  pintarNav();
  if(!tok)return pantallaToken();
  if(!silencioso||cambio){heroStop();ocultarTip()}
  const sec=SEC[s],main=$("#app");
  if(silencioso&&!cambio&&$("#cont")){
    const y=scrollY,tmp=document.createElement("div");app=tmp;
    try{await sec.fn(RUTA.sub);$("#cont").replaceChildren(...tmp.childNodes);app=$("#cont");pintarIconos(app);despuesDePintar&&despuesDePintar();scrollTo({top:y})}catch(e){app=$("#cont")}
    despuesDePintar=null;return;
  }
  scrollTo({top:0});
  main.innerHTML=`<div class="ph fade"><div><h1>${sec.t}</h1><p>${sec.d}</p></div><div class="acciones" id="acc"></div></div><div id="cont"><div class="card"><div class="skel" style="width:55%"></div><div class="skel"></div><div class="skel" style="width:80%"></div></div></div>`;
  app=$("#cont");
  try{await sec.fn(RUTA.sub);pintarIconos(app);despuesDePintar&&despuesDePintar()}
  catch(e){console.error(e);if(e.status===401)return pantallaToken("La clave de GitHub ha caducado o no es válida.");app.innerHTML=`<div class="card"><div class="msg err">${ic("alert","s")}<div>${esc(e.message)}</div></div><button class="btn sec" onclick="ir(RUTA.s,RUTA.sub)">${ic("refresh","s")}Reintentar</button></div>`}
  despuesDePintar=null;
}
let despuesDePintar=null;
const acciones=html=>{const a=$("#acc");if(a)a.innerHTML=html};
addEventListener("hashchange",()=>{const [,s,sub]=location.hash.split("/");if(s!==RUTA.s||(sub||null)!==RUTA.sub)ir(s||"inicio",sub)});

// ── Paleta de comandos (Ctrl+K) ──
function opcionesPaleta(){
  const o=[];
  for(const s of SECCIONES.filter(x=>x.k))o.push({t:s.t,d:s.d,ic:s.ic,go:()=>ir(s.k)});
  const subs=[["prod","guiones","Aprobar guiones"],["prod","borradores","Revisar borradores"],["prod","marcha","Vídeos en marcha"],["prod","ideas","Banco de ideas"],["pub","semana","Calendario semanal"],["pub","lista","Lista de publicaciones"],["pub","subir","Subir un vídeo propio"],["pub","tiktok","Borradores de TikTok"],
   ["stats","ranking","Ranking de vídeos"],["stats","comparar","Comparar dos vídeos"],["stats","horas","Mejor hora para publicar"],["stats","informe","Informe semanal"],["tend","analisis","Tendencias analizadas"],["tend","senales","Señales en bruto"],
   ["com","bandeja","Bandeja de comentarios"],["com","ideas","Ideas que piden los seguidores"],["crec","objetivos","Objetivos"],["crec","despegan","Vídeos que despegan"],["crec","horas","Horas muertas"],["crec","competencia","Competencia"]];
  for(const [s,k,t] of subs)o.push({t,d:SEC[s].t,ic:SEC[s].ic,go:()=>ir(s,k)});
  o.push({t:"Actualizar estadísticas ahora",d:"Acción",ic:"refresh",go:()=>accion(()=>lanzarFlujo("estadisticas.yml"),"Recogiendo estadísticas… tardan 1-2 minutos.",{recargar:false})});
  o.push({t:"Recoger tendencias ahora",d:"Acción",ic:"flame",go:()=>accion(()=>lanzarFlujo("tendencias.yml"),"Buscando tendencias… tardan 1-2 minutos.",{recargar:false})});
  o.push({t:"Añadir una idea al banco",d:"Acción",ic:"idea",go:()=>nuevaIdea()});
  o.push({t:"Cerrar sesión",d:"Cuenta",ic:"out",go:salir});
  return o;
}
function abrirPaleta(){
  if(!tok)return;const ops=opcionesPaleta();let sel=0,vis=ops;
  modal(`<input id="pq" placeholder="Buscar sección o acción…" autocomplete="off"><div class="res" id="pr"></div>`,{clase:"paleta",alAbrir:(m,cerrar)=>{
    const pinta=()=>{m.querySelector("#pr").innerHTML=vis.map((o,i)=>`<div class="op ${i===sel?"on":""}" data-i="${i}">${ic(o.ic)}${esc(o.t)}<small>${esc(o.d)}</small></div>`).join("")||`<div class="vacio">Nada coincide</div>`;
      m.querySelectorAll(".op").forEach(e=>{e.onclick=()=>{cerrar();vis[+e.dataset.i].go()};e.onmousemove=()=>{if(sel!==+e.dataset.i){sel=+e.dataset.i;pinta()}}})};
    const q=m.querySelector("#pq");q.oninput=()=>{const t=q.value.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");vis=ops.filter(o=>(o.t+" "+o.d).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"").includes(t));sel=0;pinta()};
    q.onkeydown=e=>{if(e.key==="ArrowDown"){sel=Math.min(vis.length-1,sel+1);pinta();e.preventDefault()}else if(e.key==="ArrowUp"){sel=Math.max(0,sel-1);pinta();e.preventDefault()}else if(e.key==="Enter"&&vis[sel]){cerrar();vis[sel].go()}};
    pinta();setTimeout(()=>q.focus(),10)}});
}
addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){e.preventDefault();cerrarModalActual?cerrarModalActual(null):abrirPaleta()}});
$("#abrirPaleta").onclick=abrirPaleta;$("#abrirPaleta2").onclick=abrirPaleta;pintarIconos();

// ── Arranque ──
// (las versiones antiguas del panel buscan este texto para recargarse solas: const VERSION="2026-11-05.2")
(async()=>{try{const t=await (await fetch(location.pathname+"?nv="+Date.now(),{cache:"no-store"})).text();const m=t.match(/window\.VERSION="([^"]+)"/);
  if(m&&m[1]!==window.VERSION&&!sessionStorage.getItem("rv"+m[1])){sessionStorage.setItem("rv"+m[1],1);location.replace(location.pathname+"?v="+m[1]+location.hash)}}catch(e){}})();
setInterval(()=>{if(document.hidden||!tok||cerrarModalActual)return;const f=document.activeElement;if(f&&f.matches("input,textarea,select"))return;
  if(["inicio","stats","prod","pub","avisos","com"].includes(RUTA.s)){olvidar();ir(RUTA.s,RUTA.sub,true)}},300000);
async function contadores(){
  try{const v=(await json("produccion/estado.json",{ttl:30000})).videos;CNT.prod=v.filter(x=>x.estado==="revision"||x.estado==="propuesto").length}catch(e){}
  try{const i=await gh("/issues?state=open&per_page=50");CNT.avisos=i.filter(x=>!x.pull_request).length}catch(e){}
  pintarNav();
}
function arrancar(){const [,s,sub]=location.hash.split("/");pintarNav();ir(s||"inicio",sub);if(tok)contadores()}
arrancar();
