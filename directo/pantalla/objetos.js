// Objetos de los duelos, hechos con piezas sencillas (sin marcas). Cada uno devuelve:
// { g: THREE.Group (apoyado en y=0), h: altura, estilo, restos: [colores], jugo: color o null }
// estilo: "aplasta" (se arruga), "estalla" (vidrio/cáscara en trozos), "revienta" (zumo), "piezas" (salen piezas)
import * as THREE from "/three/build/three.module.js";

const M = (c, o = {}) => new THREE.MeshLambertMaterial({ color: c, ...o });
function malla(geo, mat, x = 0, y = 0, z = 0) { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; return m; }
function rx(m, a) { m.rotation.x = a; return m; }
function torno(perfil, mat, seg = 48) { return malla(new THREE.LatheGeometry(perfil.map(([r, y]) => new THREE.Vector2(r, y)), seg), mat); }

const OBJ = {
  huevo() {
    const g = new THREE.Group(), p = [];
    for (let i = 0; i <= 24; i++) { const t = i / 24, a = Math.PI * t; p.push([Math.max(0.001, Math.sin(a) * 0.5 * (1 - 0.18 * t)), 0.68 - Math.cos(a) * 0.68]); }
    g.add(torno(p, M(0xf3e3c3))); return { g, h: 1.36, estilo: "estalla", restos: [0xf3e3c3, 0xfff6e4], jugo: 0xffc21a };
  },
  bombilla() {
    const g = new THREE.Group();
    const vid = M(0xd8f0ff, { transparent: true, opacity: 0.55 });
    const bulbo = malla(new THREE.SphereGeometry(0.55, 40, 28), vid, 0, 1.1); bulbo.castShadow = false; g.add(bulbo);
    const cuello = malla(new THREE.CylinderGeometry(0.33, 0.25, 0.4, 32, 1, true), vid, 0, 0.6); cuello.castShadow = false; g.add(cuello);
    g.add(malla(new THREE.CylinderGeometry(0.25, 0.22, 0.42, 32), M(0xb9bec6), 0, 0.21));
    for (let k = 0; k < 4; k++) g.add(rx(malla(new THREE.TorusGeometry(0.245, 0.025, 8, 32), M(0x9aa0aa), 0, 0.08 + k * 0.09), Math.PI / 2));
    g.add(malla(new THREE.SphereGeometry(0.09, 16, 12), M(0x333333), 0, 0.0));
    const fil = new THREE.Mesh(new THREE.TorusGeometry(0.16, 0.018, 6, 24, Math.PI), new THREE.MeshBasicMaterial({ color: 0xffd34d })); fil.position.y = 1.05; g.add(fil);
    g.add(malla(new THREE.CylinderGeometry(0.012, 0.012, 0.5, 6), M(0x777777), -0.16, 0.8)); g.add(malla(new THREE.CylinderGeometry(0.012, 0.012, 0.5, 6), M(0x777777), 0.16, 0.8));
    return { g, h: 1.65, estilo: "estalla", restos: [0xd8f0ff, 0xbfe4ff, 0xb9bec6], jugo: null };
  },
  lata() {
    const g = new THREE.Group();
    g.add(torno([[0.001, 0], [0.36, 0], [0.42, 0.08], [0.42, 1.12], [0.34, 1.26], [0.001, 1.26]], M(0xd7262e)));
    g.add(malla(new THREE.CylinderGeometry(0.34, 0.34, 0.03, 40), M(0xc9ced6), 0, 1.265));
    g.add(malla(new THREE.CylinderGeometry(0.43, 0.43, 0.22, 40, 1, true), M(0xf4f4f4, { side: THREE.DoubleSide }), 0, 0.62));
    g.add(malla(new THREE.BoxGeometry(0.2, 0.02, 0.12), M(0xaab0b8), 0.05, 1.29, 0));
    return { g, h: 1.3, estilo: "aplasta", restos: [0xd7262e, 0xc9ced6], jugo: 0x6b3a1f };
  },
  botella() {
    const g = new THREE.Group();
    const pl = M(0x9fd4f5, { transparent: true, opacity: 0.6 });
    const b = torno([[0.001, 0], [0.38, 0], [0.42, 0.1], [0.42, 1.05], [0.36, 1.3], [0.16, 1.55], [0.14, 1.72], [0.001, 1.72]], pl); b.castShadow = false; g.add(b);
    g.add(malla(new THREE.CylinderGeometry(0.43, 0.43, 0.36, 40, 1, true), M(0x2a7fd4, { side: THREE.DoubleSide }), 0, 0.62));
    g.add(malla(new THREE.CylinderGeometry(0.17, 0.17, 0.16, 24), M(0x1f5fb8), 0, 1.8));
    return { g, h: 1.88, estilo: "aplasta", restos: [0x9fd4f5, 0x2a7fd4], jugo: 0xbfe8ff };
  },
  sandia() {
    const g = new THREE.Group();
    const geo = new THREE.SphereGeometry(0.75, 48, 32); const col = [];
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) { const a = Math.atan2(pos.getZ(i), pos.getX(i)); const r = Math.sin(a * 9 + Math.sin(pos.getY(i) * 6) * 0.6) > 0.25; const c = new THREE.Color(r ? 0x1f6b2a : 0x3fa046); col.push(c.r, c.g, c.b); }
    geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
    const s = malla(geo, M(0xffffff, { vertexColors: true }), 0, 0.62); s.scale.set(1, 0.82, 0.95); g.add(s);
    return { g, h: 1.24, estilo: "revienta", restos: [0xe8364a, 0x3fa046, 0x1f6b2a, 0x222222], jugo: 0xe8364a };
  },
  pelota() {
    const g = new THREE.Group();
    g.add(malla(new THREE.SphereGeometry(0.5, 40, 28), M(0xd6ec3a), 0, 0.5));
    const pts = []; for (let i = 0; i <= 80; i++) { const t = i / 80 * Math.PI * 2; const v = new THREE.Vector3(Math.cos(t), 0.45 * Math.sin(2 * t), Math.sin(t)).normalize().multiplyScalar(0.505); pts.push(v); }
    const seam = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true), 120, 0.025, 6, true), M(0xffffff)); seam.position.y = 0.5; g.add(seam);
    return { g, h: 1.0, estilo: "aplasta", restos: [0xd6ec3a, 0xffffff], jugo: null };
  },
  movil() {
    const g = new THREE.Group();
    const cuerpo = malla(new THREE.BoxGeometry(0.8, 1.6, 0.12), M(0x2b2f36), 0, 0.82); g.add(cuerpo);
    g.add(malla(new THREE.BoxGeometry(0.72, 1.48, 0.01), new THREE.MeshLambertMaterial({ color: 0x182235, emissive: 0x0d1830 }), 0, 0.82, 0.066));
    for (let k = 0; k < 6; k++) g.add(malla(new THREE.BoxGeometry(0.13, 0.13, 0.012), new THREE.MeshLambertMaterial({ color: [0x3fa7ff, 0xff5a5a, 0x5ad86a, 0xffc93a, 0xa06bff, 0xff8a3a][k], emissive: 0x111111 }), -0.2 + (k % 3) * 0.2, 1.3 - Math.floor(k / 3) * 0.22, 0.074));
    g.add(rx(malla(new THREE.CylinderGeometry(0.07, 0.07, 0.04, 20), M(0x111111), -0.22, 1.45, -0.08), Math.PI / 2));
    g.rotation.y = -0.25;
    return { g, h: 1.64, estilo: "piezas", restos: [0x2b2f36, 0x182235, 0x3d8b45, 0xc9ced6, 0x9fdcff], jugo: null };
  },
  mando() {
    const g = new THREE.Group();
    const c = malla(new THREE.BoxGeometry(0.42, 1.5, 0.2), M(0x24272c), 0, 0.76); g.add(c);
    const cols = [0xd7262e, 0xe0e0e0, 0xe0e0e0, 0xe0e0e0, 0x3a8dde, 0x4bbf5a, 0xf2c230, 0xe0e0e0, 0xe0e0e0];
    cols.forEach((col, k) => g.add(rx(malla(new THREE.CylinderGeometry(0.05, 0.05, 0.04, 16), M(col), -0.12 + (k % 3) * 0.12, 1.35 - Math.floor(k / 3) * 0.2, 0.11), Math.PI / 2)));
    g.add(rx(malla(new THREE.CylinderGeometry(0.11, 0.11, 0.04, 24), M(0x55595f), 0, 0.62, 0.11), Math.PI / 2));
    g.rotation.y = 0.3;
    return { g, h: 1.52, estilo: "piezas", restos: [0x24272c, 0xe0e0e0, 0xd7262e, 0x3d8b45, 0xc0a040], jugo: null };
  },
  tomate() {
    const g = new THREE.Group();
    const t = malla(new THREE.SphereGeometry(0.55, 40, 28), M(0xe53a2b), 0, 0.46); t.scale.set(1, 0.82, 1); g.add(t);
    for (let k = 0; k < 6; k++) { const h = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.32, 6), M(0x3c8f2e)); h.position.set(Math.cos(k) * 0.1, 0.9, Math.sin(k) * 0.1); h.rotation.set(Math.PI / 2 - 0.3, 0, -k + Math.PI / 2); h.rotation.order = "YXZ"; h.rotation.y = -k; g.add(h); }
    g.add(malla(new THREE.CylinderGeometry(0.03, 0.04, 0.16, 8), M(0x3c8f2e), 0, 0.98));
    return { g, h: 1.02, estilo: "revienta", restos: [0xe53a2b, 0xffc94a, 0x3c8f2e], jugo: 0xe53a2b };
  },
  donut() {
    const g = new THREE.Group();
    const m = malla(new THREE.TorusGeometry(0.48, 0.24, 24, 48), M(0xd49a5a), 0, 0.24); m.rotation.x = Math.PI / 2; g.add(m);
    const gl = malla(new THREE.TorusGeometry(0.48, 0.245, 24, 48), M(0xf27fb2), 0, 0.27); gl.rotation.x = Math.PI / 2; gl.scale.z = 0.75; g.add(gl);
    const cs = [0xffffff, 0x4fc3f7, 0xffd54f, 0x81c784, 0xba68c8];
    for (let k = 0; k < 40; k++) { const a = k * 2.4, r = 0.48 + Math.sin(k * 1.7) * 0.16; const s = malla(new THREE.CapsuleGeometry(0.018, 0.06, 2, 6), M(cs[k % 5]), Math.cos(a) * r, 0.47, Math.sin(a) * r); s.rotation.set(Math.PI / 2, 0, a * 3); g.add(s); }
    g.rotation.x = 0.6; g.position.y = 0.25;
    return { g, h: 0.62, estilo: "aplasta", restos: [0xd49a5a, 0xf27fb2], jugo: null };
  },
  cubo() {
    const g = new THREE.Group(); const s = 0.36, cs = [0xd7262e, 0xff8a1a, 0xffffff, 0xf2d230, 0x2a7fd4, 0x3faa4a];
    for (let x = -1; x <= 1; x++) for (let y = 0; y < 3; y++) for (let z = -1; z <= 1; z++) {
      const mats = [x === 1 ? cs[0] : 0x111111, x === -1 ? cs[1] : 0x111111, y === 2 ? cs[2] : 0x111111, y === 0 ? cs[3] : 0x111111, z === 1 ? cs[4] : 0x111111, z === -1 ? cs[5] : 0x111111].map(c => M(c));
      const b = new THREE.Mesh(new THREE.BoxGeometry(s * 0.94, s * 0.94, s * 0.94), mats); b.position.set(x * s, s / 2 + y * s, z * s); b.castShadow = true; g.add(b);
    }
    g.rotation.y = 0.6;
    return { g, h: 1.08, estilo: "piezas", restos: cs, jugo: null };
  },
  vela() {
    const g = new THREE.Group();
    g.add(malla(new THREE.CylinderGeometry(0.3, 0.32, 1.3, 32), M(0xf6efe0), 0, 0.65));
    g.add(malla(new THREE.CylinderGeometry(0.015, 0.015, 0.14, 6), M(0x222222), 0, 1.37));
    const fl = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), new THREE.MeshBasicMaterial({ color: 0xffb21a })); fl.scale.set(1, 2.2, 1); fl.position.y = 1.55; fl.name = "llama"; g.add(fl);
    return { g, h: 1.44, estilo: "aplasta", restos: [0xf6efe0, 0xe9dcc2], jugo: null };
  },
};

export function crearObjeto(modelo) {
  const f = OBJ[modelo] || OBJ.lata; const o = f();
  o.g.traverse(m => { if (m.isMesh) { m.castShadow = m.castShadow !== false; } });
  return o;
}
export const MODELOS = Object.keys(OBJ);
