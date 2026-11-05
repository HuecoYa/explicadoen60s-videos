// ═══════════ Estadísticas ═══════════
let FILTRO="todas",ORDEN={k:"rel",d:-1},CMP=[null,null],VERTODO=false;

// todos los vídeos con métricas derivadas
function videosDe(st,est){
  const meta={};for(const v of est?.videos||[])meta[norm(v.titulo)]=v;
  const out=[];
  for(const r of REDES){const vs=(st?.videos?.[r]||[]).filter(v=>v.vistas>0); /* sin vistas = la red aún no da el dato */const med=mediana(vs.map(v=>v.vistas))||1;
    for(const v of vs){const inter=v.vistas?((v.likes||0)+2*(v.comentarios||0)+3*(v.compartidos||0)+2*(v.guardados||0))/v.vistas:null;const m=meta[norm(v.titulo)];
      out.push({...v,red:r,inter,rel:v.vistas/med,maduro:v.fecha&&Date.now()-new Date(v.fecha)>48*36e5,hora:v.fecha?horaMadrid(v.fecha):null,dia:v.fecha?diaSemana(v.fecha):null,formato:m?.formato,duracion:m?.duracion,guion:m?.guion,clave:r+":"+v.id})}}
  return out;
}
const norm=t=>(t||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/[^a-z0-9 ]/g,"").replace(/\s+/g," ").trim().slice(0,60);
const fmtX=x=>x==null?"—":(x>=10?Math.round(x):x.toFixed(1)).toString().replace(".",",")+"×";

async function vistaStats(sub){
  const [st,est]=await Promise.all([json("programador/estadisticas.json",{opcional:true}),json("produccion/estado.json")]);
  acciones(`<span class="mut peq" style="align-self:center">${st?"Datos "+hace(st.actualizado):""}</span><button class="btn sec" onclick="accion(()=>lanzarFlujo('estadisticas.yml'),'Recogiendo estadísticas… tardan 1-2 minutos.',{recargar:false})">${ic("refresh","s")}Actualizar</button>`);
  if(!st){app.innerHTML=`<div class="card">${vacio("chart","Todavía no hay estadísticas","Se recogen solas cada hora.")}</div>`;return}
  const todos=videosDe(st,est);
  let h=segmentos("stats",[["general","General"],["ranking","Ranking"],["comparar","Comparar A/B"],["horas","Mejor hora"],["informe","Informe semanal"]],sub);
  const filtros=`<div class="chips" style="margin-bottom:16px">${["todas",...REDES].map(r=>`<button class="chip ${FILTRO===r?"on":""}" onclick="FILTRO='${r}';ir('stats',RUTA.sub,true)">${r==="todas"?"Todas":`<i style="background:${COLOR[r]}"></i>${NOMBRE[r]}`}</button>`).join("")}</div>`;
  const vids=todos.filter(v=>FILTRO==="todas"||v.red===FILTRO);
  if(sub==="ranking")h+=filtros+statsRanking(vids);
  else if(sub==="comparar")h+=statsComparar(todos);
  else if(sub==="horas")h+=filtros+statsHoras(vids);
  else if(sub==="informe")h+=statsInforme(st,todos);
  else h+=filtros+statsGeneral(st,vids);
  app.innerHTML=h;animarKpis();
  if(!sub||sub==="general")despuesDePintar=()=>{const redes=FILTRO==="todas"?REDES:[FILTRO],hist=st.historial||[],xs=[...new Set(hist.map(x=>x.fecha))].sort();
    grafLineas($("#cLinea"),redes.map(r=>({nombre:NOMBRE[r],color:COLOR[r],p:hist.filter(x=>x[r+"_seguidores"]!=null).map(x=>({x:x.fecha,v:x[r+"_seguidores"]}))})),xs,{etX:f=>`${+f.slice(8)}/${+f.slice(5,7)}`});
    grafBarras($("#cBarras"),[...vids].sort((a,b)=>b.vistas-a.vistas).slice(0,10).map(v=>({nombre:v.titulo||"(sin título)",v:v.vistas,color:COLOR[v.red],tip:`<b>${esc(v.titulo)}</b><br>${NOMBRE[v.red]} · ${v.fecha?fmtDiaC(v.fecha):""}<br>Vistas <b>${nf.format(v.vistas)}</b> · Interacción <b>${pct(v.inter)}</b>`})));
    tablaVideos(vids)};
  if(sub==="horas")despuesDePintar=()=>{const c=celdasHoras(vids.filter(v=>v.maduro));grafCalor($("#calor"),c)};
}

