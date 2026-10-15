import { useCallback, useEffect, useRef, useState } from "react";
import { COLORS, FRAMES, frameDataUrl } from "../data/frames.js";
import { detectEyes } from "../faceLandmarks.js";

const MAX_DIM = 1280;

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error("Gagal memuat gambar."));
    img.src = src;
  });
}

export default function TryOn({ photoUrl, frameId, color, onColor, onFrame, recommendedIds = [] }) {
  const canvasRef = useRef(null);
  const photoRef = useRef(null);
  const glassesRef = useRef(null);
  const baseRef = useRef(null); // transform awal (untuk reset)
  const dragRef = useRef(null);

  const [t, setT] = useState(null); // {cx, cy, s, rot}
  const [status, setStatus] = useState("loading"); // loading | auto | manual
  const [photoReady, setPhotoReady] = useState(false);
  const [glassesReady, setGlassesReady] = useState(0);

  // Muat foto + deteksi posisi mata
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

      let base = { cx: w / 2, cy: h * 0.42, s: (w * 0.3) / 150, rot: 0 };
      let mode = "manual";
      try {
        const eyes = await detectEyes(img);
        if (eyes && alive) {
          const dx = eyes.right.x * w - eyes.left.x * w;
          const dy = eyes.right.y * h - eyes.left.y * h;
          base = {
            cx: ((eyes.left.x + eyes.right.x) / 2) * w,
            cy: ((eyes.left.y + eyes.right.y) / 2) * h,
            s: Math.hypot(dx, dy) / 150,
            rot: Math.atan2(dy, dx),
          };
          mode = "auto";
        }
      } catch (e) {
        console.warn("Deteksi landmark gagal, memakai posisi manual:", e);
      }
      if (!alive) return;
      baseRef.current = base;
      setT(base);
      setStatus(mode);
      setPhotoReady(true);
    })().catch(() => alive && setStatus("manual"));
    return () => {
      alive = false;
    };
  }, [photoUrl]);

  // Muat gambar frame saat pilihan frame/warna berubah
  useEffect(() => {
    let alive = true;
    loadImage(frameDataUrl(frameId, color)).then((img) => {
      if (!alive) return;
      glassesRef.current = img;
      setGlassesReady((n) => n + 1);
    });
    return () => {
      alive = false;
    };
  }, [frameId, color]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const p = photoRef.current;
    if (!canvas || !p || !t) return;
    canvas.width = p.w;
    canvas.height = p.h;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(p.img, 0, 0, p.w, p.h);
    const g = glassesRef.current;
    if (g) {
      ctx.save();
      ctx.translate(t.cx, t.cy);
      ctx.rotate(t.rot);
      ctx.shadowColor = "rgba(0,0,0,0.28)";
      ctx.shadowBlur = 6 * t.s;
      ctx.shadowOffsetY = 3 * t.s;
      ctx.drawImage(g, -170 * t.s, -50 * t.s, 340 * t.s, 100 * t.s);
      ctx.restore();
    }
  }, [t]);

  useEffect(() => {
    if (photoReady) draw();
  }, [draw, photoReady, glassesReady]);

  // Drag untuk menggeser
  function onPointerDown(e) {
    if (!t) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    dragRef.current = { x: e.clientX, y: e.clientY, cx: t.cx, cy: t.cy };
  }
  function onPointerMove(e) {
    const d = dragRef.current;
    if (!d) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const k = canvasRef.current.width / rect.width;
    setT((prev) => ({ ...prev, cx: d.cx + (e.clientX - d.x) * k, cy: d.cy + (e.clientY - d.y) * k }));
  }
  function onPointerUp() {
    dragRef.current = null;
  }

  function nudge(dx, dy) {
    setT((p) => ({ ...p, cx: p.cx + dx, cy: p.cy + dy }));
  }

  function download() {
    canvasRef.current?.toBlob((blob) => {
      if (!blob) return;
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `framefit-${FRAMES[frameId].name.toLowerCase()}.png`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    }, "image/png");
  }

  const base = baseRef.current;
  const sizePct = base && t ? Math.round((t.s / base.s) * 100) : 100;
  const rotDeg = base && t ? Math.round(((t.rot - base.rot) * 180) / Math.PI) : 0;

  return (
    <section className="card tryon" aria-labelledby="tryon-title">
      <div className="tryon-stage">
        <canvas
          ref={canvasRef}
          className="tryon-canvas"
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
          role="img"
          aria-label={`Pratinjau Virtual Try-On frame ${FRAMES[frameId].name}`}
        />
        {!photoReady && <div className="stage-loading"><span className="spinner" /> Menyiapkan pratinjau…</div>}
      </div>

      <div className="tryon-panel">
        <p className="eyebrow">Virtual Try-On</p>
        <h2 id="tryon-title">{FRAMES[frameId].name}</h2>
        <p className={`status status-${status}`}>
          {status === "loading" && "Mendeteksi posisi mata…"}
          {status === "auto" && "✓ Posisi mata terdeteksi — frame dipasang otomatis."}
          {status === "manual" && "Deteksi otomatis tidak tersedia — geser dan sesuaikan frame secara manual."}
        </p>

        <fieldset className="model-picker">
          <legend>Ganti model kacamata</legend>
          <div className="model-strip">
            {Object.entries(FRAMES).map(([id, f]) => (
              <button
                key={id}
                type="button"
                className={`model-chip ${id === frameId ? "is-on" : ""}`}
                onClick={() => onFrame(id)}
                aria-pressed={id === frameId}
                title={f.name}
              >
                <img src={frameDataUrl(id, color)} alt="" />
                <span>{f.name}</span>
                {recommendedIds.includes(id) && <i className="dot" title="Direkomendasikan" />}
              </button>
            ))}
          </div>
          <p className="muted small"><i className="dot inline" /> = direkomendasikan untuk bentuk wajahmu</p>
        </fieldset>

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

        <label className="slider">
          <span>Ukuran <b>{sizePct}%</b></span>
          <input
            type="range" min="60" max="160" value={sizePct} disabled={!t}
            onChange={(e) => setT((p) => ({ ...p, s: (base.s * e.target.value) / 100 }))}
          />
        </label>
        <label className="slider">
          <span>Kemiringan <b>{rotDeg}°</b></span>
          <input
            type="range" min="-30" max="30" value={rotDeg} disabled={!t}
            onChange={(e) => setT((p) => ({ ...p, rot: base.rot + (e.target.value * Math.PI) / 180 }))}
          />
        </label>

        <div className="nudge" aria-label="Geser frame">
          <button className="btn btn-small" onClick={() => nudge(0, -4)} aria-label="Geser naik">↑</button>
          <button className="btn btn-small" onClick={() => nudge(-4, 0)} aria-label="Geser kiri">←</button>
          <button className="btn btn-small" onClick={() => nudge(4, 0)} aria-label="Geser kanan">→</button>
          <button className="btn btn-small" onClick={() => nudge(0, 4)} aria-label="Geser turun">↓</button>
        </div>
        <p className="muted small">Tip: seret langsung pada foto untuk memindahkan frame.</p>

        <div className="btn-row">
          <button className="btn btn-primary" onClick={download} disabled={!photoReady}>Unduh hasil</button>
          <button className="btn btn-ghost" onClick={() => base && setT(base)} disabled={!photoReady}>Reset posisi</button>
        </div>
      </div>
    </section>
  );
}
