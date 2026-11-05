// ═══════════ Producción ═══════════
const FASES={propuesto:"Propuesta",aprobado:"Generando la voz",voz:"Esperando la escena 3D",escena:"En cola para renderizar",renderizando:"Renderizando",rehacer:"Corrigiendo lo que pediste",revision:"Esperando tu revisión",programado:"Programado",rechazado:"Descartado"};
const ETAPAS=["Guion","Voz","Escena 3D","Render","Revisión"];
const ETAPA_DE={aprobado:1,voz:2,rehacer:2,escena:3,renderizando:3,revision:4};
const CAMBIOS_RAPIDOS=["La cámara está demasiado lejos","El primer segundo no engancha","Falta una cifra o contador en pantalla","Una etiqueta tapa el objeto","Algo se sale del encuadre","El objeto no se reconoce","Lo que se ve no coincide con la voz","Demasiado rápido","Demasiado quieto en algún momento","Cambiar el título del post"];
let PROD=[];

function proximaPasada(){const ahora=new Date();for(let d=0;d<2;d++)for(const [h,m] of [[8,56],[19,56]]){const p=partes(new Date(Date.now()+d*864e5));const iso=aIso(`${p.year}-${p.month}-${p.day}T${String(h).padStart(2,"0")}:${m}`);if(new Date(iso)>ahora)return iso}}
const NUM_PAL=/\b(\d+[\d.,]*|cero|uno|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|quince|veinte|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|doscientos|trescientos|quinientos|mil|millón|millones|mitad|doble|triple)\b/gi;
function reglasDe(v){
  const g=v.guion||"",pal=g.split(/\s+/).filter(Boolean).length,frase1=(g.split(/(?<=[.?!…])\s/)[0]||"");
  const r=v.reglas||{},num=(g.match(NUM_PAL)||[]).length;
  const nivel=(x,def)=>x==null?def:(x>=7?"ok":x>=4?"warn":"err");
  return [
   ["Tema de uso diario",nivel(r.cotidiano,/\b(tu|tus|te|ti|tienes|usas|ahora mismo|cada (día|mañana|noche|vez)|todos los días|en tu casa)\b/i.test(frase1)?"ok":"warn"),r.cotidiano_nota||"La primera frase debería hablarle al espectador («tu…», «ahora mismo…»)."],
   ["Acción en el primer segundo",nivel(r.primer_segundo,"gris"),r.primer_segundo_nota||"Se comprueba en la escena 3D."],
   ["Lo enseña con cifras",nivel(r.ensenar,num>=4?"ok":num>=2?"warn":"err"),r.ensenar_nota||`${num} cifras en el guion (mínimo 2 que se puedan enseñar).`],
   ["Duración",pal>=205&&pal<=245?"ok":pal>=190&&pal<=260?"warn":"err",`${pal} palabras · ≈${Math.round(pal/3.4)} s`],
  ];
}
const semaforo=v=>`<div class="semaforo">${reglasDe(v).map(([t,n,nota])=>`<span class="regla ${n}" title="${esc(nota)}"><i></i>${t}</span>`).join("")}</div>`;

async function vistaProd(sub){
  const est=await json("produccion/estado.json",{ttl:15000});PROD=est.videos;
  const rev=PROD.filter(v=>v.estado==="revision"),pro=PROD.filter(v=>v.estado==="propuesto"),mar=PROD.filter(v=>["aprobado","voz","escena","renderizando","rehacer","revision"].includes(v.estado));
  const ideas=(await json("produccion/ideas.json",{opcional:true}))?.ideas||[];
  contarSeccion("prod",rev.length+pro.length);
  acciones(`<button class="btn sec" onclick="nuevaIdea()">${ic("idea","s")}Nueva idea</button>`);
  let h=segmentos("prod",[["marcha","En marcha",mar.length],["guiones","Guiones",pro.length],["borradores","Borradores",rev.length],["ideas","Banco de ideas",ideas.filter(i=>i.estado!=="usada").length],["historial","Historial"]],sub);
  if(sub==="guiones")h+=await prodGuiones(pro);
  else if(sub==="borradores")h+=prodBorradores(rev);
  else if(sub==="ideas")h+=prodIdeas(ideas);
  else if(sub==="historial")h+=prodHistorial();
  else h+=await prodMarcha(mar);
  app.innerHTML=h;
}

