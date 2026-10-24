import { useCallback, useEffect, useRef, useState } from "react";
import { API_URL } from "../api.js";
import { COLORS, FRAMES, frameDataUrl, styleInfo } from "../data/frames.js";
import { FIT_VERTICAL_ANCHOR, FIT_WIDTH_RATIO } from "../data/fit.js";
import { detectEyeCorners } from "../faceLandmarks.js";

const MAX_DIM = 1280;

function loadImage(src, cors = false) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    if (cors) img.crossOrigin = "anonymous";
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error("Gagal memuat gambar."));
    img.src = src;
  });
}

// Potong area transparan di sekeliling kacamata (sama seperti `alpha.getbbox()` di backend)
function cropToContent(img) {
  const c = document.createElement("canvas");
  c.width = img.naturalWidth || img.width;
  c.height = img.naturalHeight || img.height;
  const ctx = c.getContext("2d", { willReadFrequently: true });
  ctx.drawImage(img, 0, 0);
  const { data, width, height } = ctx.getImageData(0, 0, c.width, c.height);
  let minX = width, minY = height, maxX = -1, maxY = -1;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (data[(y * width + x) * 4 + 3] > 0) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  if (maxX < 0) return c;
  const out = document.createElement("canvas");
  out.width = maxX - minX + 1;
  out.height = maxY - minY + 1;
  out.getContext("2d").drawImage(c, minX, minY, out.width, out.height, 0, 0, out.width, out.height);
  return out;
}

const cache = new Map();
/** Gambar kacamata yang sama dengan server (PNG); SVG lokal hanya jika model belum punya PNG. */
async function loadGlasses(style, color) {
  const info = styleInfo(style);
  const key = info.asset ? `png:${info.asset}` : `svg:${info.svg}:${color}`;
  if (cache.has(key)) return cache.get(key);
  let img;
  if (info.asset) {
    try {
      img = await loadImage(`${API_URL}/assets/glasses/${info.asset}_test.png`, true);
    } catch {
      img = null;
    }
  }
  const usedSvg = !img;
  if (!img) img = await loadImage(frameDataUrl(info.svg, color));
  let cropped;
  try {
    cropped = cropToContent(img);
  } catch {
    cropped = img; // canvas ter-taint (CORS) — pakai apa adanya
  }
  const result = { source: cropped, w: cropped.width, h: cropped.height, usedSvg };
  cache.set(key, result);
  return result;
}