function statsGeneral(st,vids){
  const redes=FILTRO==="todas"?REDES:[FILTRO],sum=k=>vids.reduce((s,v)=>s+(v[k]||0),0);
  return `<div class="grid g4">${kpi("Seguidores",redes.reduce((s,r)=>s+(st.cuentas?.[r]?.seguidores||0),0),FILTRO==="todas"?"las tres redes":NOMBRE[FILTRO],"user")}${kpi("Visualizaciones",sum("vistas"),`${vids.length} vídeos`,"eye")}${kpi("Likes",sum("likes"),`interacción media ${pct(mediana(vids.map(v=>v.inter)))}`,"heart")}${kpi("Comentarios",sum("comentarios"),`${fmtN(sum("compartidos"))} compartidos`,"chat")}</div>
  <div class="grid g2"><div class="card fade"><div class="h3">${ic("user")}Seguidores en el tiempo</div><div class="chart" id="cLinea"></div></div>
  <div class="card fade"><div class="h3">${ic("eye")}Vídeos con más visualizaciones</div><div id="cBarras"></div></div></div>
  <div class="card fade"><div class="h3">${ic("list")}Todos los vídeos<span class="sub">${vids.length}</span></div><div class="tablewrap" id="tabla"></div></div>`;
}
function tablaVideos(vids){
  const cols=[["red","Red"],["titulo","Vídeo"],["fecha","Publicado"],["vistas","Vistas",1],["rel","vs su red",1],["likes","Likes",1],["comentarios","Coment.",1],["compartidos","Compart.",1],["inter","Interacción",1]];
  const todosO=[...vids].sort((a,b)=>{const x=a[ORDEN.k]??-1,y=b[ORDEN.k]??-1;return (x>y?1:x<y?-1:0)*ORDEN.d}),o=VERTODO?todosO:todosO.slice(0,25);
  $("#tabla").innerHTML=!vids.length?vacio("film","No hay vídeos"):`<table><thead><tr>${cols.map(([k,t,n])=>`<th class="${n?"n":""}" data-k="${k}">${t}${ORDEN.k===k?(ORDEN.d<0?" ↓":" ↑"):""}</th>`).join("")}</tr></thead><tbody>
   ${o.map(v=>`<tr><td>${redPill(v.red)}</td><td><a class="tt" href="${esc(v.url||"#")}" target="_blank">${esc(v.titulo||"(sin título)")}</a></td><td class="mut">${v.fecha?fmtDiaC(v.fecha):"—"}</td>
   <td class="n"><b>${fmtN(v.vistas)}</b></td><td class="n"><span class="pill ${v.rel>=1.5?"ok":v.rel<.6?"err":""}">${fmtX(v.rel)}</span></td><td class="n">${fmtN(v.likes)}</td><td class="n">${fmtN(v.comentarios)}</td><td class="n">${fmtN(v.compartidos)}</td><td class="n">${pct(v.inter)}</td></tr>`).join("")}</tbody></table>${todosO.length>25?`<p style="text-align:center"><button class="btn sec peq" id="vertodo">${VERTODO?"Ver menos":`Ver los ${todosO.length}`}</button></p>`:""}`;
  const vt=$("#vertodo");if(vt)vt.onclick=()=>{VERTODO=!VERTODO;tablaVideos(vids)};
  $("#tabla").querySelectorAll("th").forEach(th=>th.onclick=()=>{const k=th.dataset.k;ORDEN=ORDEN.k===k?{k,d:-ORDEN.d}:{k,d:-1};tablaVideos(vids)});
}