async function trabajosGitHub(){
  try{
    const runs=(await gh("/actions/runs?per_page=15")).workflow_runs.filter(r=>r.status!=="completed");
    const out=[];
    for(const r of runs.slice(0,4)){
      let jobs=[];try{jobs=(await gh(`/actions/runs/${r.id}/jobs`)).jobs.filter(j=>j.status!=="completed")}catch(e){}
      out.push({nombre:r.name,estado:r.status,desde:r.run_started_at||r.created_at,url:r.html_url,jobs:jobs.map(j=>({n:j.name,desde:j.started_at,estado:j.status}))});
    }
    return out;
  }catch(e){return null}
}
async function prodMarcha(mar){
  const trab=await trabajosGitHub(),pas=proximaPasada();
  const jobDe=id=>trab?.flatMap(t=>t.jobs).find(j=>j.n.includes(`(${id})`));
  const eta=v=>{const j=jobDe(v.id);
    if(v.error)return `<span class="pill err">${ic("alert","s")}${esc(v.error)}</span>`;
    if(v.estado==="aprobado")return j?`Generando la voz desde ${hace(j.desde)} · lista en unos minutos`:"La voz se genera en 5-15 minutos";
    if(v.estado==="voz"||v.estado==="rehacer")return `Claude la hará en la próxima pasada: ${fmtDiaC(pas)} a las ${fmtHora(pas)} (${dentro(pas)})`;
    if(v.estado==="escena")return j?`Renderizando desde ${hace(j.desde)}`:"El render empieza en unos minutos";
    if(v.estado==="renderizando")return j?`Renderizando desde ${hace(j.desde)} · listo hacia las ${fmtHora(new Date(new Date(j.desde).getTime()+32*60000).toISOString())}`:"Renderizando (unos 30 minutos)";
    if(v.estado==="revision")return "Listo: revísalo y apruébalo para programarlo";return ""};
  let h=`<div class="grid g21"><div class="card fade"><div class="h3">${ic("film")}Vídeos en camino<span class="sub">${mar.length}</span></div>`;
  h+=mar.length?mar.map(v=>{const e=ETAPA_DE[v.estado]??0;return `<div class="fila" style="display:block"><div style="display:flex;gap:10px;align-items:center"><span class="t"><b>${esc(v.titulo)}</b></span><span class="pill ${v.estado==="revision"?"acc":v.error?"err":""}">${FASES[v.estado]}</span>${v.estado==="revision"?`<a class="btn peq" href="#/prod/borradores">Revisar</a>`:""}</div>
    <div class="etapas">${ETAPAS.map((_,i)=>`<div class="etapa ${i<e?"hecha":i===e?(v.error?"fallo":"ahora"):""}"></div>`).join("")}</div>
    <div class="etapas-n">${ETAPAS.map((t,i)=>`<span class="${i<=e?"on":""}">${t}</span>`).join("")}</div>
    <div class="mut peq" style="margin-top:6px">${eta(v)}${v.nota?` · <i>Cambios pedidos: ${esc(v.nota)}</i>`:""}</div></div>`}).join("")
   :vacio("film","Nada en marcha","Cuando apruebes un guion, aquí verás cómo avanza paso a paso.",`<a class="btn sec peq" href="#/prod/guiones">Ver guiones</a>`);
  h+=`</div><div class="card fade"><div class="h3">${ic("zap")}GitHub trabajando ahora</div>`;
  h+=trab==null?`<p class="mut peq">No se pudo consultar (la clave necesita permiso «Actions: lectura»).</p>`:trab.length?trab.map(t=>`<div class="fila" style="display:block"><b>${esc(t.nombre)}</b> <span class="pill ${t.estado==="in_progress"?"acc":""}">${t.estado==="in_progress"?"en curso":"en cola"}</span><div class="mut peq">${hace(t.desde)}${t.jobs.length?" · "+t.jobs.map(j=>esc(j.n)).join(", "):""}</div></div>`).join("")
   :vacio("check","Nada en curso","Voces, renders y publicaciones aparecen aquí mientras se hacen.");
  h+=`<div class="sep"></div><div class="mut peq">${ic("clock","s")} Próxima pasada de Claude: <b style="color:var(--fg)">${fmtDiaC(pas)}, ${fmtHora(pas)}</b><br>Escribe escenas, corrige lo que pidas y propone guiones nuevos.</div></div></div>`;
  return h;
}

