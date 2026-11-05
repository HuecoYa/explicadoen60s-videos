// ═══════════ Núcleo: GitHub, datos, fechas y piezas de interfaz ═══════════
const O="explicadoen60s",R="explicadoen60s.github.io",API=`https://api.github.com/repos/${O}/${R}`;
const TZ="Europe/Madrid";
const HUECOS={tiktok:[10,13,16,18,21],instagram:[10,18],youtube:[12,16]};
const REDES=["tiktok","instagram","youtube"];
const COLOR={tiktok:"#3987e5",instagram:"#d55181",youtube:"#c98500"};
const NOMBRE={tiktok:"TikTok",instagram:"Instagram",youtube:"YouTube",todas:"Todas"};
const EST={pendiente:"Pendiente",publicado:"Publicado",borrador:"En tu bandeja de TikTok",error:"Error",caducado:"No salió"};
const EST_PILL={pendiente:"",publicado:"ok",borrador:"warn",error:"err",caducado:"err"};
let tok="";try{tok=localStorage.getItem("ghtoken")||""}catch(e){}
let usuario="";try{usuario=localStorage.getItem("usuario")||""}catch(e){}
if(!usuario)tok="";
let cal=null,calSha=null;
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
let app=$("#app");
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const dorm=ms=>new Promise(r=>setTimeout(r,ms));

// ── GitHub ──
async function gh(path,opt={}){
  const r=await fetch(path.startsWith("http")?path:API+path,{...opt,headers:{Authorization:`Bearer ${tok}`,Accept:"application/vnd.github+json",...(opt.headers||{})}});
  if(!r.ok){const t=await r.text();const e=new Error(`GitHub ${r.status}: ${t.slice(0,200)}`);e.status=r.status;throw e}
  return r.status===204?null:(opt.texto?r.text():r.json());
}
const b64e=s=>btoa(unescape(encodeURIComponent(s))), b64d=s=>decodeURIComponent(escape(atob(s.replace(/\n/g,""))));
async function leerArchivo(p){const j=await gh(`/contents/${p}?ref=main&t=${Date.now()}`);return {txt:j.content?b64d(j.content):await leerCrudo(p),sha:j.sha}}
async function leerCrudo(p){return gh(`/contents/${p}?ref=main&t=${Date.now()}`,{headers:{Accept:"application/vnd.github.raw"},texto:true})}
// caché corta de ficheros de solo lectura (para no pedir lo mismo al cambiar de pestaña)
const CACHE={};
async function json(p,{ttl=60000,opcional=false}={}){
  const c=CACHE[p];if(c&&Date.now()-c.t<ttl)return c.v;
  try{const v=JSON.parse(await leerCrudo(p));CACHE[p]={t:Date.now(),v};return v}
  catch(e){if(opcional&&e.status===404)return null;throw e}
}
function olvidar(p){if(p)delete CACHE[p];else for(const k in CACHE)delete CACHE[k]}
async function cargarCal(){const f=await leerArchivo("programador/calendario.json");cal=JSON.parse(f.txt);calSha=f.sha;return cal}
async function guardarCal(cambio,msg){
  for(let i=0;i<4;i++){
    await cargarCal();cambio(cal);
    cal.posts.sort((a,b)=>new Date(a.hora)-new Date(b.hora)||a.red.localeCompare(b.red));
    try{const j=await gh("/contents/programador/calendario.json",{method:"PUT",body:JSON.stringify({message:msg+" [skip ci]",content:b64e(JSON.stringify(cal,null,1)+"\n"),sha:calSha,branch:"main"})});calSha=j.content.sha;olvidar("programador/calendario.json");return}
    catch(e){if(e.status!==409&&e.status!==422)throw e;await dorm(1500)}
  }
  throw new Error("No se pudo guardar: el calendario cambió a la vez. Vuelve a intentarlo.");
}
async function editarJson(ruta,cambio,msg,{crear=null}={}){
  for(let i=0;i<4;i++){
    let f;try{f=await leerArchivo(ruta)}catch(e){if(e.status===404&&crear)f={txt:JSON.stringify(crear),sha:null};else throw e}
    const d=JSON.parse(f.txt);cambio(d);
    try{await gh(`/contents/${ruta}`,{method:"PUT",body:JSON.stringify({message:msg,content:b64e(JSON.stringify(d,null,1)+"\n"),...(f.sha?{sha:f.sha}:{}),branch:"main"})});olvidar(ruta);return d}
    catch(e){if(e.status!==409&&e.status!==422)throw e;await dorm(1500)}
  }
  throw new Error("No se pudo guardar: cambió a la vez. Vuelve a intentarlo.");
}
async function lanzarFlujo(f,inputs){await gh(`/actions/workflows/${f}/dispatches`,{method:"POST",body:JSON.stringify({ref:"main",...(inputs?{inputs}:{})})})}
const lanzar=(probar=false)=>lanzarFlujo("publicar.yml",{probar});