// ── Ranking ──
function statsRanking(vids){
  vids=vids.filter(v=>v.maduro);
  if(!vids.length)return `<div class="card">${vacio("chart","Sin vídeos")}</div>`;
  const o=[...vids].sort((a,b)=>b.rel*(1+(b.inter||0)*5)-a.rel*(1+(a.inter||0)*5));
  const porFormato={};for(const v of vids.filter(v=>v.formato)){(porFormato[v.formato]=porFormato[v.formato]||[]).push(v.rel)}
  const formatos=Object.entries(porFormato).map(([f,a])=>({f,m:mediana(a),n:a.length})).sort((a,b)=>b.m-a.m);
  const nombresF={A:"A · Así funciona",B:"B · Si tuvieras que inventar",C:"C · ¿Y si construyes…?"};
  const porDia=Array.from({length:7},(_,d)=>({d,m:mediana(vids.filter(v=>v.dia===d).map(v=>v.rel)),n:vids.filter(v=>v.dia===d).length})).filter(x=>x.n);
  const fila=(v,i)=>`<div class="fila"><span class="punt" style="--p:${Math.min(100,v.rel*40)};--c:${v.rel>=1.5?"var(--ok)":v.rel>=.8?"var(--acc)":"var(--err)"}"><span>${i+1}</span></span>${redPill(v.red)}<span class="t"><b>${esc(v.titulo)}</b><small>${fmtN(v.vistas)} vistas · ${fmtX(v.rel)} su red · interacción ${pct(v.inter)}${v.formato?` · formato ${v.formato}`:""}</small></span>${v.url?`<a class="ib" href="${esc(v.url)}" target="_blank" title="Ver">${ic("ext","s")}</a>`:""}</div>`;
  return `<div class="msg info">${ic("info","s")}<div>El ranking compara cada vídeo con <b>lo normal en su red</b> (la mediana de vistas) y premia la interacción: comentarios ×2, compartidos ×3, guardados ×2. Así un vídeo de Instagram no queda abajo solo porque Instagram dé menos vistas.</div></div>
  <div class="grid g21"><div class="card fade"><div class="h3">${ic("star")}Los que mejor funcionan</div>${o.slice(0,10).map(fila).join("")}</div>
   <div><div class="card fade"><div class="h3">${ic("film")}Por formato</div>${formatos.length?formatos.map(f=>`<div style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;font-size:13px"><span>${nombresF[f.f]||f.f}</span><b>${fmtX(f.m)}</b></div><div class="barra" style="margin-top:6px"><i style="width:${Math.min(100,f.m/Math.max(...formatos.map(x=>x.m))*100)}%"></i></div><div class="faint peq">${f.n} vídeos</div></div>`).join(""):`<p class="mut peq">Aún no hay vídeos enlazados con su formato.</p>`}</div>
   <div class="card fade"><div class="h3">${ic("cal")}Por día de publicación</div>${porDia.map(x=>`<div style="display:grid;grid-template-columns:40px 1fr 52px;gap:8px;align-items:center;margin:6px 0;font-size:13px"><span>${DIAS[x.d]}</span><div class="barra"><i style="width:${Math.min(100,x.m/Math.max(...porDia.map(z=>z.m))*100)}%"></i></div><b class="num" style="text-align:right">${fmtX(x.m)}</b></div>`).join("")}</div></div></div>
  <div class="card fade"><div class="h3">${ic("alert")}Los que menos funcionan<span class="sub">para aprender qué evitar</span></div>${o.slice(-5).reverse().map((v,i)=>fila(v,o.length-1-i)).join("")}</div>`;
}

// ── Comparar A/B ──
function statsComparar(todos){
  const ops=[...todos].sort((a,b)=>new Date(b.fecha)-new Date(a.fecha));
  if(!CMP[0]&&ops.length>1){const o=todos.filter(v=>v.maduro).sort((a,b)=>b.rel-a.rel);CMP=[o[0].clave,o[o.length-1].clave]}
  const sel=i=>`<select onchange="CMP[${i}]=this.value;ir('stats','comparar',true)">${ops.map(v=>`<option value="${v.clave}" ${CMP[i]===v.clave?"selected":""}>${NOMBRE[v.red]} · ${esc(v.titulo.slice(0,70))}</option>`).join("")}</select>`;
  const a=todos.find(v=>v.clave===CMP[0]),b=todos.find(v=>v.clave===CMP[1]);
  if(!a||!b)return `<div class="card">${vacio("compare","Hacen falta al menos dos vídeos")}</div>`;
  const filaM=(t,va,vb,fmt=fmtN,mejor=1)=>{const g=va==null||vb==null?0:(va>vb?1:vb>va?2:0)*(mejor>0?1:1);return `<tr><td class="mut">${t}</td><td class="n" style="${g===1?"color:var(--ok);font-weight:700":""}">${fmt(va)}</td><td class="n" style="${g===2?"color:var(--ok);font-weight:700":""}">${fmt(vb)}</td></tr>`};
  const gancho=v=>(v.guion||"").split(/(?<=[.?!…])\s/)[0];
  const concl=[];const r=(x,y)=>x&&y?x/y:null;
  if(a.rel&&b.rel){const k=a.rel>b.rel?[a,b]:[b,a];concl.push(`«${esc(k[0].titulo.slice(0,50))}» rindió <b>${fmtX(r(k[0].rel,k[1].rel))}</b> más que el otro, comparando cada uno con lo normal en su red.`)}
  if(a.inter&&b.inter)concl.push(`Interacción: ${pct(a.inter)} frente a ${pct(b.inter)}. ${Math.abs(a.inter-b.inter)/Math.max(a.inter,b.inter)>.3?"La diferencia es grande: el que más interacción tiene engancha mejor o provoca más comentarios.":"Parecida en los dos."}`);
  if(a.hora!=null&&b.hora!=null&&a.hora!==b.hora)concl.push(`Se publicaron a horas distintas (${a.hora}:00 frente a ${b.hora}:00). Mira «Mejor hora» para ver si eso influye.`);
  if(a.formato&&b.formato&&a.formato!==b.formato)concl.push(`Formatos distintos: ${a.formato} frente a ${b.formato}.`);
  return `<div class="card fade"><div class="grid g2" style="margin:0"><div><label>Vídeo A</label>${sel(0)}</div><div><label>Vídeo B</label>${sel(1)}</div></div></div>
  <div class="grid g2"><div class="card fade"><div class="h3">${ic("compare")}Cara a cara</div><div class="tablewrap"><table><thead><tr><th></th><th class="n">A</th><th class="n">B</th></tr></thead><tbody>
   ${filaM("Red",NOMBRE[a.red],NOMBRE[b.red],x=>x)}${filaM("Publicado",a.fecha,b.fecha,x=>x?fmtDiaC(x)+" "+fmtHora(x):"—")}
   ${filaM("Visualizaciones",a.vistas,b.vistas)}${filaM("vs lo normal en su red",a.rel,b.rel,fmtX)}${filaM("Likes",a.likes,b.likes)}${filaM("Comentarios",a.comentarios,b.comentarios)}${filaM("Compartidos",a.compartidos,b.compartidos)}${filaM("Guardados",a.guardados,b.guardados)}
   ${filaM("Interacción",a.inter,b.inter,pct)}${filaM("Duración",a.duracion,b.duracion,x=>x?x+" s":"—")}${filaM("Formato",a.formato,b.formato,x=>x||"—")}</tbody></table></div></div>
   <div class="card fade"><div class="h3">${ic("spark")}Qué se puede aprender</div>${concl.map(c=>`<div class="alerta">${ic("idea")}<div class="t">${c}</div></div>`).join("")}
    ${gancho(a)||gancho(b)?`<div class="bloque"><span class="etiqueta">Primera frase de A</span><p>${esc(gancho(a)||"—")}</p></div><div class="bloque"><span class="etiqueta">Primera frase de B</span><p>${esc(gancho(b)||"—")}</p></div>`:""}</div></div>`;
}

// ── Mejor hora ──
function celdasHoras(vids){
  const g={};for(const v of vids.filter(v=>v.hora!=null)){const k=v.dia+"-"+v.hora;(g[k]=g[k]||[]).push(v)}
  return Object.entries(g).map(([k,a])=>{const [d,h]=k.split("-").map(Number),m=mediana(a.map(x=>x.rel));return {d,h,v:m,n:a.length,tip:`<b>${DIAS[d]} a las ${h}:00</b><br>${a.length} vídeo(s) · rinden ${fmtX(m)} lo normal<br>${a.slice(0,3).map(x=>"· "+esc(x.titulo.slice(0,40))).join("<br>")}`}});
}
function horasRanking(vids){
  return Array.from({length:24},(_,h)=>{const a=vids.filter(v=>v.hora===h);return {h,n:a.length,m:mediana(a.map(x=>x.rel))}}).filter(x=>x.n);
}
function statsHoras(vids){
  vids=vids.filter(v=>v.maduro);
  const hr=horasRanking(vids),buenas=hr.filter(x=>x.n>=2).sort((a,b)=>b.m-a.m).slice(0,3),malas=hr.filter(x=>x.n>=2&&x.m<.7).sort((a,b)=>a.m-b.m);
  const redes=FILTRO==="todas"?REDES:[FILTRO];
  return `<div class="msg info">${ic("info","s")}<div>Calculado con tus propios vídeos: cada uno se compara con lo normal en su red. Con pocos vídeos por hora la estimación es orientativa; mejora cada semana.</div></div>
  <div class="grid g3">
   <div class="card fade"><div class="h3">${ic("star")}Mejores horas</div>${buenas.length?buenas.map(x=>`<div class="fila"><span class="hora">${String(x.h).padStart(2,"0")}:00</span><span class="t"><b>${fmtX(x.m)} lo normal</b><small>${x.n} vídeos</small></span></div>`).join(""):`<p class="mut peq">Hacen falta al menos 2 vídeos por hora.</p>`}</div>
   <div class="card fade"><div class="h3">${ic("alert")}Horas flojas</div>${malas.length?malas.slice(0,3).map(x=>`<div class="fila"><span class="hora">${String(x.h).padStart(2,"0")}:00</span><span class="t"><b>${fmtX(x.m)} lo normal</b><small>${x.n} vídeos</small></span></div>`).join(""):`<p class="mut peq">Ninguna hora destaca por ir mal.</p>`}</div>
   <div class="card fade"><div class="h3">${ic("clock")}Tu horario ahora</div>${redes.map(r=>`<div style="margin:6px 0">${redPill(r)} <span class="num">${HUECOS[r].map(h=>{const x=hr.find(z=>z.h===h);return `<span class="pill ${x&&x.n>=2?(x.m>=1.2?"ok":x.m<.7?"err":""):""}" style="margin:2px">${h}:00</span>`}).join("")}</span></div>`).join("")}<p class="faint peq">Verde: rinde por encima de lo normal. Rojo: por debajo.</p></div></div>
  <div class="card fade"><div class="h3">${ic("grid")}Rendimiento por día y hora<span class="sub">más intenso = mejor</span></div><div id="calor"></div></div>
  <div class="card fade"><div class="h3">${ic("chart")}Por hora de publicación</div>${hr.map(x=>`<div style="display:grid;grid-template-columns:52px 1fr 90px;gap:10px;align-items:center;margin:5px 0;font-size:13px"><span class="num">${String(x.h).padStart(2,"0")}:00</span><div class="barra"><i style="width:${Math.min(100,x.m/Math.max(...hr.map(z=>z.m))*100)}%"></i></div><span class="num" style="text-align:right">${fmtX(x.m)} · ${x.n}</span></div>`).join("")}</div>`;
}

// ── Informe semanal ──
function statsInforme(st,todos){
  const hist=st.historial||[],hoy=new Date(),hace7=new Date(Date.now()-7*864e5),hace14=new Date(Date.now()-14*864e5);
  const valor=(r,campo,d)=>{const obj=new Date(Date.now()-d*864e5).toISOString().slice(0,10);const h=[...hist].reverse().find(x=>x.fecha<=obj)||hist[0];return h?h[r+"_"+campo]:null};
  const act=r=>st.cuentas?.[r]?.seguidores,semana=todos.filter(v=>v.fecha&&new Date(v.fecha)>hace7),previa=todos.filter(v=>v.fecha&&new Date(v.fecha)>hace14&&new Date(v.fecha)<=hace7);
  const mejor=[...semana].sort((a,b)=>b.rel-a.rel)[0],peor=semana.filter(v=>v.maduro).sort((a,b)=>a.rel-b.rel)[0];
  const sumV=a=>a.reduce((s,v)=>s+(v.vistas||0),0);
  const lineas=[];
  for(const r of REDES){const a=act(r),b=valor(r,"seguidores",7);if(a!=null)lineas.push(`${NOMBRE[r]}: ${fmtN(a)} seguidores (${b!=null?(a-b>=0?"+":"")+fmtN(a-b):"sin dato previo"} en 7 días).`)}
  const recs=[];
  if(mejor)recs.push(`Haz una segunda parte o el mismo formato con otro objeto de «${mejor.titulo}»: rindió ${fmtX(mejor.rel)} lo normal.`);
  if(peor&&peor.rel<.6)recs.push(`Revisa el primer segundo de «${peor.titulo}» (${fmtX(peor.rel)}): compáralo con el mejor en «Comparar A/B».`);
  const hb=horasRanking(todos.filter(v=>v.maduro)).filter(x=>x.n>=2).sort((a,b)=>b.m-a.m)[0];if(hb)recs.push(`La hora que mejor funciona hasta ahora es las ${hb.h}:00 (${fmtX(hb.m)} lo normal).`);
  if(semana.length<10)recs.push(`Esta semana se publicaron ${semana.length} vídeos entre las tres redes: con más constancia el algoritmo te enseña más.`);
  const texto=`Informe semanal de @explicadoen60s (${fmtDiaC(hace7.toISOString())} – ${fmtDiaC(hoy.toISOString())})\n\n${lineas.join("\n")}\n\nPublicaciones (cada red cuenta aparte): ${semana.length} (semana anterior: ${previa.length}).\nVisualizaciones de esos vídeos: ${fmtN(sumV(semana))}.\n${mejor?`Mejor vídeo: «${mejor.titulo}» en ${NOMBRE[mejor.red]}, ${fmtN(mejor.vistas)} vistas (${fmtX(mejor.rel)} lo normal).\n`:""}${peor?`Más flojo: «${peor.titulo}» en ${NOMBRE[peor.red]}, ${fmtN(peor.vistas)} vistas.\n`:""}\nQué hacer esta semana:\n${recs.map(r=>"· "+r).join("\n")}`;
  return `<div class="grid g4">${REDES.map(r=>kpi(NOMBRE[r],act(r),`${delta(act(r),valor(r,"seguidores",7))} en 7 días`,"user")).join("")}${kpi("Publicaciones",semana.length,`${delta(semana.length,previa.length)} vs semana anterior`,"film")}</div>
  <div class="grid g2"><div class="card fade"><div class="h3">${ic("report")}Resumen de la semana<button class="btn sec peq" style="margin-left:auto" onclick="copiar(document.getElementById('inf').textContent)">${ic("copy","s")}Copiar</button></div><pre id="inf" style="max-height:none">${esc(texto)}</pre></div>
  <div class="card fade"><div class="h3">${ic("spark")}Qué hacer esta semana</div>${recs.map(r=>`<div class="alerta">${ic("idea")}<div class="t">${esc(r)}</div></div>`).join("")||`<p class="mut">Aún no hay datos suficientes.</p>`}
   ${mejor?`<div class="sep"></div><span class="etiqueta">Mejor vídeo de la semana</span><div class="fila">${redPill(mejor.red)}<span class="t"><b>${esc(mejor.titulo)}</b><small>${fmtN(mejor.vistas)} vistas · ${fmtX(mejor.rel)} lo normal</small></span></div>`:""}</div></div>`;
}