async function prodGuiones(pro){
  if(!pro.length)return `<div class="card">${vacio("idea","No hay guiones esperando",`Claude propone nuevos en cada pasada (${fmtHora(proximaPasada())}). Puedes darle temas en el banco de ideas.`,`<a class="btn sec peq" href="#/prod/ideas">Banco de ideas</a>`)}</div>`;
  return pro.map(v=>{const pal=(v.guion||"").split(/\s+/).length;return `<div class="card fade">
   <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:flex-start"><div><b style="font-size:16.5px;font-family:'Space Grotesk'">${esc(v.titulo)}</b><div class="mut peq" style="margin-top:2px">Formato ${esc(v.formato||"?")} · ${pal} palabras · ≈${Math.round(pal/3.4)} s${v.tendencia?` · ${ic("flame","s")} viene de la tendencia «${esc(v.tendencia)}»`:""}${v.idea?` · ${ic("idea","s")} idea del banco`:""}</div></div>${(v.tags||[]).length?`<div class="chips">${v.tags.map(t=>`<span class="pill">#${esc(t)}</span>`).join("")}</div>`:""}</div>
   <div style="margin:12px 0 4px">${semaforo(v)}</div>
   ${v.ganchos?.length?`<label>Elige el gancho (primera frase)</label><div class="chips" id="gk_${v.id}">${v.ganchos.map((g,i)=>`<button class="chip ${i===0?"on":""}" onclick="elegirGancho('${v.id}',${i})">${esc(g)}</button>`).join("")}</div>`:""}
   <label>Guion (lo que dirá la voz). Puedes editarlo antes de aprobar.</label><textarea id="g_${v.id}" style="min-height:190px">${esc(v.guion)}</textarea>
   <label>Texto del post</label><textarea id="t_${v.id}" style="min-height:58px">${esc(v.texto)}</textarea>
   ${v.nota_guion?`<div class="msg info">${ic("info","s")}Pediste: ${esc(v.nota_guion)}</div>`:""}
   <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px"><button class="btn ok" onclick="aprobarGuion('${v.id}')">${ic("check","s")}Aprobar guion</button><button class="btn sec" onclick="otraVersion('${v.id}')">${ic("refresh","s")}Pedir otra versión</button><button class="btn fantasma" onclick="descartar('${v.id}')">${ic("trash","s")}Descartar</button></div></div>`}).join("");
}
function elegirGancho(id,i){const v=PROD.find(x=>x.id===id),ta=$("#g_"+id),g=ta.value,resto=g.replace(/^.*?[.?!…](\s|$)/,"");ta.value=v.ganchos[i]+" "+resto;
  $$(`#gk_${id} .chip`).forEach((b,k)=>b.classList.toggle("on",k===i))}
