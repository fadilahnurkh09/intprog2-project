import { useEffect, useRef, useState } from "react";
import { API_URL, virtualTryOn } from "../api.js";
import { FRAMES, STYLE_ORDER, frameDataUrl, styleInfo } from "../data/frames.js";
import ManualTryOn from "./ManualTryOn.jsx";

export function thumbSrc(style, color = "#1a1714") {
  const info = styleInfo(style);
  return info.asset
    ? `${API_URL}/assets/glasses/${info.asset}_test.png`
    : frameDataUrl(info.svg, color);
}

/** <img> thumbnail dari backend, otomatis jatuh ke SVG lokal bila gagal dimuat */
export function FrameThumb({ style, color }) {
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [style]);
  const info = styleInfo(style);
  return (
    <img
      src={failed ? frameDataUrl(info.svg, color || "#1a1714") : thumbSrc(style, color)}
      onError={() => setFailed(true)}
      alt=""
      loading="lazy"
    />
  );
}

export default function TryOn({ photoFile, photoUrl, style, onStyle, recommended }) {
  const info = styleInfo(style);
  const name = FRAMES[info.svg]?.name || style;
  const serverOk = !!info.tryOn;

  const [mode, setMode] = useState("server"); // server | manual
  const [color, setColor] = useState("#1a1714");
  const [state, setState] = useState({ status: "idle", url: "", error: "" });
  const cache = useRef(new Map()); // style -> object URL
  const [retry, setRetry] = useState(0);

  // Reset cache saat foto berganti
  useEffect(() => {
    const c = cache.current;
    return () => {
      c.forEach((u) => URL.revokeObjectURL(u));
      c.clear();
    };
  }, [photoFile]);

  useEffect(() => {
    if (mode !== "server" || !serverOk) return;
    const cached = cache.current.get(info.tryOn);
    if (cached) {
      setState({ status: "ready", url: cached, error: "" });
      return;
    }
    const ctrl = new AbortController();
    setState({ status: "loading", url: "", error: "" });
    virtualTryOn(photoFile, info.tryOn, ctrl.signal)
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        cache.current.set(info.tryOn, url);
        setState({ status: "ready", url, error: "" });
      })
      .catch((e) => {
        if (e.name !== "AbortError") setState({ status: "error", url: "", error: e.message });
      });
    return () => ctrl.abort();
  }, [photoFile, info.tryOn, serverOk, mode, retry]);

  // Model tanpa aset di server → otomatis mode manual
  const effectiveMode = serverOk ? mode : "manual";

  function download() {
    const a = document.createElement("a");
    a.href = state.url;
    a.download = `framefit-${style}.png`;
    a.click();
  }

  return (
    <section aria-labelledby="tryon-title" className="tryon-wrap">
      <div className="section-head head-row">
        <div>
          <h2 id="tryon-title">Virtual Try-On</h2>
          <p className="muted">Pilih model kacamata, lalu lihat hasilnya di fotomu.</p>
        </div>
        {serverOk && (
          <div className="seg" role="group" aria-label="Mode try-on">
            <button className={effectiveMode === "server" ? "on" : ""} onClick={() => setMode("server")}>Otomatis</button>
            <button className={effectiveMode === "manual" ? "on" : ""} onClick={() => setMode("manual")}>Atur manual</button>
          </div>
        )}
      </div>

      <div className="card model-card">
        <p className="muted small">Ganti model kacamata</p>
        <div className="model-strip">
          {STYLE_ORDER.map((s) => (
            <button
              key={s}
              type="button"
              className={`model-chip ${s === style ? "is-on" : ""}`}
              onClick={() => onStyle(s)}
              aria-pressed={s === style}
            >
              <FrameThumb style={s} />
              <span>{FRAMES[styleInfo(s).svg].name}</span>
              {recommended.includes(s) && <i className="dot" title="Direkomendasikan" />}
            </button>
          ))}
        </div>
        <p className="muted small"><i className="dot inline" /> = direkomendasikan untuk bentuk wajahmu</p>
      </div>

      {effectiveMode === "manual" ? (
        <>
          {!serverOk && (
            <p className="note-box">Model {name} belum punya aset di server, jadi dipasang di browser. Atur posisinya secara manual.</p>
          )}
          <ManualTryOn photoUrl={photoUrl} style={style} color={color} onColor={setColor} />
        </>
      ) : (
        <div className="card tryon">
          <div className="tryon-stage">
            {state.url && <img className="tryon-img" src={state.url} alt={`Hasil Virtual Try-On frame ${name}`} />}
            {state.status === "loading" && (
              <div className={`stage-loading ${state.url ? "over" : ""}`}><span className="spinner" /> Memasang {name}…</div>
            )}
            {state.status === "error" && (
              <div className="stage-loading error-state">
                <p>{state.error}</p>
                <div className="btn-row">
                  <button className="btn btn-primary" onClick={() => setRetry((n) => n + 1)}>Coba lagi</button>
                  <button className="btn btn-ghost" onClick={() => setMode("manual")}>Atur manual</button>
                </div>
              </div>
            )}
          </div>
          <div className="tryon-panel">
            <p className="eyebrow">Hasil dari server</p>
            <h2>{name}</h2>
            <p className="muted">
              Posisi dan ukuran frame dihitung otomatis dari titik mata di wajahmu. Kalau kurang pas, pakai <b>Atur manual</b>.
            </p>
            <div className="btn-row">
              <button className="btn btn-primary" onClick={download} disabled={state.status !== "ready"}>Unduh hasil</button>
              <button className="btn btn-ghost" onClick={() => setMode("manual")}>Atur manual</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
