// ═══════════ Tendencias ═══════════
let TFILTRO="todas",TEND=null;
async function vistaTend(sub){
  const [a,raw]=await Promise.all([json("produccion/tendencias.json",{opcional:true}),json("programador/tendencias_raw.json",{opcional:true})]);TEND=a;
  acciones(`<span class="mut peq" style="align-self:center">${a?"Análisis "+hace(a.actualizado):""}${raw?" · señales "+hace(raw.actualizado):""}</span><button class="btn sec" onclick="accion(()=>lanzarFlujo('tendencias.yml'),'Buscando tendencias… las señales llegan en 1-2 minutos y Claude las analiza en su próxima pasada.',{recargar:false})">${ic("refresh","s")}Recoger señales</button>`);
  const ts=a?.tendencias||[];
  let h=segmentos("tend",[["analisis","Analizadas",ts.length],["senales","Señales en bruto"],["descartadas","Descartadas",(a?.descartadas||[]).length]],sub);
  if(sub==="senales")h+=tendSenales(raw);
  else if(sub==="descartadas")h+=`<div class="card fade">${(a?.descartadas||[]).map(d=>`<div class="fila"><span class="t"><b>${esc(d.tema)}</b><small>${esc(d.motivo)}</small></span></div>`).join("")||vacio("check","Nada descartado")}</div>`;
  else h+=tendAnalisis(a);
  app.innerHTML=h;
}
function tendAnalisis(a){
  if(!a?.tendencias?.length)return `<div class="card">${vacio("flame","Aún no hay tendencias analizadas","Las señales se recogen a las 7:40 y 18:40, y Claude las analiza en la pasada siguiente (8:56 y 19:56). Mientras, mira «Señales en bruto».",`<a class="btn sec peq" href="#/tend/senales">Señales en bruto</a>`)}</div>`;
  const tipos=[...new Set(a.tendencias.map(t=>t.tipo).filter(Boolean))];
  const ts=a.tendencias.filter(t=>TFILTRO==="todas"||t.tipo===TFILTRO).sort((x,y)=>y.puntuacion-x.puntuacion);
  const TIPO={actualidad:["Actualidad","warn"],evergreen:["Siempre funciona","ok"],nicho:["Ya triunfa en el nicho","info"]};
  return `${a.resumen?`<div class="card fade" style="border-color:rgba(255,210,63,.25)"><div class="h3">${ic("spark")}Lo que conviene hacer hoy</div><p style="margin:0;color:var(--fg2)">${esc(a.resumen)}</p></div>`:""}
  <div class="chips" style="margin-bottom:16px">${["todas",...tipos].map(t=>`<button class="chip ${TFILTRO===t?"on":""}" onclick="TFILTRO='${t}';ir('tend','analisis',true)">${t==="todas"?"Todas":(TIPO[t]?.[0]||t)}</button>`).join("")}</div>`+
  ts.map((t,i)=>{const r=t.reglas||{},abierto=i<2;return `<div class="card fade"><div class="tend">
    <div class="punt" style="--p:${t.puntuacion};--c:${colorPunt(t.puntuacion)};width:54px;height:54px;font-size:16px"><span>${t.puntuacion}</span></div>
    <div style="min-width:0"><h3>${esc(t.tema)}</h3><p class="mut" style="margin:0">${esc(t.por_que||"")}</p>
     <div class="meta">${t.tipo?`<span class="pill ${TIPO[t.tipo]?.[1]||""}">${TIPO[t.tipo]?.[0]||esc(t.tipo)}</span>`:""}${t.urgencia?`<span class="pill ${/24|hoy|ya/i.test(t.urgencia)?"err":""}">${ic("clock","s")}${esc(t.urgencia)}</span>`:""}${t.formato?`<span class="pill">Formato ${esc(t.formato)}</span>`:""}${t.potencial?`<span class="pill acc">Potencial ${esc(t.potencial)}</span>`:""}</div></div>
    <div class="acciones" style="display:flex;flex-direction:column;gap:6px"><button class="btn peq" onclick="tendAIdea('${esc(t.id)}')">${ic("idea","s")}Convertir en guion</button><button class="btn sec peq" onclick="copiar(fichaTend('${esc(t.id)}'))">${ic("copy","s")}Copiar ficha</button></div></div>
    <details ${abierto?"open":""} style="margin-top:12px"><summary>Ficha completa</summary>
     ${t.angulo?`<div class="bloque"><span class="etiqueta">Cómo enfocarlo para la cuenta</span><p>${esc(t.angulo)}</p></div>`:""}
     <div class="grid g2" style="margin:0">${t.titulo?`<div class="bloque"><span class="etiqueta">Título propuesto</span><p><b>${esc(t.titulo)}</b></p></div>`:""}${t.gancho?`<div class="bloque"><span class="etiqueta">Gancho (primera frase)</span><p>«${esc(t.gancho)}»</p></div>`:""}
      ${t.primer_segundo?`<div class="bloque"><span class="etiqueta">Qué se ve en el primer segundo</span><p>${esc(t.primer_segundo)}</p></div>`:""}${t.cifras?.length?`<div class="bloque"><span class="etiqueta">Cifras para enseñar en pantalla</span><div class="chips" style="margin-top:4px">${t.cifras.map(c=>`<span class="pill acc">${esc(c)}</span>`).join("")}</div></div>`:""}</div>
     ${t.estructura?.length?`<div class="bloque"><span class="etiqueta">Estructura del vídeo</span><ol style="margin:4px 0 0;padding-left:20px">${t.estructura.map(p=>`<li>${esc(p)}</li>`).join("")}</ol></div>`:""}
     <div class="bloque"><span class="etiqueta">Las 3 reglas</span><div class="reglas3" style="margin-top:6px">${[["cotidiano","Tema de uso diario"],["primer_segundo","Acción en el primer segundo"],["ensenar","Se puede enseñar con cifras"]].map(([k,n])=>`<div class="regla3"><div class="etiqueta" style="color:var(--fg2)"><span>${n}</span><b>${r[k]??"—"}/10</b></div><div class="barra" style="margin-top:5px"><i style="width:${(r[k]||0)*10}%;background:${(r[k]||0)>=7?"var(--ok)":(r[k]||0)>=4?"var(--acc)":"var(--err)"}"></i></div></div>`).join("")}</div></div>
     ${t.por_que_funcionaria?`<div class="bloque"><span class="etiqueta">Por qué funcionaría</span><p>${esc(t.por_que_funcionaria)}</p></div>`:""}
     <div class="grid g2" style="margin:0">${t.competencia?`<div class="bloque"><span class="etiqueta">Qué hay ya publicado</span><p>${esc(t.competencia)}</p></div>`:""}${t.riesgos?`<div class="bloque"><span class="etiqueta">Riesgos</span><p>${esc(t.riesgos)}</p></div>`:""}${t.mejor_hora?`<div class="bloque"><span class="etiqueta">Cuándo publicarlo</span><p>${esc(t.mejor_hora)}</p></div>`:""}${t.hashtags?.length?`<div class="bloque"><span class="etiqueta">Hashtags</span><p>${t.hashtags.map(x=>"#"+esc(x)).join(" ")}</p></div>`:""}</div>
     ${t.senales?.length?`<div class="bloque"><span class="etiqueta">Señales y fuentes</span>${t.senales.map(s=>`<div class="peq" style="margin-top:4px">${ic("trend","s")} <b>${esc(s.fuente)}</b>: ${esc(s.dato)}${s.url?` · <a href="${esc(s.url)}" target="_blank">abrir</a>`:""}</div>`).join("")}</div>`:""}
    </details></div>`}).join("");
}
function fichaTend(id){const t=TEND.tendencias.find(x=>x.id===id);if(!t)return "";
  return [`${t.tema} (${t.puntuacion}/100)`,t.por_que,t.angulo&&"Enfoque: "+t.angulo,t.titulo&&"Título: "+t.titulo,t.gancho&&"Gancho: "+t.gancho,t.primer_segundo&&"Primer segundo: "+t.primer_segundo,t.cifras?.length&&"Cifras: "+t.cifras.join(" · "),t.estructura?.length&&"Estructura:\n"+t.estructura.map((p,i)=>`${i+1}. ${p}`).join("\n"),t.formato&&"Formato: "+t.formato,t.hashtags?.length&&t.hashtags.map(x=>"#"+x).join(" ")].filter(Boolean).join("\n\n")}