function prodBorradores(rev){
  const vid=n=>`https://github.com/${O}/${R}/releases/download/videos/${n}`;
  if(!rev.length)return `<div class="card">${vacio("eye","No hay borradores por revisar","Cuando un vídeo termine de renderizarse aparecerá aquí.")}</div>`;
  return `<div class="grid g2">`+rev.map(v=>`<div class="card fade"><b style="font-size:16px;font-family:'Space Grotesk'">${esc(v.titulo)}</b>
   <div class="mut peq">${v.duracion?v.duracion+" s · ":""}formato ${esc(v.formato||"")}${v.aprobado_por?` · guion aprobado por ${esc(v.aprobado_por.split("_")[0])}`:""}</div>
   <video controls preload="metadata" playsinline src="${vid(v.id+".mp4")}"></video>
   <details><summary>Texto del post</summary><p class="peq">${esc(v.texto)}</p></details>
   <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px"><button class="btn ok" onclick="aprobarVideo('${v.id}')">${ic("check","s")}Aprobar y programar</button><button class="btn sec" onclick="rehacer('${v.id}')">${ic("edit","s")}Pedir cambios</button><button class="btn fantasma" onclick="descartar('${v.id}')">${ic("trash","s")}Descartar</button></div></div>`).join("")+`</div>`;
}
function prodHistorial(){
  const hech=PROD.filter(v=>["programado","rechazado"].includes(v.estado)).slice(-40).reverse();
  return `<div class="card fade">`+(hech.map(v=>`<div class="fila"><span class="t"><b>${esc(v.titulo)}</b><small><span class="pill ${v.estado==="programado"?"ok":""}">${FASES[v.estado]}</span>${v.programado_por?`por ${esc(v.programado_por.split("_")[0])}`:""}${v.duracion?` · ${v.duracion} s`:""}</small></span></div>`).join("")||vacio("film","Aún no hay historial"))+`</div>`;
}
function prodIdeas(ideas){
  const pend=ideas.filter(i=>i.estado!=="usada"),usadas=ideas.filter(i=>i.estado==="usada");
  return `<div class="card fade"><div class="h3">${ic("idea")}Ideas pendientes<span class="sub">Claude las convierte en guiones en su próxima pasada, empezando por las de prioridad alta</span></div>
   ${pend.length?pend.map(i=>`<div class="fila"><span class="pill ${i.prioridad==="alta"?"acc":""}">${i.prioridad||"normal"}</span><span class="t"><b>${esc(i.texto)}</b><small>${esc(i.origen||"manual")}${i.por?` · ${esc(i.por.split("_")[0])}`:""} · ${hace(i.fecha)}${i.notas?` · ${esc(i.notas)}`:""}</small></span><button class="ib peligro" title="Quitar" onclick="quitarIdea('${i.id}')">${ic("trash","s")}</button></div>`).join("")
     :vacio("idea","El banco está vacío","Apunta aquí temas que se te ocurran (o que pidan en comentarios o salgan en tendencias).",`<button class="btn peq" onclick="nuevaIdea()">${ic("plus","s")}Añadir idea</button>`)}</div>
   ${usadas.length?`<div class="card plano"><details><summary>Ya convertidas en guion (${usadas.length})</summary>${usadas.slice(-20).reverse().map(i=>`<div class="fila"><span class="t"><b>${esc(i.texto)}</b><small>${esc(i.guion||"")}</small></span></div>`).join("")}</details></div>`:""}`;
}
async function nuevaIdea(texto="",extra={}){
  const t=await pedir("Nueva idea de vídeo",{texto:"Un tema, una pregunta o un objeto. Claude lo comprobará con las 3 reglas antes de escribir el guion.",valor:texto,placeholder:"¿Cómo sabe el móvil dónde lo tocas?",si:"Añadir al banco"});
  if(!t)return;
  await accion(()=>editarJson("produccion/ideas.json",d=>{d.ideas.push({id:"i"+Date.now().toString(36),texto:t,prioridad:extra.prioridad||"normal",origen:extra.origen||"manual",notas:extra.notas||"",por:usuario,fecha:new Date().toISOString(),estado:"pendiente"})},`Panel: idea nueva [skip ci]`,{crear:{ideas:[]}}),"Idea guardada. Claude la usará en la próxima pasada.",{recargar:RUTA.s==="prod"});
}
async function quitarIdea(id){if(!await confirmar("¿Quitar esta idea?","",{si:"Quitar",peligro:true}))return;await accion(()=>editarJson("produccion/ideas.json",d=>{d.ideas=d.ideas.filter(i=>i.id!==id)},"Panel: idea quitada [skip ci]"),"Idea quitada")}
async function aprobarGuion(id){const g=$("#g_"+id).value.trim(),t=$("#t_"+id).value.trim();
  await accion(()=>editarJson("produccion/estado.json",d=>{const v=d.videos.find(x=>x.id===id);v.guion=g;v.texto=t;v.estado="aprobado";v.aprobado=new Date().toISOString();v.aprobado_por=usuario;delete v.nota_guion},`Panel: guion aprobado ${id}`),"Guion aprobado. La voz se genera en unos minutos.")}
