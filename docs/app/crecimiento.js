// ═══════════ Crecimiento ═══════════
function serieMetrica(hist,red,metrica){return (hist||[]).map(h=>({f:h.fecha,v:red==="todas"?REDES.reduce((s,r)=>s+(h[r+"_"+metrica]||0),0):h[red+"_"+metrica]})).filter(x=>x.v!=null)}
function pendiente(puntos){ // regresión lineal (valor por día) con los últimos 14 días
  const p=puntos.slice(-14);if(p.length<2)return null;const t0=new Date(p[0].f).getTime(),xs=p.map(q=>(new Date(q.f).getTime()-t0)/864e5),ys=p.map(q=>q.v);
  const mx=xs.reduce((a,b)=>a+b)/xs.length,my=ys.reduce((a,b)=>a+b)/ys.length;let num=0,den=0;xs.forEach((x,i)=>{num+=(x-mx)*(ys[i]-my);den+=(x-mx)**2});return den?num/den:null}
function progresoObjetivo(o,st){
  const actual=o.red==="todas"?REDES.reduce((s,r)=>s+(st?.cuentas?.[r]?.[o.metrica]||0),0):(st?.cuentas?.[o.red]?.[o.metrica]||0);
  const serie=serieMetrica(st?.historial,o.red,o.metrica),m=pendiente(serie),falta=o.meta-actual;
  const diasLimite=Math.max(0,(new Date(o.fecha)-Date.now())/864e5),necesita=diasLimite?falta/diasLimite:null;
  let prevision;
  if(falta<=0)prevision="¡Conseguido! 🎉";
  else if(m==null||m<=0)prevision=`Faltan ${fmtN(falta)}. Necesitas unos ${fmtN(Math.ceil(necesita||0))} al día hasta el ${new Date(o.fecha).toLocaleDateString("es-ES",{day:"numeric",month:"long"})}.`;
  else{const d=falta/m,llega=new Date(Date.now()+d*864e5);prevision=`Al ritmo actual (+${fmtN(m)} al día) llegas el ${llega.toLocaleDateString("es-ES",{day:"numeric",month:"long",year:llega.getFullYear()!==new Date().getFullYear()?"numeric":undefined})}${llega>new Date(o.fecha)?` · tarde: necesitas +${fmtN(Math.ceil(necesita))} al día`:" · a tiempo ✓"}.`}
  return {actual,ritmo:m,necesita,prevision,serie};
}
// vídeos de las últimas 72 h que van mucho mejor que otros de su red a la misma edad
function despegando(series){
  if(!series)return [];
  const ahora=Date.now(),vals=Object.values(series);
  const vistasAEdad=(s,h)=>{const t0=new Date(s.fecha).getTime();let mejor=null;for(const [t,v] of s.p){const e=(new Date(t).getTime()-t0)/36e5;if(e<=h+1.5)mejor=v;else break}return mejor};
  const out=[];
  for(const s of vals){const edad=(ahora-new Date(s.fecha))/36e5;if(edad>72||edad<1||!s.p.length)continue;
    const act=s.p[s.p.length-1][1],otros=vals.filter(o=>o!==s&&o.red===s.red&&(ahora-new Date(o.fecha))/36e5>edad);
    const esp=mediana(otros.map(o=>vistasAEdad(o,edad)).filter(v=>v!=null));
    const ult=s.p.slice(-4),ritmo=ult.length>1?(ult[ult.length-1][1]-ult[0][1])/((new Date(ult[ult.length-1][0])-new Date(ult[0][0]))/36e5||1):null;
    if(esp&&otros.length>=3)out.push({...s,vistas:act,horas:edad,esperado:esp,ratio:act/esp,ritmo})}
  return out.filter(x=>x.ratio>=1.8).sort((a,b)=>b.ratio-a.ratio);
}
async function vistaCrec(sub){
  const [st,obj,series,raw,est]=await Promise.all([json("programador/estadisticas.json",{opcional:true}),json("produccion/objetivos.json",{opcional:true}),json("programador/series.json",{opcional:true}),json("programador/tendencias_raw.json",{opcional:true}),json("produccion/estado.json")]);
  const desp=despegando(series);
  let h=segmentos("crec",[["objetivos","Objetivos"],["despegan","Vídeos que despegan",desp.length],["horas","Horas muertas"],["competencia","Competencia"]],sub);
  if(sub==="despegan")h+=crecDespegan(series,desp);
  else if(sub==="horas")h+=crecHoras(st,est);
  else if(sub==="competencia")h+=crecCompetencia(obj,raw,st);
  else h+=crecObjetivos(obj,st);
  app.innerHTML=h;
  if(!sub||sub==="objetivos")despuesDePintar=()=>(obj?.objetivos||[]).forEach(o=>{const el=$("#g_"+o.id);if(!el)return;const p=progresoObjetivo(o,st),xs=p.serie.map(x=>x.f);
    let proy=null;if(p.ritmo>0&&p.serie.length){const u=p.serie[p.serie.length-1];const fin=new Date(o.fecha).toISOString().slice(0,10);if(fin>u.f){proy=[{x:u.f,v:u.v},{x:fin,v:u.v+p.ritmo*(new Date(fin)-new Date(u.f))/864e5}];xs.push(fin)}}
    grafLineas(el,[{nombre:"Real",color:o.red==="todas"?"#ffd23f":COLOR[o.red],p:p.serie.map(x=>({x:x.f,v:x.v}))}],xs,{alto:150,etX:f=>`${+f.slice(8)}/${+f.slice(5,7)}`,etiquetaFinal:false,proyeccion:proy})});
}
function crecObjetivos(obj,st){
  acciones(`<button class="btn" onclick="editarObjetivo()">${ic("plus","s")}Nuevo objetivo</button>`);
  const os=obj?.objetivos||[];
  if(!os.length)return `<div class="card">${vacio("target","Sin objetivos","Ponte una meta (por ejemplo 1.000 seguidores en TikTok) y verás si llegas a tiempo.")}</div>`;
  return `<div class="grid g2">${os.map(o=>{const p=progresoObjetivo(o,st),pc=Math.min(100,p.actual/o.meta*100);return `<div class="card fade">
   <div style="display:flex;align-items:center;gap:8px">${redPill(o.red)}<b style="font-family:'Space Grotesk';font-size:16px">${fmtN(o.meta)} ${o.metrica==="seguidores"?"seguidores":"visualizaciones"}</b><span class="mut peq">antes del ${new Date(o.fecha).toLocaleDateString("es-ES",{day:"numeric",month:"short",year:"numeric"})}</span>
   <span style="margin-left:auto;display:flex;gap:4px"><button class="ib" title="Editar" onclick="editarObjetivo('${o.id}')">${ic("edit","s")}</button><button class="ib peligro" title="Quitar" onclick="quitarObjetivo('${o.id}')">${ic("trash","s")}</button></span></div>
   <div style="display:flex;align-items:baseline;gap:10px;margin:12px 0 8px"><span style="font:700 30px 'Space Grotesk'" class="num">${fmtN(p.actual)}</span><span class="mut">${pc.toFixed(0)} %</span></div>
   <div class="barra"><i style="width:${pc}%"></i></div><p class="mut peq" style="margin:8px 0 0">${esc(p.prevision)}</p>
   <div class="chart" id="g_${o.id}" style="margin-top:10px"></div></div>`}).join("")}</div>`;
}
async function editarObjetivo(id){
  const obj=(await json("produccion/objetivos.json",{opcional:true,ttl:0}))||{objetivos:[],competencia:[]},o=obj.objetivos.find(x=>x.id===id)||{red:"tiktok",metrica:"seguidores",meta:1000,fecha:new Date(Date.now()+60*864e5).toISOString().slice(0,10)};
  const r=await modal(`<h3>${id?"Editar":"Nuevo"} objetivo</h3>
   <div class="grid g2" style="margin:0"><div><label>Red</label><select id="or">${["todas",...REDES].map(x=>`<option value="${x}" ${o.red===x?"selected":""}>${NOMBRE[x]}</option>`).join("")}</select></div>
   <div><label>Métrica</label><select id="om"><option value="seguidores" ${o.metrica==="seguidores"?"selected":""}>Seguidores</option><option value="vistas" ${o.metrica==="vistas"?"selected":""}>Visualizaciones</option></select></div>
   <div><label>Meta</label><input id="on" type="number" min="1" value="${o.meta}"></div><div><label>Fecha límite</label><input id="of" type="date" value="${o.fecha}"></div></div>
   <div class="pie"><button class="btn sec" data-r="0">Cancelar</button><button class="btn" data-r="1">Guardar</button></div>`,
   {alAbrir:(m,c)=>m.querySelectorAll("[data-r]").forEach(b=>b.onclick=()=>c(b.dataset.r==="1"?{red:m.querySelector("#or").value,metrica:m.querySelector("#om").value,meta:+m.querySelector("#on").value,fecha:m.querySelector("#of").value}:null))});
  if(!r||!r.meta||!r.fecha)return;
  await accion(()=>editarJson("produccion/objetivos.json",d=>{d.objetivos=d.objetivos||[];const x=d.objetivos.find(z=>z.id===id);if(x)Object.assign(x,r);else d.objetivos.push({id:"o"+Date.now().toString(36),...r})},"Panel: objetivo [skip ci]",{crear:{objetivos:[],competencia:[]}}),"Objetivo guardado")}
