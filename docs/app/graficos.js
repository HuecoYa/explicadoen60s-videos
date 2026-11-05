// ═══════════ Gráficos en SVG (sin librerías) ═══════════
function sparkline(serie,color,alto=44){
  if(!serie||serie.length<2)return `<svg viewBox="0 0 200 ${alto}"><line x1="0" y1="${alto-6}" x2="200" y2="${alto-6}" stroke="var(--bd)" stroke-width="2" stroke-dasharray="4 5"/></svg>`;
  const mn=Math.min(...serie),mx=Math.max(...serie),sp=mx-mn||1,pts=serie.map((v,i)=>[i/(serie.length-1)*200,alto-6-(v-mn)/sp*(alto-12)]);
  const d=pts.map((p,i)=>(i?"L":"M")+p[0].toFixed(1)+" "+p[1].toFixed(1)).join(" "),id="g"+Math.random().toString(36).slice(2,7);
  return `<svg viewBox="0 0 200 ${alto}" preserveAspectRatio="none" style="height:${alto}px;width:100%;display:block"><defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${color}" stop-opacity=".32"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs><path d="${d} L200 ${alto} L0 ${alto}Z" fill="url(#${id})"/><path d="${d}" fill="none" stroke="${color}" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>`;
}
// series: [{nombre,color,p:[{x:clave,v}]}], xs: claves ordenadas, etX: clave→texto
function grafLineas(el,series,xs,{alto=240,etX=x=>x,fmt=fmtN,etiquetaFinal=true,proyeccion=null}={}){
  const W=el.clientWidth||700,H=alto,m={t:12,r:etiquetaFinal?96:16,b:26,l:48};
  series=series.filter(s=>s.p.length);if(!series.length||!xs.length){el.innerHTML=vacio("chart","Sin datos todavía","La línea se irá dibujando con un punto nuevo cada día.");return}
  const n=Math.max(1,xs.length-1);
  const todos=series.flatMap(s=>s.p.map(x=>x.v)).concat(proyeccion?proyeccion.map(p=>p.v):[]);
  const mx=Math.max(1,...todos)*1.08,mn=Math.min(0,...todos);
  const X=x=>m.l+(xs.length>1?xs.indexOf(x)/n:.5)*(W-m.l-m.r),Y=v=>m.t+(1-(v-mn)/(mx-mn))*(H-m.t-m.b);
  let s=`<svg viewBox="0 0 ${W} ${H}" height="${H}">`;
  for(let i=0;i<=4;i++){const v=mn+(mx-mn)/4*i,y=Y(v);s+=`<line x1="${m.l}" x2="${W-m.r}" y1="${y}" y2="${y}" stroke="var(--bd)" stroke-width="1"/><text x="${m.l-8}" y="${y+4}" text-anchor="end">${fmt(v)}</text>`}
  const paso=Math.ceil(xs.length/7);xs.forEach((x,i)=>{if(i%paso===0||i===xs.length-1)s+=`<text x="${X(x)}" y="${H-6}" text-anchor="middle">${etX(x)}</text>`});
  if(proyeccion){const d=proyeccion.map((q,i)=>(i?"L":"M")+X(q.x)+" "+Y(q.v)).join(" ");s+=`<path d="${d}" fill="none" stroke="var(--faint)" stroke-width="2" stroke-dasharray="5 5"/>`}
  series.forEach(({color,p,nombre})=>{const d=p.map((q,i)=>(i?"L":"M")+X(q.x)+" "+Y(q.v)).join(" ");
    s+=`<path d="${d}" fill="none" stroke="${color}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>`;
    if(p.length<40)p.forEach(q=>s+=`<circle cx="${X(q.x)}" cy="${Y(q.v)}" r="${p.length<3?4.5:2.6}" fill="${color}" stroke="var(--s1)" stroke-width="1.5"/>`);
    const u=p[p.length-1];if(etiquetaFinal)s+=`<text x="${X(u.x)+9}" y="${Y(u.v)+4}" style="fill:var(--fg);font-weight:600">${esc(nombre)} ${fmt(u.v)}</text>`});
  s+=`<line class="cruz" x1="0" x2="0" y1="${m.t}" y2="${H-m.b}" stroke="var(--faint)" stroke-dasharray="3 3" visibility="hidden"/><rect x="${m.l}" y="0" width="${Math.max(1,W-m.l-m.r)}" height="${H}" fill="transparent" class="hit"/></svg>`;
  el.innerHTML=(series.length>1?`<div class="leyenda">${series.map(x=>`<span><i style="background:${x.color}"></i>${esc(x.nombre)}</span>`).join("")}</div>`:"")+s;
  const hit=el.querySelector(".hit"),cr=el.querySelector(".cruz"),svg=el.querySelector("svg");
  hit.onpointermove=e=>{const b=svg.getBoundingClientRect(),x=(e.clientX-b.left)*W/b.width,i=Math.round((x-m.l)/((W-m.l-m.r)/n)),k=xs[Math.max(0,Math.min(xs.length-1,i))];
    cr.setAttribute("x1",X(k));cr.setAttribute("x2",X(k));cr.setAttribute("visibility","visible");
    verTip(e,`<b>${etX(k)}</b><br>`+series.map(({nombre,color,p})=>{const q=p.find(z=>z.x===k);return `<span style="color:${color}">●</span> ${esc(nombre)}: <b>${q?fmt(q.v):"—"}</b>`}).join("<br>"))};
  hit.onpointerleave=()=>{cr.setAttribute("visibility","hidden");ocultarTip()};
}
// items: [{nombre,v,color,tip}]
function grafBarras(el,items,{fmt=fmtN}={}){
  if(!items.length){el.innerHTML=vacio("chart","Sin datos");return}
  const mx=Math.max(...items.map(i=>i.v))||1;
  el.innerHTML=items.map((it,i)=>`<div class="hbar" data-i="${i}"><div><div class="nom">${esc(it.nombre)}</div><div class="b" style="background:${it.color};width:${Math.max(1.5,it.v/mx*100)}%;animation-delay:${i*.035}s"></div></div><div class="v">${fmt(it.v)}</div></div>`).join("");
  el.querySelectorAll(".hbar").forEach(b=>{const it=items[+b.dataset.i];if(!it.tip)return;b.onpointermove=e=>verTip(e,it.tip);b.onpointerleave=ocultarTip});
}
// mapa de calor día × hora; celdas: {d,h,v,n,tip}
function grafCalor(el,celdas,{color="#ffd23f"}={}){
  const mx=Math.max(1,...celdas.map(c=>c.v||0));
  let h=`<div class="calor"><span></span>${Array.from({length:24},(_,i)=>`<span class="hcol">${i%3===0?i:""}</span>`).join("")}`;
  for(let d=0;d<7;d++){h+=`<span class="l">${DIAS[d]}</span>`;
    for(let k=0;k<24;k++){const c=celdas.find(x=>x.d===d&&x.h===k);
      h+=`<span class="c" ${c?`data-k="${d}-${k}" style="background:color-mix(in srgb, ${color} ${Math.round(18+82*(c.v/mx))}%, var(--s3))"`:""}></span>`}}
  el.innerHTML=h+`</div>`;
  el.querySelectorAll("[data-k]").forEach(x=>{const [d,k]=x.dataset.k.split("-").map(Number),c=celdas.find(z=>z.d===d&&z.h===k);x.onpointermove=e=>verTip(e,c.tip);x.onpointerleave=ocultarTip});
}