async function otraVersion(id){const n=await pedir("¿Qué cambiarías del guion?",{texto:"Claude lo reescribirá en la próxima pasada.",largo:true,chips:["Gancho más fuerte","Más cifras que se puedan enseñar","Menos palabras","Tema más cotidiano","Otro formato","Más sorpresa a mitad"]});if(!n)return;
  await accion(()=>editarJson("produccion/estado.json",d=>{d.videos.find(x=>x.id===id).nota_guion=n},`Panel: otra versión del guion ${id}`),"Anotado. Claude lo reescribirá en la próxima pasada.")}
async function descartar(id){if(!await confirmar("¿Descartar este vídeo?","No se borra, pasa al historial como descartado.",{si:"Descartar",peligro:true}))return;await accion(()=>editarJson("produccion/estado.json",d=>{d.videos.find(x=>x.id===id).estado="rechazado"},`Panel: descartado ${id}`),"Descartado")}
async function rehacer(id){const nota=await pedir("¿Qué hay que cambiar?",{texto:"Marca uno o varios cambios rápidos o escríbelo con tus palabras. Claude lo corregirá en la próxima pasada.",largo:true,chips:CAMBIOS_RAPIDOS});if(!nota)return;
  await accion(()=>editarJson("produccion/estado.json",d=>{const v=d.videos.find(x=>x.id===id);v.estado="rehacer";v.nota=nota},`Panel: cambios en ${id}`),"Anotado. Claude lo corregirá en la próxima pasada.")}
async function aprobarVideo(id){
  const v=PROD.find(x=>x.id===id);
  await accion(async()=>{
    await guardarCal(c=>{
      if(c.posts.some(x=>x.id===`${id}-tiktok`&&x.estado==="pendiente"))throw new Error("Este vídeo ya está programado");
      const ocup=[...c.posts],horas={};
      horas.tiktok=siguienteHueco("tiktok",ocup);
      const tt=new Date(aIso(horas.tiktok));
      for(const r of ["youtube","instagram"]){let h,ex=[...ocup];
        while((h=siguienteHueco(r,ex))&&new Date(aIso(h))<=tt)ex.push({red:r,hora:aIso(h)});horas[r]=h}
      for(const r of REDES)c.posts.push({id:`${id}-${r}`,red:r,hora:aIso(horas[r]),video:r==="tiktok"?`${id}_tiktok.mp4`:`${id}.mp4`,titulo:v.titulo,texto:v.texto,tags:v.tags||[],estado:"pendiente",intentos:0,por:usuario});
    },`Panel: programar ${id} (${usuario})`);
    await editarJson("produccion/estado.json",d=>{const q=d.videos.find(x=>x.id===id);q.estado="programado";q.programado_por=usuario},`Panel: vídeo aprobado ${id} [skip ci]`);
  },"Programado en TikTok, Instagram y YouTube.");
}