export default function ManualTryOn({ photoUrl, style, color, onColor }) {
  const info = styleInfo(style);
  const name = FRAMES[info.svg]?.name || style;

  const canvasRef = useRef(null);
  const photoRef = useRef(null);
  const dragRef = useRef(null);

  const [eye, setEye] = useState(null); // {cx, cy, dist, rot} dari landmark / default
  const [glasses, setGlasses] = useState(null);
  const [adj, setAdj] = useState({ dx: 0, dy: 0, k: 1, dr: 0 }); // penyesuaian pengguna
  const [status, setStatus] = useState("loading"); // loading | auto | manual
  const [photoReady, setPhotoReady] = useState(false);

  // Foto + deteksi sudut mata
  useEffect(() => {
    let alive = true;
    setPhotoReady(false);
    setStatus("loading");
    (async () => {
      const img = await loadImage(photoUrl);
      if (!alive) return;
      const ratio = Math.min(1, MAX_DIM / Math.max(img.naturalWidth, img.naturalHeight));
      const w = Math.round(img.naturalWidth * ratio);
      const h = Math.round(img.naturalHeight * ratio);
      photoRef.current = { img, w, h };

      let base = { cx: w / 2, cy: h * 0.42, dist: w * 0.22, rot: 0 };
      let mode = "manual";
      try {
        const e = await detectEyeCorners(img);
        if (e && alive) {
          const dx = (e.right.x - e.left.x) * w;
          const dy = (e.right.y - e.left.y) * h;
          base = {
            cx: ((e.left.x + e.right.x) / 2) * w,
            cy: ((e.left.y + e.right.y) / 2) * h,
            dist: Math.hypot(dx, dy),
            rot: Math.atan2(dy, dx),
          };
          mode = "auto";
        }
      } catch (err) {
        console.warn("Deteksi landmark gagal, memakai posisi manual:", err);
      }
      if (!alive) return;
      setEye(base);
      setStatus(mode);
      setPhotoReady(true);
    })().catch(() => alive && setStatus("manual"));
    return () => {
      alive = false;
    };
  }, [photoUrl]);

  // Gambar kacamata (ganti model → penyesuaian direset)
  useEffect(() => {
    let alive = true;
    setAdj({ dx: 0, dy: 0, k: 1, dr: 0 });
    loadGlasses(style, color).then((g) => alive && setGlasses(g));
    return () => {
      alive = false;
    };
  }, [style, color]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const p = photoRef.current;
    if (!canvas || !p || !eye) return;
    canvas.width = p.w;
    canvas.height = p.h;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(p.img, 0, 0, p.w, p.h);
    if (!glasses) return;

    // Sama seperti backend: lebar = jarak mata × rasio, tinggi proporsional
    const s = ((eye.dist * FIT_WIDTH_RATIO) / glasses.w) * adj.k;
    const gw = glasses.w * s;
    const gh = glasses.h * s;
    const rot = eye.rot + adj.dr;
    // Tinggi bingkai setelah diputar (backend memakai rotate(expand=True))
    const rotH = gw * Math.abs(Math.sin(rot)) + gh * Math.abs(Math.cos(rot));
    const cx = eye.cx + adj.dx;
    const cy = eye.cy + adj.dy + (0.5 - FIT_VERTICAL_ANCHOR) * rotH;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rot);
    ctx.drawImage(glasses.source, -gw / 2, -gh / 2, gw, gh);
    ctx.restore();
  }, [eye, glasses, adj]);

  useEffect(() => {
    if (photoReady) draw();
  }, [draw, photoReady]);

  // Geser dengan drag
  function onPointerDown(e) {
    e.currentTarget.setPointerCapture(e.pointerId);
    dragRef.current = { x: e.clientX, y: e.clientY, dx: adj.dx, dy: adj.dy };
  }
  function onPointerMove(e) {
    const d = dragRef.current;
    if (!d) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const k = canvasRef.current.width / rect.width;
    setAdj((a) => ({ ...a, dx: d.dx + (e.clientX - d.x) * k, dy: d.dy + (e.clientY - d.y) * k }));
  }
  const onPointerUp = () => (dragRef.current = null);
  const nudge = (dx, dy) => setAdj((a) => ({ ...a, dx: a.dx + dx, dy: a.dy + dy }));

  function download() {
    canvasRef.current?.toBlob((blob) => {
      if (!blob) return;
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `framefit-${style}-manual.png`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    }, "image/png");
  }

  const sizePct = Math.round(adj.k * 100);
  const rotDeg = Math.round((adj.dr * 180) / Math.PI);
  const ready = photoReady && !!glasses;

  return (
    <section className="card tryon" aria-labelledby="manual-title">
      <div className="tryon-stage">
        <canvas
          ref={canvasRef}
          className="tryon-canvas"
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
          role="img"
          aria-label={`Pratinjau Virtual Try-On frame ${name}`}
        />
        {!photoReady && <div className="stage-loading"><span className="spinner" /> Menyiapkan pratinjau…</div>}
      </div>

      <div className="tryon-panel">
        <p className="eyebrow">Mode manual</p>
        <h2 id="manual-title">{name}</h2>
        <p className={`status status-${status}`}>
          {status === "loading" && "Mendeteksi posisi mata…"}
          {status === "auto" && "✓ Posisi mata terdeteksi — frame dipasang otomatis."}
          {status === "manual" && "Deteksi otomatis tidak tersedia — geser dan sesuaikan frame secara manual."}
        </p>

        {glasses?.usedSvg && (
          <fieldset className="swatches">
            <legend>Warna frame</legend>
            {COLORS.map((c) => (
              <button
                key={c.id}
                type="button"
                className={`swatch ${color === c.value ? "is-on" : ""}`}
                style={{ "--c": c.value }}
                onClick={() => onColor(c.value)}
                aria-label={c.name}
                aria-pressed={color === c.value}
                title={c.name}
              />
            ))}
          </fieldset>
        )}

        <label className="slider">
          <span>Ukuran <b>{sizePct}%</b></span>
          <input type="range" min="60" max="160" value={sizePct} disabled={!ready}
            onChange={(e) => setAdj((a) => ({ ...a, k: e.target.value / 100 }))} />
        </label>
        <label className="slider">
          <span>Kemiringan <b>{rotDeg}°</b></span>
          <input type="range" min="-30" max="30" value={rotDeg} disabled={!ready}
            onChange={(e) => setAdj((a) => ({ ...a, dr: (e.target.value * Math.PI) / 180 }))} />
        </label>

        <div className="nudge" aria-label="Geser frame">
          <button className="btn btn-small" onClick={() => nudge(0, -4)} aria-label="Geser naik">↑</button>
          <button className="btn btn-small" onClick={() => nudge(-4, 0)} aria-label="Geser kiri">←</button>
          <button className="btn btn-small" onClick={() => nudge(4, 0)} aria-label="Geser kanan">→</button>
          <button className="btn btn-small" onClick={() => nudge(0, 4)} aria-label="Geser turun">↓</button>
        </div>
        <p className="muted small">Tip: seret langsung pada foto untuk memindahkan frame.</p>

        <div className="btn-row">
          <button className="btn btn-primary" onClick={download} disabled={!ready}>Unduh hasil</button>
          <button className="btn btn-ghost" onClick={() => setAdj({ dx: 0, dy: 0, k: 1, dr: 0 })} disabled={!ready}>Reset posisi</button>
        </div>
      </div>
    </section>
  );
}
