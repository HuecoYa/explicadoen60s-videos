// ═══════════ Comunidad ═══════════
let CFILTRO="preguntas",COM=null,CAN=null;
const esPregunta=t=>/[¿?]|\b(c[oó]mo|por qu[eé]|qu[eé] pasa|cu[aá]nto|cu[aá]l|d[oó]nde|se puede|haz (uno|un v[ií]deo)|podr[ií]as|y (el|la|los|las) )\b/i.test(t||"");
async function vistaCom(sub){
  const [com,an]=await Promise.all([json("programador/comunidad.json",{opcional:true}),json("produccion/comunidad_analisis.json",{opcional:true})]);COM=com;CAN=an;
  const cs=com?.comentarios||[],preg=cs.filter(c=>esPregunta(c.texto)),sinr=preg.filter(c=>!c.respuestas);
  acciones(`<span class="mut peq" style="align-self:center">${com?"Comentarios "+hace(com.actualizado):""}</span>`);
  let h=segmentos("com",[["bandeja","Bandeja",sinr.length],["ideas","Ideas que piden",(an?.ideas||[]).length||ideasDeComentarios(cs).length]],sub);
  const errs=Object.entries(com?.errores||{});
  if(errs.length)h+=`<div class="msg warn">${ic("alert","s")}<div>${errs.map(([r,e])=>`<b>${NOMBRE[r]}</b>: ${/insufficient|scope|403/i.test(e)?"falta el permiso de comentarios. En Conexiones, vuelve a conectar YouTube (ahora pide también «gestionar comentarios»).":esc(e)}`).join("<br>")}</div></div>`;
  if(sub==="ideas")h+=comIdeas(cs,an);else h+=comBandeja(cs,an);
  app.innerHTML=h;animarKpis();
}
function respuestaPara(c,an){
  if(an?.respuestas?.[c.id])return an.respuestas[c.id];
  if(esPregunta(c.texto))return `¡Buena pregunta, ${c.autor.replace(/^@/,"").split(/[\s_.]/)[0]}! Lo apuntamos para un próximo vídeo 👀`;
  return `¡Gracias por comentar! 🙌`;
}
function comBandeja(cs,an){
  const f={todos:()=>true,preguntas:c=>esPregunta(c.texto),sin:c=>esPregunta(c.texto)&&!c.respuestas,youtube:c=>c.red==="youtube",instagram:c=>c.red==="instagram"};
  const lista=cs.filter(f[CFILTRO]||f.todos);
  const n=k=>cs.filter(f[k]).length;
  return `${an?.resumen?`<div class="card fade"><div class="h3">${ic("spark")}Qué dicen tus seguidores</div><p style="margin:0;color:var(--fg2)">${esc(an.resumen)}</p></div>`:""}
  <div class="grid g4">${kpi("Comentarios leídos",cs.length,"YouTube e Instagram","chat")}${kpi("Preguntas",n("preguntas"),"oportunidades de vídeo","idea")}${kpi("Sin responder",n("sin"),"responder ayuda al alcance","clock")}${kpi("TikTok",null,"no da comentarios por API: revísalos en la app","info")}</div>
  <div class="chips" style="margin-bottom:16px">${[["preguntas","Preguntas"],["sin","Sin responder"],["todos","Todos"],["youtube","YouTube"],["instagram","Instagram"]].map(([k,t])=>`<button class="chip ${CFILTRO===k?"on":""}" onclick="CFILTRO='${k}';ir('com','bandeja',true)">${t} <span class="faint">${n(k)}</span></button>`).join("")}</div>
  <div class="card fade">${lista.length?lista.slice(0,80).map(c=>{const r=respuestaPara(c,an);return `<div class="com"><div class="av">${iniciales(c.autor)}</div><div style="min-width:0">
   <div class="cab"><b>${esc(c.autor)}</b>${redPill(c.red)}<span>${hace(c.fecha)}</span>${c.likes?`<span>${ic("heart","s")} ${c.likes}</span>`:""}${c.respuestas?`<span class="pill ok">${c.respuestas} respuesta(s)</span>`:esPregunta(c.texto)?`<span class="pill warn">sin responder</span>`:""}</div>
   <div class="txt">${esc(c.texto)}</div><div class="faint peq">en «${esc((c.video||"").slice(0,70))}»</div>
   <div class="resp"><span class="etiqueta">Respuesta sugerida</span><div>${esc(r)}</div></div>
   <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px"><button class="btn sec peq" onclick='copiar(${JSON.stringify(r).replace(/'/g,"&#39;")})'>${ic("copy","s")}Copiar respuesta</button>${c.url?`<a class="btn fantasma peq" href="${esc(c.url)}" target="_blank">${ic("ext","s")}Abrir</a>`:""}${esPregunta(c.texto)?`<button class="btn fantasma peq" onclick='nuevaIdea(${JSON.stringify(c.texto.slice(0,140)).replace(/'/g,"&#39;")},{origen:"comentario de ${esc(c.autor)}",prioridad:"alta"})'>${ic("idea","s")}Convertir en idea</button>`:""}</div>
   </div></div>`}).join(""):vacio("chat","No hay comentarios aquí","Los comentarios de YouTube e Instagram se leen cada 3 horas.")}</div>`;
}
// ideas detectadas en los comentarios (si Claude aún no las ha agrupado)
function ideasDeComentarios(cs){
  const g={};
  for(const c of cs){const t=(c.texto||"").toLowerCase();
    const m=t.match(/(?:c[oó]mo funciona|haz(?: un v[ií]deo)? (?:de|sobre)|y (?:el|la|los|las)|explica(?:r)?(?: el| la)?|por qu[eé])\s+([a-záéíóúñ ]{3,40})/i);
    if(m){const k=m[1].trim().split(/\s+/).slice(0,4).join(" ");(g[k]=g[k]||[]).push(c)}}
  return Object.entries(g).map(([tema,a])=>({tema,menciones:a.length,ejemplos:a.slice(0,3).map(c=>c.texto)})).sort((a,b)=>b.menciones-a.menciones);
}
function comIdeas(cs,an){
  const ideas=an?.ideas?.length?an.ideas:ideasDeComentarios(cs);
  return `<div class="msg info">${ic("info","s")}<div>Temas que tus seguidores piden en los comentarios. Un vídeo que responde a un comentario suele funcionar muy bien: menciona a quien lo pidió.</div></div>
  <div class="card fade">${ideas.length?ideas.map(i=>`<div class="fila" style="align-items:flex-start"><span class="punt" style="--p:${Math.min(100,i.menciones*20)};--c:var(--acc)"><span>${i.menciones}</span></span><span class="t"><b>${esc(i.idea||i.tema)}</b><small style="display:block">${(i.ejemplos||[]).map(e=>"«"+esc(e.slice(0,110))+"»").join("<br>")}</small></span><button class="btn sec peq" onclick='nuevaIdea(${JSON.stringify(i.idea||i.tema).replace(/'/g,"&#39;")},{origen:"pedido en comentarios",prioridad:"alta",notas:${JSON.stringify((i.ejemplos||[]).join(" | ")).replace(/'/g,"&#39;")}})'>${ic("idea","s")}Al banco</button></div>`).join("")
   :vacio("idea","Todavía no hay peticiones claras","Cuando alguien escriba «cómo funciona…» o «haz uno de…», aparecerá aquí.")}</div>`;
}