// ── Fechas (hora de Madrid) ──
function partes(d){const o={};new Intl.DateTimeFormat("en-GB",{timeZone:TZ,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",weekday:"short",hourCycle:"h23"}).formatToParts(d).forEach(p=>o[p.type]=p.value);return o}
function aLocal(iso){const p=partes(new Date(iso));return `${p.year}-${p.month}-${p.day}T${p.hour}:${p.minute}`}
function aIso(local){
  const [d,t]=local.split("T"),[Y,M,D]=d.split("-").map(Number),[h,m]=t.split(":").map(Number);
  const utc=Date.UTC(Y,M-1,D,h,m),p=partes(new Date(utc));
  const off=Math.round((Date.UTC(+p.year,p.month-1,+p.day,+p.hour,+p.minute)-utc)/60000);
  const s=off>=0?"+":"-",a=Math.abs(off);
  return `${d}T${t}:00${s}${String(a/60|0).padStart(2,"0")}:${String(a%60).padStart(2,"0")}`;
}
const diaClave=d=>{const p=partes(d);return `${p.year}-${p.month}-${p.day}`};
const horaMadrid=iso=>+partes(new Date(iso)).hour;
const DIAS=["lun","mar","mié","jue","vie","sáb","dom"];
const diaSemana=iso=>({Mon:0,Tue:1,Wed:2,Thu:3,Fri:4,Sat:5,Sun:6})[partes(new Date(iso)).weekday];
const fmtDia=iso=>new Date(iso).toLocaleDateString("es-ES",{timeZone:TZ,weekday:"long",day:"numeric",month:"long"});
const fmtDiaC=iso=>new Date(iso).toLocaleDateString("es-ES",{timeZone:TZ,weekday:"short",day:"numeric",month:"short"});
const fmtHora=iso=>new Date(iso).toLocaleTimeString("es-ES",{timeZone:TZ,hour:"2-digit",minute:"2-digit"});
const hace=iso=>{if(!iso)return "—";const m=Math.round((Date.now()-new Date(iso))/60000);return m<1?"ahora mismo":m<60?`hace ${m} min`:m<1440?`hace ${Math.round(m/60)} h`:`hace ${Math.round(m/1440)} días`};
const dentro=iso=>{const m=Math.round((new Date(iso)-Date.now())/60000);return m<=0?"ya":m<60?`en ${m} min`:m<1440?`en ${Math.round(m/60)} h`:`en ${Math.round(m/1440)} días`};
const EXTRA={};
function siguienteHueco(red,ocupados){
  const ahora=Date.now()+15*60000;
  for(let d=0;d<30;d++){
    const base=new Date(Date.now()+d*864e5),p=partes(base);
    for(const h of (EXTRA[`${p.year}-${p.month}-${p.day}`]||{})[red]||HUECOS[red]){
      const loc=`${p.year}-${p.month}-${p.day}T${String(h).padStart(2,"0")}:00`,iso=aIso(loc);
      if(new Date(iso)<ahora)continue;
      if(!ocupados.some(x=>x.red===red&&Math.abs(new Date(x.hora)-new Date(iso))<30*60000))return loc;
    }
  }
}

// ── Números ──
const nf=new Intl.NumberFormat("es-ES"),nc=new Intl.NumberFormat("es-ES",{notation:"compact",maximumFractionDigits:1});
const fmtN=n=>n==null||isNaN(n)?"—":(Math.abs(n)>=10000?nc.format(n):nf.format(Math.round(n)));
const pct=(x,d=1)=>x==null||!isFinite(x)?"—":(x*100).toFixed(d).replace(".",",")+" %";
const mediana=a=>{const s=a.filter(x=>x!=null&&isFinite(x)).sort((x,y)=>x-y);if(!s.length)return null;const m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2};
function contar(el,valor){if(valor==null||valor===""){el.textContent="—";return}valor=+valor;const t0=performance.now(),d=850;
  const paso=t=>{const p=Math.min(1,(t-t0)/d),e=1-Math.pow(1-p,3);el.textContent=fmtN(valor*e);if(p<1&&el.isConnected)requestAnimationFrame(paso)};requestAnimationFrame(paso)}
function delta(act,ant){if(ant==null||act==null)return "";const d=act-ant;if(!ant&&!d)return `<span class="delta eq">=</span>`;
  const p=ant?d/ant:null;return `<span class="delta ${d>0?"up":d<0?"down":"eq"}">${d>0?"▲":d<0?"▼":"="} ${p!=null?Math.abs(p*100).toFixed(p&&Math.abs(p)<.1?1:0).replace(".",",")+" %":fmtN(Math.abs(d))}</span>`}

// ── Iconos (trazos tipo Lucide, en máscara para heredar el color) ──
const P={
 home:'<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
 film:'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 3v18M17 3v18M3 8h4M3 16h4M17 8h4M17 16h4"/>',
 trend:'<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
 cal:'<rect x="3" y="4.5" width="18" height="17" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/>',
 chart:'<path d="M3 3v18h18"/><path d="M7 15l4-5 3 3 5-7"/>',
 chat:'<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-5A8 8 0 1 1 21 12Z"/>',
 target:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>',
 bell:'<path d="M6 8a6 6 0 0 1 12 0c0 7 3 8.5 3 8.5H3S6 15 6 8"/><path d="M10.3 20.5a2 2 0 0 0 3.4 0"/>',
 plug:'<path d="M9 2v6M15 2v6"/><path d="M6 8h12v3a6 6 0 0 1-12 0Z"/><path d="M12 17v5"/>',
 gear:'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"/>',
 search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
 plus:'<path d="M12 5v14M5 12h14"/>',check:'<path d="M20 6 9 17l-5-5"/>',x:'<path d="M18 6 6 18M6 6l12 12"/>',
 clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',play:'<path d="M7 4v16l13-8Z"/>',
 trash:'<path d="M3 6h18M8 6V4h8v2M6 6l1 15h10l1-15"/>',edit:'<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
 copy:'<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/>',
 ext:'<path d="M14 3h7v7M21 3l-9 9"/><path d="M19 14v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h6"/>',
 refresh:'<path d="M21 12a9 9 0 1 1-2.6-6.4L21 8"/><path d="M21 3v5h-5"/>',upload:'<path d="M12 15V3M7 8l5-5 5 5"/><path d="M4 15v5h16v-5"/>',
 idea:'<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5 1 1.2 1 2V16h5.2v-.2c0-.8.4-1.5 1-2A6 6 0 0 0 12 3Z"/>',
 flame:'<path d="M12 22c4 0 7-3 7-7 0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-4-2 2-5 5-5 8 0 4 3 7 7 7Z"/>',
 alert:'<path d="M12 3 2 20h20Z"/><path d="M12 10v4M12 17.5v.5"/>',info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
 up:'<path d="m6 15 6-6 6 6"/>',left:'<path d="m15 6-6 6 6 6"/>',right:'<path d="m9 6 6 6-6 6"/>',down:'<path d="m6 9 6 6 6-6"/>',user:'<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
 eye:'<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
 heart:'<path d="M12 20s-8-4.7-8-10.5A4.5 4.5 0 0 1 12 7a4.5 4.5 0 0 1 8 2.5C20 15.3 12 20 12 20Z"/>',
 share:'<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/>',
 zap:'<path d="M13 2 4 14h7l-1 8 9-12h-7Z"/>',spark:'<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
 out:'<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5M21 12H9"/>',filter:'<path d="M3 5h18l-7 8v6l-4 2v-8Z"/>',
 grip:'<circle cx="9" cy="6" r="1"/><circle cx="15" cy="6" r="1"/><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="9" cy="18" r="1"/><circle cx="15" cy="18" r="1"/>',
 list:'<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',grid:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
 compare:'<path d="M16 3h5v5M8 21H3v-5M21 3l-7 7M3 21l7-7"/>',report:'<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
 rocket:'<path d="M5 15c-1.5 1.5-2 5-2 5s3.5-.5 5-2"/><path d="M9 15 4 13l3-4h5M9 15l2 5 4-3v-5"/><path d="M12 9c3-5 7-6 9-6 0 2-1 6-6 9"/>',
 eyes:'<circle cx="8" cy="12" r="4"/><circle cx="16" cy="12" r="4"/><circle cx="8" cy="12" r="1"/><circle cx="16" cy="12" r="1"/>',
 mic:'<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',cube:'<path d="M12 2 3 7v10l9 5 9-5V7Z"/><path d="m3 7 9 5 9-5M12 12v10"/>',
 star:'<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9Z"/>',
 cog2:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l4 2"/>',
};
const SVG=n=>`url('data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${P[n]||P.info}</svg>`).replace(/'/g,"%27")}')`;
const IC={};const ic=(n,c="")=>{IC[n]=IC[n]||SVG(n);return `<span class="ico ${c}" style="--m:${IC[n]}"></span>`};
function pintarIconos(raiz=document){raiz.querySelectorAll(".ico[data-i]").forEach(e=>{e.style.setProperty("--m",SVG(e.dataset.i));e.removeAttribute("data-i")})}

// ── Avisos flotantes, modales y paleta ──
function toast(txt,tipo="ok",ms=4200){
  const d=document.createElement("div");d.className="toast "+tipo;d.innerHTML=ic(tipo==="err"?"alert":tipo==="info"?"info":"check")+`<div>${txt}</div>`;
  $("#toasts").append(d);setTimeout(()=>{d.classList.add("sale");setTimeout(()=>d.remove(),260)},ms);
}
let cerrarModalActual=null;
function modal(html,{clase="",alAbrir}={}){
  const capa=$("#capaModal");capa.innerHTML=`<div class="modal ${clase}" role="dialog" aria-modal="true">${html}</div>`;capa.hidden=false;
  return new Promise(res=>{
    const cerrar=v=>{capa.hidden=true;capa.innerHTML="";document.removeEventListener("keydown",tecla);cerrarModalActual=null;res(v)};
    const tecla=e=>{if(e.key==="Escape")cerrar(null)};document.addEventListener("keydown",tecla);
    capa.onclick=e=>{if(e.target===capa)cerrar(null)};cerrarModalActual=cerrar;
    alAbrir&&alAbrir(capa.firstElementChild,cerrar);
    const f=capa.querySelector("input,textarea,select,.btn");f&&f.focus();
  });
}
function confirmar(titulo,texto="",{si="Sí",peligro=false}={}){
  return modal(`<h3>${esc(titulo)}</h3>${texto?`<p class="mut">${texto}</p>`:""}<div class="pie"><button class="btn sec" data-r="0">Cancelar</button><button class="btn ${peligro?"peligro":""}" data-r="1">${esc(si)}</button></div>`,
    {alAbrir:(m,c)=>m.querySelectorAll("[data-r]").forEach(b=>b.onclick=()=>c(b.dataset.r==="1"))});
}
function pedir(titulo,{texto="",valor="",tipo="text",largo=false,placeholder="",si="Guardar",chips=[]}={}){
  return modal(`<h3>${esc(titulo)}</h3>${texto?`<p class="mut" style="margin:0 0 6px">${texto}</p>`:""}
    ${chips.length?`<div class="chips" style="margin:10px 0">${chips.map(c=>`<button class="chip" data-c="${esc(c)}">${esc(c)}</button>`).join("")}</div>`:""}
    ${largo?`<textarea id="mv" placeholder="${esc(placeholder)}">${esc(valor)}</textarea>`:`<input id="mv" type="${tipo}" value="${esc(valor)}" placeholder="${esc(placeholder)}">`}
    <div class="pie"><button class="btn sec" data-r="0">Cancelar</button><button class="btn" data-r="1">${esc(si)}</button></div>`,
    {alAbrir:(m,c)=>{const i=m.querySelector("#mv");m.querySelectorAll("[data-c]").forEach(b=>b.onclick=()=>{b.classList.toggle("on");const sel=[...m.querySelectorAll("[data-c].on")].map(x=>x.dataset.c);i.value=sel.join(". ")+(sel.length?". ":"")});
      m.querySelectorAll("[data-r]").forEach(b=>b.onclick=()=>c(b.dataset.r==="1"?i.value.trim():null));if(!largo)i.onkeydown=e=>{if(e.key==="Enter")c(i.value.trim())}}});
}
async function accion(fn,ok,{recargar=true}={}){try{const r=await fn();if(ok)toast(ok);if(recargar)ir(RUTA.s,RUTA.sub,true);return r}catch(e){toast(esc(e.message),"err",7000)}}
async function copiar(t,el){try{await navigator.clipboard.writeText(t);toast("Copiado al portapapeles")}catch(e){await pedir("Copia el texto",{valor:t,largo:true,si:"Cerrar"})}}

// ── Tooltip ──
const tip=$("#tip");
function verTip(e,html){tip.innerHTML=html;tip.style.display="block";const x=Math.min(e.clientX+14,innerWidth-tip.offsetWidth-8),y=Math.min(e.clientY+14,innerHeight-tip.offsetHeight-8);tip.style.left=x+"px";tip.style.top=y+"px"}
function ocultarTip(){tip.style.display="none"}

// ── Trozos de interfaz ──
const vacio=(icono,titulo,texto="",extra="")=>`<div class="vacio">${ic(icono)}<b>${titulo}</b>${texto}${extra?`<div style="margin-top:14px">${extra}</div>`:""}</div>`;
const redPill=r=>`<span class="red ${r}">${NOMBRE[r]||r}</span>`;
function segmentos(s,lista,actual){return `<nav class="seg">${lista.map(([k,t,n,rojo])=>`<a href="#/${s}/${k}" class="${actual===k?"on":""}">${t}${n?`<span class="badge ${rojo?"rojo":""}">${n}</span>`:""}</a>`).join("")}</nav>`}
function kpi(lab,val,pie="",icono=""){return `<div class="card kpi fade"><div class="lab">${icono?ic(icono,"s"):""}${lab}</div><div class="val" data-n="${val??""}">—</div><div class="pie">${pie}</div></div>`}
function animarKpis(raiz=app){raiz.querySelectorAll("[data-n]").forEach(el=>contar(el,el.dataset.n===""?null:el.dataset.n))}
const iniciales=n=>(n||"?").replace(/^@/,"").split(/[\s._]+/).filter(Boolean).slice(0,2).map(x=>x[0].toUpperCase()).join("")||"?";
