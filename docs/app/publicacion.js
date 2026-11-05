// ═══════════ Publicación ═══════════
let SEMANA=0;
async function vistaPub(sub){
  await cargarCal();
  const iss=await gh("/issues?state=open&per_page=50").catch(()=>[]);
  const tt=iss.filter(i=>!i.pull_request&&/tiktok/i.test(i.title));
  acciones(`<a class="btn sec" href="#/pub/subir">${ic("upload","s")}Subir vídeo propio</a>`);
  const fallos=cal.posts.filter(p=>p.estado==="error"||p.estado==="caducado").length;
  let h=segmentos("pub",[["semana","Semana"],["lista","Lista",fallos,true],["tiktok","Borradores de TikTok",tt.length],["subir","Subir vídeo"]],sub);
  if(sub==="lista")h+=pubLista();
  else if(sub==="tiktok")h+=pubTikTok(tt);
  else if(sub==="subir"){app.innerHTML=h+pubSubir();prepararSubir();return}
  else h+=pubSemana();
  app.innerHTML=h;
  if(sub==="semana"||!sub)despuesDePintar=prepararSemana;
}

// ── Vista semanal con arrastrar y soltar ──
function lunes(offset){const p=partes(new Date());const hoy=new Date(Date.UTC(+p.year,p.month-1,+p.day));const dow=(hoy.getUTCDay()+6)%7;return new Date(hoy.getTime()-(dow-offset*7)*864e5)}
function pubSemana(){
  const L=lunes(SEMANA),dias=Array.from({length:7},(_,i)=>new Date(L.getTime()+i*864e5)),claves=dias.map(d=>d.toISOString().slice(0,10));
  const hoyK=diaClave(new Date()),H0=8,H1=23;
  const posts=cal.posts.filter(p=>claves.includes(diaClave(new Date(p.hora))));
  const choque=p=>cal.posts.some(q=>q!==p&&q.red===p.red&&q.estado==="pendiente"&&p.estado==="pendiente"&&Math.abs(new Date(q.hora)-new Date(p.hora))<30*60000);
  const tarjeta=p=>{const i=cal.posts.indexOf(p),mov=!["publicado","borrador"].includes(p.estado);
    return `<div class="post ${p.red} ${mov?"":"hecho"} ${choque(p)?"choque":""}" ${mov?`draggable="true"`:""} data-i="${i}" title="${esc(p.titulo)}"><b>${esc(p.titulo)}</b><small><span>${fmtHora(p.hora)} · ${NOMBRE[p.red]}</span><span>${p.estado==="publicado"?"✓":p.estado==="borrador"?"📲":p.estado==="pendiente"?"":"⚠"}</span></small></div>`};
  let g=`<div class="semana"><div class="cab"></div>${dias.map((d,i)=>`<div class="cab ${claves[i]===hoyK?"hoy":""}">${DIAS[i]}<b>${d.getUTCDate()}</b></div>`).join("")}`;
  for(let h=H0;h<=H1;h++){
    g+=`<div class="hh">${String(h).padStart(2,"0")}:00</div>`;
    claves.forEach((k,i)=>{const enCelda=posts.filter(p=>diaClave(new Date(p.hora))===k&&(Math.max(H0,Math.min(H1,horaMadrid(p.hora))))===h);
      const hueco=REDES.some(r=>HUECOS[r].includes(h)),pas=new Date(aIso(`${k}T${String(h).padStart(2,"0")}:59`))<new Date();
      g+=`<div class="celda ${hueco?"hueco":""} ${pas?"pasado":""}" data-d="${k}" data-h="${h}">${enCelda.map(tarjeta).join("")}</div>`});
  }
  g+=`</div>`;
  const pend=posts.filter(p=>p.estado==="pendiente").length,pub=posts.filter(p=>p.estado==="publicado"||p.estado==="borrador").length;
  return `<div class="card fade" style="padding:14px">
   <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:12px"><button class="ib" onclick="SEMANA--;ir('pub','semana',true)" title="Semana anterior">${ic("left","s")}</button>
    <b style="font-family:'Space Grotesk';font-size:15px">${dias[0].getUTCDate()} – ${dias[6].getUTCDate()} de ${dias[6].toLocaleDateString("es-ES",{month:"long",timeZone:"UTC"})}</b>
    <button class="ib" onclick="SEMANA++;ir('pub','semana',true)" title="Semana siguiente">${ic("right","s")}</button>
    ${SEMANA?`<button class="btn fantasma peq" onclick="SEMANA=0;ir('pub','semana',true)">Hoy</button>`:""}
    <span class="pill">${pend} programados</span><span class="pill ok">${pub} publicados</span>
    <span class="mut peq" style="margin-left:auto">Arrastra una publicación a otra hora para moverla · las franjas rayadas son tus horas habituales</span></div>
   <div class="semana-wrap">${g}</div></div>`;
}
function prepararSemana(){
  let arr=null;
  $$(".post").forEach(el=>{const p=cal.posts[+el.dataset.i];
    el.onclick=()=>detallePost(p);
    el.ondragstart=e=>{arr=p;el.classList.add("arrastrando");e.dataTransfer.effectAllowed="move";e.dataTransfer.setData("text/plain",p.id)};
    el.ondragend=()=>{el.classList.remove("arrastrando");$$(".celda.sobre").forEach(c=>c.classList.remove("sobre"))}});
  $$(".celda").forEach(c=>{
    c.ondragover=e=>{if(arr){e.preventDefault();c.classList.add("sobre")}};c.ondragleave=()=>c.classList.remove("sobre");
    c.ondrop=async e=>{e.preventDefault();c.classList.remove("sobre");if(!arr)return;const p=arr;arr=null;
      const loc=`${c.dataset.d}T${String(c.dataset.h).padStart(2,"0")}:00`;if(new Date(aIso(loc))<new Date()){toast("No se puede mover al pasado","err");return}
      await accion(()=>guardarCal(k=>{const q=k.posts.find(x=>x.id===p.id&&x.hora===p.hora)||k.posts.find(x=>x.id===p.id);q.hora=aIso(loc);q.estado="pendiente";q.intentos=0;delete q.ultimo_error},`Panel: mover ${p.id}`),`Movido a ${fmtDiaC(aIso(loc))}, ${c.dataset.h}:00`)}});
}
async function detallePost(p){
  const mov=!["publicado","borrador"].includes(p.estado),url=p.resultado?.url;
  const r=await modal(`<div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">${redPill(p.red)}<span class="pill ${EST_PILL[p.estado]||""}">${EST[p.estado]||p.estado}</span></div>
    <h3>${esc(p.titulo)}</h3><p class="mut peq" style="margin:0 0 10px">${fmtDia(p.hora)}, ${fmtHora(p.hora)}${p.por?` · aprobado por ${esc(p.por.split("_")[0])}`:""}</p>
    ${p.ultimo_error&&p.estado!=="publicado"?`<div class="msg err">${ic("alert","s")}${esc(p.ultimo_error)}</div>`:""}
    <pre>${esc(p.texto)}${(p.tags||[]).length?"\n\n"+p.tags.map(t=>"#"+t).join(" "):""}</pre>
    ${mov?`<label>Cambiar fecha y hora</label><input id="nh" type="datetime-local" value="${aLocal(p.hora)}">`:""}
    <div class="pie" style="flex-wrap:wrap">${url?`<a class="btn sec" href="${esc(url)}" target="_blank">${ic("ext","s")}Ver publicado</a>`:""}
     <button class="btn sec" data-r="copiar">${ic("copy","s")}Copiar texto</button>
     ${mov?`<button class="btn peligro" data-r="quitar">${ic("trash","s")}Quitar</button><button class="btn sec" data-r="ya">${ic("play","s")}Publicar ya</button><button class="btn" data-r="mover">Guardar hora</button>`:`<button class="btn" data-r="">Cerrar</button>`}</div>`,
    {alAbrir:(m,c)=>m.querySelectorAll("[data-r]").forEach(b=>b.onclick=()=>c({a:b.dataset.r,h:m.querySelector("#nh")?.value}))});
  if(!r||!r.a)return;
  if(r.a==="copiar")return copiar(p.texto+((p.tags||[]).length?"\n\n"+p.tags.map(t=>"#"+t).join(" "):""));
  if(r.a==="quitar")return quitarPost(p);
  if(r.a==="ya")return yaa(p);
  if(r.a==="mover"&&r.h)return accion(()=>guardarCal(k=>{const q=k.posts.find(x=>x.id===p.id&&x.hora===p.hora)||k.posts.find(x=>x.id===p.id);q.hora=aIso(r.h);q.estado="pendiente";q.intentos=0;delete q.ultimo_error},`Panel: mover ${p.id}`),"Hora cambiada");
}
async function quitarPost(p){if(!await confirmar("¿Quitar esta publicación del calendario?",esc(p.titulo),{si:"Quitar",peligro:true}))return;await accion(()=>guardarCal(c=>{c.posts=c.posts.filter(x=>!(x.id===p.id&&x.hora===p.hora))},`Panel: quitar ${p.id}`),"Quitada del calendario")}
async function yaa(p){if(!await confirmar("¿Publicar ahora mismo?",`${esc(p.titulo)} en ${NOMBRE[p.red]}`,{si:"Publicar ya"}))return;
  await accion(async()=>{await guardarCal(c=>{const q=c.posts.find(x=>x.id===p.id&&x.hora===p.hora)||c.posts.find(x=>x.id===p.id);q.hora=new Date(Date.now()-60000).toISOString().replace(/\.\d+Z$/,"+00:00");q.estado="pendiente";q.intentos=0},`Panel: publicar ya ${p.id}`);await lanzar(false)},"Enviado. Se publicará en 1-3 minutos.")}

