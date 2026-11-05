// ═══════════ Inicio de sesión (dos usuarios; la clave de GitHub va cifrada con la contraseña) ═══════════
const USUARIOS=["Nikoloz_Lekishvili","Christian_Civico"];
const enc=new TextEncoder(),dec=new TextDecoder();
const b64a=a=>btoa(String.fromCharCode(...new Uint8Array(a))),unb64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function claveDe(user,pass,salt){const k=await crypto.subtle.importKey("raw",enc.encode(user.toLowerCase()+"\n"+pass),"PBKDF2",false,["deriveKey"]);
  return crypto.subtle.deriveKey({name:"PBKDF2",salt,iterations:600000,hash:"SHA-256"},k,{name:"AES-GCM",length:256},false,["encrypt","decrypt"])}
async function cifrar(user,pass,texto){const salt=crypto.getRandomValues(new Uint8Array(16)),iv=crypto.getRandomValues(new Uint8Array(12));
  const k=await claveDe(user,pass,salt);return {salt:b64a(salt),iv:b64a(iv),ct:b64a(await crypto.subtle.encrypt({name:"AES-GCM",iv},k,enc.encode(texto)))}}
async function descifrar(user,pass,o){const k=await claveDe(user,pass,unb64(o.salt));return dec.decode(await crypto.subtle.decrypt({name:"AES-GCM",iv:unb64(o.iv)},k,unb64(o.ct)))}
async function leerAcceso(){try{const r=await fetch("acceso.json?t="+Date.now(),{cache:"no-store"});return r.ok?await r.json():null}catch(e){return null}}
function marcoLogin(html){document.body.classList.add("sinsesion");app=$("#app");app.innerHTML=`<div class="login fade"><div class="card login-card" style="padding:26px">
  <div class="brand" style="padding:0 0 18px"><div class="logo">60s</div><div><b>explicadoen60s</b><small>Panel de control</small></div></div>${html}</div>
  <p class="mut peq" style="text-align:center;max-width:420px;margin:16px auto">Herramienta privada de @explicadoen60s para producir, programar y analizar sus vídeos.<br><a href="privacidad.html">Privacidad</a> · <a href="terminos.html">Términos</a></p></div>`}
function pantallaToken(err){
  marcoLogin(`<h2 style="margin:0 0 4px;font-size:22px">Iniciar sesión</h2><p class="mut" style="margin:0 0 6px">Entra con tu usuario del equipo.</p>
  ${err?`<div class="msg err">${ic("alert","s")}${esc(err)}</div>`:""}
  <label for="lu">Usuario</label><input id="lu" autocomplete="username" value="${esc(usuario)}" placeholder="Nombre_Apellido">
  <label for="lp">Contraseña</label><input id="lp" type="password" autocomplete="current-password">
  <p style="margin:18px 0 10px"><button class="btn" id="entrar" style="width:100%;padding:12px">Entrar</button></p>
  <p class="mut peq" style="text-align:center;margin:0"><a href="#" id="cfg">Configurar el acceso (primera vez o clave de GitHub caducada)</a></p>`);
  const go=async()=>{const u=USUARIOS.find(x=>x.toLowerCase()===$("#lu").value.trim().toLowerCase()),pw=$("#lp").value;
    if(!u)return pantallaToken("Ese usuario no existe.");
    $("#entrar").disabled=true;$("#entrar").textContent="Comprobando…";
    const acc=await leerAcceso();if(!acc||!acc.usuarios?.[u])return pantallaConfig("Primero hay que configurar el acceso (solo una vez).");
    try{tok=await descifrar(u,pw,acc.usuarios[u])}catch(e){usuario=u;return pantallaToken("Contraseña incorrecta.")}
    try{await cargarCal()}catch(e){return pantallaConfig("La clave de GitHub guardada ya no funciona (¿caducó?). Configura una nueva.")}
    usuario=u;try{localStorage.setItem("ghtoken",tok);localStorage.setItem("usuario",u)}catch(e){}
    document.body.classList.remove("sinsesion");arrancar()};
  $("#entrar").onclick=go;$("#lp").onkeydown=e=>{if(e.key==="Enter")go()};
  $("#cfg").onclick=e=>{e.preventDefault();pantallaConfig()};
}
function pantallaConfig(err){
  marcoLogin(`<h2 style="margin:0 0 4px;font-size:22px">Configurar el acceso</h2>
  <p class="mut">Se hace una sola vez. La clave de GitHub se guarda <b>cifrada con la contraseña</b>: sin la contraseña no sirve de nada.</p>
  ${err?`<div class="msg warn">${ic("alert","s")}${esc(err)}</div>`:""}
  <ol class="mut peq" style="padding-left:18px"><li>Con la cuenta <b>explicadoen60s</b>, abre <a href="https://github.com/settings/personal-access-tokens/new" target="_blank">crear token</a>.</li>
  <li>Caducidad: la más larga posible. Repository access: <b>Only select repositories</b> → <i>${R}</i>.</li>
  <li>Permissions → <b>Contents</b>, <b>Actions</b> e <b>Issues</b>: <i>Read and write</i>. Genera y copia.</li></ol>
  <label for="ct">Token de GitHub</label><input id="ct" type="password" placeholder="github_pat_…" autocomplete="off">
  <label for="cp1">Contraseña del panel (para los dos usuarios)</label><input id="cp1" type="password" autocomplete="new-password">
  <label for="cp2">Repite la contraseña</label><input id="cp2" type="password" autocomplete="new-password">
  <label for="cu">¿Quién eres?</label><select id="cu">${USUARIOS.map(u=>`<option ${u===usuario?"selected":""}>${u}</option>`).join("")}</select>
  <div id="cmsg"></div><p style="margin:18px 0 10px"><button class="btn" id="cgo" style="width:100%;padding:12px">Guardar y entrar</button></p>
  <p class="mut peq" style="text-align:center;margin:0"><a href="#" id="volver">Volver</a></p>`);
  $("#volver").onclick=e=>{e.preventDefault();pantallaToken()};
  $("#cgo").onclick=async()=>{const t=$("#ct").value.trim(),p1=$("#cp1").value,p2=$("#cp2").value,u=$("#cu").value,m=x=>$("#cmsg").innerHTML=`<div class="msg err">${esc(x)}</div>`;
    if(!t)return m("Falta el token.");if(p1.length<8)return m("La contraseña es demasiado corta.");if(p1!==p2)return m("Las contraseñas no coinciden.");
    $("#cgo").disabled=true;$("#cgo").textContent="Cifrando y guardando…";tok=t;
    try{await cargarCal();
      const usuarios={};for(const x of USUARIOS)usuarios[x]=await cifrar(x,p1,t);
      let sha;try{sha=(await gh(`/contents/docs/acceso.json?ref=main`)).sha}catch(e){}
      await gh("/contents/docs/acceso.json",{method:"PUT",body:JSON.stringify({message:"Panel: acceso configurado [skip ci]",content:b64e(JSON.stringify({version:1,iteraciones:600000,usuarios},null,1)+"\n"),branch:"main",...(sha?{sha}:{})})});
      usuario=u;try{localStorage.setItem("ghtoken",t);localStorage.setItem("usuario",u)}catch(e){}
      document.body.classList.remove("sinsesion");arrancar()}
    catch(e){$("#cgo").disabled=false;$("#cgo").textContent="Guardar y entrar";m(e.status===401?"El token no es válido.":e.message)}};
}
function salir(){try{localStorage.removeItem("ghtoken")}catch(e){}tok="";heroStop();pantallaToken()}
