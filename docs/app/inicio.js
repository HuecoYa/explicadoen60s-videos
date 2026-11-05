// ═══════════ Resumen ═══════════
let H3=null;
function heroStop(){if(H3){cancelAnimationFrame(H3.raf);H3.ro&&H3.ro.disconnect();H3.r.dispose();H3=null}}
function heroStart(canvas){
  heroStop();if(!window.THREE||!canvas)return;
  const T=THREE,r=new T.WebGLRenderer({canvas,antialias:true,alpha:true});r.setPixelRatio(Math.min(devicePixelRatio,2));
  const sc=new T.Scene(),cam=new T.PerspectiveCamera(32,1,.1,100);cam.position.set(0,0,10);
  sc.add(new T.AmbientLight(0xffffff,.55));const dl=new T.DirectionalLight(0xffffff,1.1);dl.position.set(4,5,6);sc.add(dl);
  const pl=new T.PointLight(0xffd23f,1.2,20);pl.position.set(-3,-2,4);sc.add(pl);
  const cv=document.createElement("canvas");cv.width=cv.height=512;const c=cv.getContext("2d");
  const g=c.createRadialGradient(200,180,40,256,256,280);g.addColorStop(0,"#ffe680");g.addColorStop(1,"#f2b705");c.fillStyle=g;c.fillRect(0,0,512,512);
  c.strokeStyle="rgba(20,20,26,.25)";c.lineWidth=14;c.beginPath();c.arc(256,256,226,0,7);c.stroke();
  c.translate(256,256);c.rotate(-Math.PI/2);c.translate(-256,-256);
  c.fillStyle="#14141a";c.textAlign="center";c.font="600 46px 'Space Grotesk',sans-serif";c.fillText("explicado en",256,190);
  c.font="700 190px 'Space Grotesk',sans-serif";c.fillText("60s",262,350);
  c.fillStyle="rgba(20,20,26,.2)";c.fillRect(146,388,220,16);c.fillStyle="#14141a";c.fillRect(146,388,165,16);
  const tex=new T.CanvasTexture(cv);tex.anisotropy=4;
  const cara=new T.MeshStandardMaterial({map:tex,metalness:.35,roughness:.35}),canto=new T.MeshStandardMaterial({color:0xe9a800,metalness:.7,roughness:.28});
  const moneda=new T.Mesh(new T.CylinderGeometry(1.5,1.5,.34,96),[canto,cara,cara]);moneda.rotation.x=Math.PI/2;
  const grupo=new T.Group();grupo.add(moneda);sc.add(grupo);
  const anillo=new T.Mesh(new T.TorusGeometry(2.45,.025,12,160,Math.PI*1.5),new T.MeshBasicMaterial({color:0xffd23f,transparent:true,opacity:.75}));sc.add(anillo);
  const orbes=REDES.map((k,i)=>{const m=new T.Mesh(new T.SphereGeometry(.34,40,24),new T.MeshStandardMaterial({color:COLOR[k],metalness:.25,roughness:.3,emissive:COLOR[k],emissiveIntensity:.15}));m.userData={f:i*2.1};sc.add(m);return m});
  const pg=new T.BufferGeometry(),N=160,pos=new Float32Array(N*3);for(let i=0;i<N*3;i++)pos[i]=(Math.random()-.5)*16;pg.setAttribute("position",new T.BufferAttribute(pos,3));
  const polvo=new T.Points(pg,new T.PointsMaterial({color:0xffd23f,size:.035,transparent:true,opacity:.5}));sc.add(polvo);
  let tx=0,ty=0,vy=0,arr=false,lx=0;
  canvas.onpointermove=e=>{const b=canvas.getBoundingClientRect();tx=((e.clientX-b.left)/b.width-.5);ty=((e.clientY-b.top)/b.height-.5);if(arr){vy+=(e.clientX-lx)*.004;lx=e.clientX}};
  canvas.onpointerdown=e=>{arr=true;lx=e.clientX;canvas.style.cursor="grabbing"};
  addEventListener("pointerup",()=>{arr=false;canvas.style.cursor="grab"});
  const ajustar=()=>{const w=canvas.clientWidth,h=canvas.clientHeight;r.setSize(w,h,false);cam.aspect=w/h;
    const ancho=w<700,k=ancho?.72:.92;grupo.position.x=ancho?0:2.7;grupo.position.y=ancho?-1.45:0;grupo.scale.setScalar(k);anillo.scale.setScalar(k);anillo.position.copy(grupo.position);cam.updateProjectionMatrix()};
  const ro=new ResizeObserver(ajustar);ro.observe(canvas);ajustar();
  const t0=performance.now();
  const bucle=()=>{if(!canvas.isConnected)return heroStop();const t=(performance.now()-t0)/1000;
    vy*=.95;grupo.rotation.y+=.006+vy;grupo.rotation.x+=((ty*.5)-grupo.rotation.x)*.05;grupo.position.z=Math.sin(t*1.2)*.12;
    anillo.rotation.z=-t*.35;anillo.rotation.x=.25+ty*.3;anillo.rotation.y=tx*.4;
    orbes.forEach(o=>{const a=t*.6+o.userData.f,k=grupo.scale.x;o.position.set(grupo.position.x+Math.cos(a)*2.45*k,grupo.position.y+Math.sin(a)*.9*k,Math.sin(a)*1.6)});
    polvo.rotation.y=t*.02;r.render(sc,cam);H3.raf=requestAnimationFrame(bucle)};
  H3={r,ro,raf:0};bucle();
}
const saludo=()=>{const h=+partes(new Date()).hour;return h<6?"Buenas noches":h<14?"Buenos días":h<21?"Buenas tardes":"Buenas noches"};