async function tendAIdea(id){const t=TEND.tendencias.find(x=>x.id===id);if(!t)return;
  if(!await confirmar("¿Convertir esta tendencia en guion?",`Se añade al banco de ideas con prioridad alta. Claude escribirá el guion en su próxima pasada (${fmtHora(proximaPasada())}) usando toda la ficha.`,{si:"Añadir al banco"}))return;
  await accion(()=>editarJson("produccion/ideas.json",d=>{d.ideas.push({id:"i"+Date.now().toString(36),texto:t.titulo||t.tema,prioridad:"alta",origen:"tendencia: "+t.tema,notas:fichaTend(id),tendencia:t.id,por:usuario,fecha:new Date().toISOString(),estado:"pendiente"})},"Panel: idea desde tendencia [skip ci]",{crear:{ideas:[]}}),"Añadida al banco de ideas con prioridad alta.",{recargar:false})}

function tendSenales(raw){
  if(!raw)return `<div class="card">${vacio("trend","Todavía no hay señales","Pulsa «Recoger señales» arriba.")}</div>`;
  const err=Object.entries(raw.errores||{});
  const lista=(items,fn)=>items?.length?items.map(fn).join(""):`<p class="mut peq">Sin datos.</p>`;
  const yt=raw.youtube||{};
  return `${err.length?`<div class="msg warn">${ic("alert","s")}<div>${err.map(([k,v])=>`${esc(k)}: ${esc(String(v).slice(0,120))}`).join("<br>")}</div></div>`:""}
  <div class="grid g2">
   <div class="card fade"><div class="h3">${ic("trend")}Google Trends · España hoy<span class="sub">búsquedas aproximadas</span></div>${lista(raw.google_trends,t=>`<div class="fila" style="align-items:flex-start"><span class="pill acc" style="min-width:60px;justify-content:center">${esc(t.busquedas)}</span><span class="t"><b>${esc(t.tema)}</b><small>${(t.noticias||[]).slice(0,2).map(n=>`<a href="${esc(n.url)}" target="_blank">${esc(n.titulo.slice(0,70))}</a> <span class="faint">${esc(n.fuente)}</span>`).join("<br>")}</small></span></div>`)}</div>
   <div class="card fade"><div class="h3">${ic("film")}Shorts de «cómo funciona» que triunfan<span class="sub">última semana</span></div>${lista(raw.nicho,v=>`<div class="fila"><span class="t"><a class="tt" style="color:var(--fg);font-weight:600" href="${esc(v.url)}" target="_blank">${esc(v.titulo)}</a><small>${esc(v.canal)} · ${hace(v.fecha)} · ${fmtN(v.comentarios)} comentarios</small></span><b class="num">${fmtN(v.vistas)}</b></div>`)}</div>
   <div class="card fade"><div class="h3">${ic("report")}Wikipedia · lo más leído ayer</div>${lista(raw.wikipedia?.slice(0,25),t=>`<div class="fila"><span class="t"><a class="tt" style="color:var(--fg)" href="${esc(t.url)}" target="_blank">${esc(t.tema)}</a></span><span class="num mut">${fmtN(t.lecturas)}</span></div>`)}</div>
   <div class="card fade"><div class="h3">${ic("cube")}YouTube España · Ciencia y tecnología</div>${lista(Array.isArray(yt.ciencia_tecnologia)?yt.ciencia_tecnologia.slice(0,15):[],v=>`<div class="fila"><span class="t"><a class="tt" style="color:var(--fg)" href="${esc(v.url)}" target="_blank">${esc(v.titulo)}</a><small>${esc(v.canal)} · ${hace(v.fecha)}</small></span><b class="num">${fmtN(v.vistas)}</b></div>`)}</div>
  </div>
  <div class="card fade"><details><summary>YouTube España · tendencias generales (${Array.isArray(yt.general)?yt.general.length:0})</summary>${lista(Array.isArray(yt.general)?yt.general:[],v=>`<div class="fila"><span class="t"><a class="tt" style="color:var(--fg)" href="${esc(v.url)}" target="_blank">${esc(v.titulo)}</a><small>${esc(v.canal)}</small></span><b class="num">${fmtN(v.vistas)}</b></div>`)}</details></div>`;
}