// ── Lista ──
function pubLista(){
  const desde=Date.now()-3*864e5,posts=[...cal.posts].sort((a,b)=>new Date(a.hora)-new Date(b.hora)).filter(p=>p.estado==="pendiente"||new Date(p.hora)>desde);
  if(!posts.length)return `<div class="card">${vacio("cal","No hay nada programado","",`<a class="btn peq" href="#/pub/subir">Subir un vídeo</a>`)}</div>`;
  let h="",dia="";
  posts.forEach(p=>{const d=fmtDia(p.hora),i=cal.posts.indexOf(p);if(d!==dia){h+=(dia?"</div>":"")+`<div class="etiqueta" style="margin:18px 4px 8px">${d}</div><div class="card fade" style="padding:6px 16px">`;dia=d}
    const mov=!["publicado","borrador"].includes(p.estado);
    h+=`<div class="fila"><span class="hora">${fmtHora(p.hora)}</span>${redPill(p.red)}<span class="t"><b>${esc(p.titulo)}</b><small><span class="pill ${EST_PILL[p.estado]||""}">${EST[p.estado]||p.estado}</span>${p.resultado?.url?`<a href="${esc(p.resultado.url)}" target="_blank">ver</a>`:""}${p.ultimo_error&&p.estado!=="publicado"?`<span style="color:var(--err)" title="${esc(p.ultimo_error)}">${esc(p.ultimo_error.slice(0,70))}</span>`:""}</small></span>
     <span style="display:flex;gap:6px">${mov?`<button class="ib" title="Publicar ya" onclick="yaa(cal.posts[${i}])">${ic("play","s")}</button>`:""}<button class="ib" title="Detalles" onclick="detallePost(cal.posts[${i}])">${ic("edit","s")}</button></span></div>`});
  return h+"</div>";
}