async function quitarObjetivo(id){if(!await confirmar("¿Quitar este objetivo?","",{si:"Quitar",peligro:true}))return;await accion(()=>editarJson("produccion/objetivos.json",d=>{d.objetivos=d.objetivos.filter(x=>x.id!==id)},"Panel: objetivo quitado [skip ci]"),"Objetivo quitado")}

function crecDespegan(series,desp){
  const recientes=series?Object.values(series).filter(s=>(Date.now()-new Date(s.fecha))/36e5<=72&&s.p.length).sort((a,b)=>new Date(b.fecha)-new Date(a.fecha)):[];
  return `<div class="msg info">${ic("info","s")}<div>Cada hora se apuntan las vistas de cada vídeo. Si uno de los últimos 3 días va <b>al menos 1,8 veces mejor</b> que tus otros vídeos a la misma edad, aparece aquí (y en el Resumen). Es el momento de responder comentarios, fijarlo en el perfil y preparar una segunda parte.</div></div>
  <div class="card fade"><div class="h3">${ic("rocket")}Despegando ahora</div>${desp.length?desp.map(d=>`<div class="fila">${redPill(d.red)}<span class="t"><b>${esc(d.titulo)}</b><small>${fmtN(d.vistas)} vistas en ${Math.round(d.horas)} h · lo normal a esa edad: ${fmtN(d.esperado)}${d.ritmo?` · ahora +${fmtN(d.ritmo)}/h`:""}</small></span><span class="pill ok">${fmtX(d.ratio)}</span>${d.url?`<a class="ib" href="${esc(d.url)}" target="_blank">${ic("ext","s")}</a>`:""}</div>`).join(""):vacio("rocket","Ningún vídeo despegando ahora mismo","Con más historial por hora la detección será más fina.")}</div>
  <div class="card fade"><div class="h3">${ic("clock")}Últimos 3 días, hora a hora</div>${recientes.length?recientes.map(s=>`<div class="fila">${redPill(s.red)}<span class="t"><b>${esc(s.titulo)}</b><small>publicado ${hace(s.fecha)} · ${fmtN(s.p[s.p.length-1][1])} vistas</small></span><div style="width:140px">${sparkline(s.p.map(x=>x[1]),COLOR[s.red],32)}</div></div>`).join(""):vacio("chart","Sin vídeos recientes con historial")}</div>`;
}
function crecHoras(st,est){
  const vids=videosDe(st,est).filter(v=>v.maduro),porRed=REDES.map(r=>{const v=vids.filter(x=>x.red===r),hr=horasRanking(v);return {r,hr,flojas:hr.filter(x=>x.n>=2&&x.m<.7),buenas:hr.filter(x=>x.n>=2&&x.m>=1.2)}});
  return `<div class="msg info">${ic("info","s")}<div>Horas en las que publicar rinde menos de 0,7 veces lo normal (con al menos 2 vídeos). Gastar un vídeo ahí es desperdiciarlo: muévelo a una hora buena.</div></div>
  <div class="grid g3">${porRed.map(({r,hr,flojas,buenas})=>`<div class="card fade"><div class="h3">${redPill(r)}</div>
   <span class="etiqueta">Tu horario</span><div style="margin:6px 0 12px">${HUECOS[r].map(h=>{const x=hr.find(z=>z.h===h);return `<span class="pill ${x&&x.n>=2?(x.m>=1.2?"ok":x.m<.7?"err":""):""}" style="margin:2px">${h}:00${x?` · ${fmtX(x.m)}`:""}</span>`}).join("")}</div>
   <span class="etiqueta">Horas muertas</span>${flojas.length?flojas.map(x=>`<div class="fila"><span class="hora">${String(x.h).padStart(2,"0")}:00</span><span class="t"><b>${fmtX(x.m)} lo normal</b><small>${x.n} vídeos</small></span></div>`).join(""):`<p class="mut peq">Ninguna por ahora.</p>`}
   <span class="etiqueta" style="display:block;margin-top:10px">Horas que funcionan</span>${buenas.length?buenas.map(x=>`<div class="fila"><span class="hora">${String(x.h).padStart(2,"0")}:00</span><span class="t"><b>${fmtX(x.m)} lo normal</b><small>${x.n} vídeos</small></span></div>`).join(""):`<p class="mut peq">Aún no hay datos suficientes.</p>`}</div>`).join("")}</div>`;
}
function crecCompetencia(obj,raw,st){
  acciones(`<button class="btn" onclick="anadirCompetidor()">${ic("plus","s")}Vigilar un canal</button>`);
  const cs=raw?.competencia||[],nos=st?.cuentas?.youtube;
  return `<div class="msg info">${ic("info","s")}<div>Canales de YouTube que se vigilan (datos públicos, se actualizan a las 7:40 y 18:40). De TikTok e Instagram no se pueden leer cuentas ajenas con sus APIs.</div></div>
  ${(obj?.competencia||[]).length?"":`<div class="card">${vacio("eyes","No vigilas a nadie todavía","Añade canales parecidos al tuyo (por su @) para ver qué publican y qué les funciona.")}</div>`}
  ${cs.length?`<div class="card fade"><div class="tablewrap"><table><thead><tr><th>Canal</th><th class="n">Seguidores</th><th class="n">Vídeos</th><th class="n">Vistas totales</th><th class="n">Media últimos 10</th><th></th></tr></thead><tbody>
   ${nos?`<tr style="background:var(--acc-soft)"><td><b>Tú</b> · ${esc(nos.nombre)}</td><td class="n">${fmtN(nos.seguidores)}</td><td class="n">${fmtN(nos.videos)}</td><td class="n">${fmtN(nos.vistas)}</td><td class="n">—</td><td></td></tr>`:""}
   ${cs.map(c=>c.error?`<tr><td>${esc(c.canal)}</td><td colspan="4" class="mut">${esc(c.error)}</td><td><button class="ib peligro" onclick="quitarCompetidor('${esc(c.canal)}')">${ic("trash","s")}</button></td></tr>`:`<tr><td><b>${esc(c.nombre)}</b> <span class="faint">${esc(c.canal)}</span></td><td class="n">${fmtN(c.seguidores)}</td><td class="n">${fmtN(c.videos)}</td><td class="n">${fmtN(c.vistas)}</td><td class="n">${fmtN(mediana((c.ultimos||[]).map(v=>v.vistas)))}</td><td><button class="ib peligro" title="Dejar de vigilar" onclick="quitarCompetidor('${esc(c.canal)}')">${ic("trash","s")}</button></td></tr>`).join("")}</tbody></table></div></div>
  <div class="grid g2">${cs.filter(c=>c.ultimos?.length).map(c=>`<div class="card fade"><div class="h3">${esc(c.nombre)}<span class="sub">últimos vídeos</span></div>${[...c.ultimos].sort((a,b)=>b.vistas-a.vistas).map(v=>`<div class="fila"><span class="t"><a class="tt" style="color:var(--fg)" href="${esc(v.url)}" target="_blank">${esc(v.titulo)}</a><small>${hace(v.fecha)}</small></span><b class="num">${fmtN(v.vistas)}</b></div>`).join("")}</div>`).join("")}</div>`:""}
  ${(obj?.competencia||[]).length&&!cs.length?`<div class="card">${vacio("clock","Pendiente de la próxima recogida",`Vigilando: ${(obj.competencia).map(esc).join(", ")}`,`<button class="btn sec peq" onclick="accion(()=>lanzarFlujo('tendencias.yml'),'Recogiendo… 1-2 minutos.',{recargar:false})">Recoger ahora</button>`)}</div>`:""}
  ${raw?.nicho?.length?`<div class="card fade"><div class="h3">${ic("film")}Lo que más funciona en tu nicho esta semana<a class="sub" href="#/tend/senales">ver más</a></div>${raw.nicho.slice(0,6).map(v=>`<div class="fila"><span class="t"><a class="tt" style="color:var(--fg)" href="${esc(v.url)}" target="_blank">${esc(v.titulo)}</a><small>${esc(v.canal)} · ${hace(v.fecha)}</small></span><b class="num">${fmtN(v.vistas)}</b></div>`).join("")}</div>`:""}`;
}
async function anadirCompetidor(){const c=await pedir("Canal de YouTube a vigilar",{texto:"Escribe su @ (por ejemplo @QuantumFracture).",placeholder:"@canal",si:"Vigilar"});if(!c)return;
  await accion(()=>editarJson("produccion/objetivos.json",d=>{d.competencia=d.competencia||[];const h="@"+c.replace(/^@/,"").trim();if(!d.competencia.includes(h))d.competencia.push(h)},"Panel: vigilar canal [skip ci]",{crear:{objetivos:[],competencia:[]}}),"Añadido. Sus datos llegan en la próxima recogida (o pulsa «Recoger ahora» en Tendencias).")}
async function quitarCompetidor(c){if(!await confirmar(`¿Dejar de vigilar ${c}?`,"",{si:"Quitar",peligro:true}))return;await accion(()=>editarJson("produccion/objetivos.json",d=>{d.competencia=(d.competencia||[]).filter(x=>x!==c)},"Panel: dejar de vigilar [skip ci]"),"Quitado")}