// valor de una métrica en el historial n días atrás
// registro del historial de hace «dias» días (o el más antiguo si aún no hay tanto historial)
function histRef(hist,dias){if(!hist?.length)return null;const obj=new Date(Date.now()-dias*864e5).toISOString().slice(0,10),hoy=new Date().toISOString().slice(0,10);
  return [...hist].reverse().find(x=>x.fecha<=obj)||(hist[0].fecha<hoy?hist[0]:null)}
const refTexto=(hist,dias)=>{const h=histRef(hist,dias);return h?`vs ${+h.fecha.slice(8)}/${+h.fecha.slice(5,7)}`:"sin historial aún"};
function histValor(hist,campo,dias){const h=histRef(hist,dias);return h?REDES.reduce((s,r)=>s+(campo==="total_seg"?(h[r+"_seguidores"]||0):(h[r+"_vistas"]||0)),0):null}

async function vistaInicio(){
  const [st,est,tend,obj,series,com]=await Promise.all([json("programador/estadisticas.json",{opcional:true}),json("produccion/estado.json"),json("produccion/tendencias.json",{opcional:true}),
    json("produccion/objetivos.json",{opcional:true}),json("programador/series.json",{opcional:true}),json("programador/comunidad.json",{opcional:true})]);
  await cargarCal().catch(()=>null);
  const cu=st?.cuentas||{},tot=k=>REDES.reduce((s,r)=>s+(cu[r]?.[k]||0),0),hist=st?.historial||[];
  const prox=(cal?.posts||[]).filter(p=>p.estado==="pendiente").sort((a,b)=>new Date(a.hora)-new Date(b.hora));
  const fallidos=(cal?.posts||[]).filter(p=>(p.estado==="error"||p.estado==="caducado")&&Date.now()-new Date(p.hora)<3*864e5);
  const v=est.videos,cuenta=e=>v.filter(x=>x.estado===e).length;
  const pubSemana=(cal?.posts||[]).filter(p=>(p.estado==="publicado"||p.estado==="borrador")&&Date.now()-new Date(p.hora)<7*864e5).length;
  // alertas
  const al=[];
  for(const d of despegando(series).slice(0,2))al.push(["ok","rocket",`«${d.titulo}» está despegando`,`${NOMBRE[d.red]} · ${fmtN(d.vistas)} vistas en ${Math.round(d.horas)} h, ${d.ratio.toFixed(1).replace(".",",")} veces lo normal. Responde comentarios ahora y piensa en una segunda parte.`,d.url,"Ver vídeo"]);
  if(cuenta("revision"))al.push(["warn","eye",`${cuenta("revision")} vídeo(s) esperando tu revisión`,"Apruébalos para que entren en el calendario.","#/prod/borradores","Revisar"]);
  if(cuenta("propuesto"))al.push(["info","idea",`${cuenta("propuesto")} guion(es) nuevos para aprobar`,"Claude los ha preparado siguiendo las 3 reglas.","#/prod/guiones","Ver guiones"]);
  for(const x of v.filter(x=>x.error))al.push(["err","alert",`Problema con «${x.titulo}»`,x.error,"#/prod/marcha","Ver"]);
  for(const p of fallidos.slice(0,3))al.push(["err","alert",`No se publicó en ${NOMBRE[p.red]}: «${p.titulo}»`,p.ultimo_error||"Revisa la conexión de esa red.","#/pub/lista","Ver"]);
  for(const [r,e] of Object.entries(st?.errores||{}))al.push(["warn","plug",`${NOMBRE[r]}: sin datos nuevos`,permisoTexto(r,e),"#/conex","Conexiones"]);
  if(!prox.length)al.push(["warn","cal","No hay nada programado","Aprueba algún borrador o sube un vídeo para no perder ritmo.","#/prod/borradores","Producción"]);
  const preguntas=(com?.comentarios||[]).filter(c=>esPregunta(c.texto)&&!c.respuestas&&Date.now()-new Date(c.fecha)<4*864e5).length;
  if(preguntas)al.push(["info","chat",`${preguntas} pregunta(s) de seguidores sin responder`,"Responder pronto ayuda a que el algoritmo empuje el vídeo.","#/com/bandeja","Responder"]);
  const t1=(tend?.tendencias||[]).filter(t=>t.puntuacion>=70)[0];

  app.innerHTML=`<section class="card hero fade"><canvas id="h3d" aria-label="Logo 3D de explicadoen60s"></canvas>
   <div class="txt"><div class="kick">${esc(fmtDia(new Date().toISOString()))}</div><h2>${saludo()}, ${esc(usuario.split("_")[0])}</h2>
   <p>${st?`Datos de las redes ${hace(st.actualizado)}.`:"Las estadísticas aparecerán tras la primera recogida."} ${prox.length?`Siguiente publicación ${dentro(prox[0].hora)} en ${NOMBRE[prox[0].red]}.`:""}</p></div></section>
  <div class="grid g4">
   ${kpi("Seguidores",tot("seguidores"),`${delta(tot("seguidores"),histValor(hist,"total_seg",7))}<span>${refTexto(hist,7)}</span>`,"user")}
   ${kpi("Visualizaciones",tot("vistas"),`${delta(tot("vistas"),histValor(hist,"total_vis",7))}<span>${refTexto(hist,7)}</span>`,"eye")}
   ${kpi("Publicados esta semana",pubSemana,`${prox.length} en cola`,"cal")}
   ${kpi("En producción",v.filter(x=>["propuesto","aprobado","voz","escena","renderizando","rehacer","revision"].includes(x.estado)).length,`${cuenta("revision")} para revisar · ${cuenta("propuesto")} guiones`,"film")}
  </div>
  <div class="grid g21">
   <div class="card fade"><div class="h3">${ic("bell")}Lo importante ahora<span class="sub">${al.length?al.length+" avisos":""}</span></div>
    ${al.length?al.map(([t,i,b,s,url,btn])=>`<div class="alerta ${t}">${ic(i)}<div class="t"><b>${esc(b)}</b><small>${esc(s)}</small></div>${url?`<a class="btn sec peq" href="${esc(url)}" ${url.startsWith("http")?'target="_blank"':""}>${btn}</a>`:""}</div>`).join("")
     :vacio("check","Todo en orden","No hay nada urgente. Buen momento para revisar tendencias.")}</div>
   <div class="card fade"><div class="h3">${ic("target")}Objetivos</div>
    ${(obj?.objetivos||[]).slice(0,4).map(o=>{const p=progresoObjetivo(o,st);return `<div style="margin:0 0 14px"><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px"><span>${redPill(o.red)} ${o.metrica==="seguidores"?"seguidores":"visualizaciones"}</span><b class="num">${fmtN(p.actual)} / ${fmtN(o.meta)}</b></div><div class="barra"><i style="width:${Math.min(100,p.actual/o.meta*100)}%"></i></div><div class="faint peq" style="margin-top:4px">${p.prevision}</div></div>`}).join("")||vacio("target","Sin objetivos","",`<a class="btn sec peq" href="#/crec/objetivos">Crear objetivo</a>`)}
    <a class="btn fantasma peq" href="#/crec/objetivos">Ver crecimiento ${ic("ext","s")}</a></div>
  </div>
  <div class="grid g3">${REDES.map(r=>{const c=cu[r];return `<div class="card fade" style="padding:16px">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">${redPill(r)}<span class="mut peq">${esc(c?.nombre||"")}</span><span class="sub" style="margin-left:auto">${delta(c?.seguidores,histRed(hist,r,7))}</span></div>
    <div class="val num" style="font:700 30px 'Space Grotesk'" data-n="${c?.seguidores??""}">—</div><div class="mut peq">seguidores · ${fmtN(c?.vistas)} vistas · ${fmtN(c?.videos)} vídeos</div>
    <div style="margin-top:10px">${sparkline(hist.map(h=>h[r+"_seguidores"]).filter(x=>x!=null),COLOR[r])}</div></div>`}).join("")}</div>
  <div class="grid g2">
   <div class="card fade"><div class="h3">${ic("cal")}Próximas publicaciones<a class="sub" href="#/pub/semana">Calendario</a></div>${prox.slice(0,6).map(p=>`<div class="fila"><span class="hora">${fmtHora(p.hora)}</span>${redPill(p.red)}<span class="t"><b>${esc(p.titulo)}</b><small>${fmtDiaC(p.hora)} · ${dentro(p.hora)}</small></span></div>`).join("")||vacio("cal","Nada programado")}</div>
   <div class="card fade"><div class="h3">${ic("flame")}Tendencia destacada<a class="sub" href="#/tend">Ver todas</a></div>
    ${t1?`<div style="display:flex;gap:12px;align-items:flex-start"><div class="punt" style="--p:${t1.puntuacion};--c:${colorPunt(t1.puntuacion)}"><span>${t1.puntuacion}</span></div><div><b style="font-size:16px">${esc(t1.tema)}</b><p class="mut peq" style="margin:4px 0 8px">${esc(t1.angulo||t1.por_que||"")}</p>${t1.gancho?`<div class="bloque"><span class="etiqueta">Gancho</span><p>«${esc(t1.gancho)}»</p></div>`:""}</div></div>`
     :vacio("flame","Aún no hay tendencias analizadas","Claude las analiza en cada pasada (8:56 y 19:56).")}</div>
  </div>`;
  animarKpis();
  despuesDePintar=()=>heroStart($("#h3d"));
}
function histRed(hist,r,dias){const h=histRef(hist,dias);return h?h[r+"_seguidores"]:null}
const colorPunt=p=>p>=75?"var(--ok)":p>=55?"var(--acc)":p>=35?"var(--warn)":"var(--err)";
function permisoTexto(r,e){
  if(e.includes("no conectado"))return "No está conectado.";
  if(r==="youtube"&&/insufficient|403|scope/i.test(e))return "Falta el permiso de estadísticas: vuelve a conectar YouTube.";
  if(r==="tiktok"&&/scope|permission|401|403/i.test(e))return "Falta el permiso de estadísticas de TikTok.";
  return "No se pudieron actualizar los datos ("+e.slice(0,90)+")";
}