// ── Borradores de TikTok ──
let TEXTOS=[];
function pubTikTok(iss){
  if(!iss.length)return `<div class="card">${vacio("check","No hay borradores pendientes","Cuando un vídeo llegue a tu bandeja de TikTok, aquí tendrás el texto listo para copiar.")}</div>`;
  TEXTOS=[];
  return `<div class="msg info">${ic("info","s")}<div>TikTok solo deja enviar el vídeo como borrador. Abre la app → bandeja de entrada → «Tu vídeo está listo», pega el texto y publica. Después pulsa «Hecho».</div></div>`+
   iss.map(i=>{const m=(i.body||"").match(/```\n?([\s\S]*?)```/),txt=m?m[1].trim():"",k=TEXTOS.push(txt)-1;
    return `<div class="card fade"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap"><b>${esc(i.title)}</b><span class="mut peq">${hace(i.created_at)}</span></div>
    ${txt?`<pre>${esc(txt)}</pre>`:""}<div style="display:flex;gap:8px;flex-wrap:wrap">${txt?`<button class="btn" onclick="copiar(TEXTOS[${k}])">${ic("copy","s")}Copiar texto</button>`:""}<button class="btn sec" onclick="cerrarAviso(${i.number})">${ic("check","s")}Hecho, ya está publicado</button></div></div>`}).join("");
}
async function cerrarAviso(n){await accion(()=>gh(`/issues/${n}`,{method:"PATCH",body:JSON.stringify({state:"closed"})}),"Marcado como hecho");contadores()}

// ── Subir vídeo propio ──
function pubSubir(){
  return `<div class="card fade" style="max-width:760px">
  <label for="ti">Título</label><input id="ti" maxlength="100" placeholder="Así funciona un termo ☕">
  <label for="tx">Descripción</label><textarea id="tx" placeholder="Texto del post. Los hashtags se añaden solos."></textarea>
  <label for="tg">Hashtags (separados por comas, sin #)</label><input id="tg" placeholder="termo, física, curiosidades">
  <div class="grid g2" style="margin:0"><div><label for="v1">Vídeo (Instagram y YouTube)</label><input id="v1" type="file" accept="video/mp4"></div>
  <div><label for="v2">Vídeo con música para TikTok <span class="faint">(opcional)</span></label><input id="v2" type="file" accept="video/mp4"></div></div>
  <label>Dónde y cuándo (hora de Madrid)</label>
  ${REDES.map(r=>`<div style="display:grid;grid-template-columns:auto 110px minmax(0,1fr);gap:10px;align-items:center;margin:8px 0"><input type="checkbox" id="c_${r}" checked style="width:18px;height:18px;accent-color:var(--acc)">${redPill(r)}<input type="datetime-local" id="h_${r}"></div>`).join("")}
  <p class="mut peq">Se rellenan solos con el siguiente hueco libre de tu horario. Puedes cambiarlos.</p>
  <div id="nmsg"></div><button class="btn" id="prog">${ic("upload","s")}Programar</button></div>`;
}
function prepararSubir(){REDES.forEach(r=>{$("#h_"+r).value=siguienteHueco(r,cal.posts)||""});$("#prog").onclick=programar}
function slug(t){return t.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_|_$/g,"").slice(0,40)||"video"}
async function programar(){
  const msg=(t,c="info")=>$("#nmsg").innerHTML=`<div class="msg ${c}">${t}</div>`;
  const titulo=$("#ti").value.trim(),texto=$("#tx").value.trim(),tags=$("#tg").value.split(",").map(s=>s.trim().replace(/^#/,"")).filter(Boolean);
  const v1=$("#v1").files[0],v2=$("#v2").files[0],redes=REDES.filter(r=>$("#c_"+r).checked);
  if(!titulo||!texto)return msg("Falta el título o la descripción.","err");
  if(!v1)return msg("Falta el vídeo.","err");
  if(!redes.length)return msg("Elige al menos una red.","err");
  for(const r of redes)if(!$("#h_"+r).value)return msg(`Falta la hora de ${NOMBRE[r]}.`,"err");
  const base=slug(titulo)+"_"+Date.now().toString(36).slice(-4),n1=base+".mp4",n2=base+"_tiktok.mp4";
  const subir={[n1]:v1};if(v2&&redes.includes("tiktok"))subir[n2]=v2;
  $("#prog").disabled=true;
  try{msg("Subiendo el vídeo… no cierres la página.");await subirVideos(subir,t=>msg(t));
    msg("Guardando en el calendario…");
    await guardarCal(c=>{for(const r of redes)c.posts.push({id:`${base}-${r}`,red:r,hora:aIso($("#h_"+r).value),video:(r==="tiktok"&&subir[n2])?n2:n1,titulo,texto,tags,estado:"pendiente",intentos:0,por:usuario})},`Panel: programar ${titulo}`);
    toast(`Programado en ${redes.map(r=>NOMBRE[r]).join(", ")}`);ir("pub","semana");
  }catch(e){msg("No se pudo: "+esc(e.message),"err");$("#prog").disabled=false}
}
async function subirVideos(archivos,progreso){
  try{const rel=await gh("/releases/tags/videos");
    for(const [n,f] of Object.entries(archivos)){progreso(`Subiendo ${n} (${(f.size/1048576).toFixed(1)} MB)…`);
      const r=await fetch(`https://uploads.github.com/repos/${O}/${R}/releases/${rel.id}/assets?name=${encodeURIComponent(n)}`,{method:"POST",headers:{Authorization:`Bearer ${tok}`,"Content-Type":"video/mp4"},body:f});
      if(!r.ok)throw new Error("release "+r.status)}
    return;
  }catch(e){if(e.status===401)throw e;console.log("Subida directa no disponible:",e.message)}
  progreso("Subiendo por la vía alternativa…");
  const main=await gh("/git/ref/heads/main"),com=await gh(`/git/commits/${main.object.sha}`),arbol=[];
  for(const [n,f] of Object.entries(archivos)){progreso(`Subiendo ${n} (${(f.size/1048576).toFixed(1)} MB)…`);
    const b64=await new Promise((ok,ko)=>{const fr=new FileReader();fr.onload=()=>ok(fr.result.split(",")[1]);fr.onerror=ko;fr.readAsDataURL(f)});
    const bl=await gh("/git/blobs",{method:"POST",body:JSON.stringify({content:b64,encoding:"base64"})});arbol.push({path:`subida/${n}`,mode:"100644",type:"blob",sha:bl.sha})}
  const tr=await gh("/git/trees",{method:"POST",body:JSON.stringify({base_tree:com.tree.sha,tree:arbol})});
  const nc=await gh("/git/commits",{method:"POST",body:JSON.stringify({message:"Vídeos nuevos desde el panel",tree:tr.sha,parents:[main.object.sha]})});
  try{await gh("/git/refs/heads/subida",{method:"PATCH",body:JSON.stringify({sha:nc.sha,force:true})})}catch(e){await gh("/git/refs",{method:"POST",body:JSON.stringify({ref:"refs/heads/subida",sha:nc.sha})})}
}
