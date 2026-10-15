import { useEffect, useMemo, useRef, useState } from "react";
import Uploader from "./components/Uploader.jsx";
import Result from "./components/Result.jsx";
import FrameCatalog from "./components/FrameCatalog.jsx";
import TryOn from "./components/TryOn.jsx";
import { predictFaceShape } from "./api.js";
import { getRecommendations } from "./data/frames.js";

const STEPS = ["Unggah foto", "Analisis AI", "Rekomendasi", "Coba virtual"];

export default function App() {
  const [file, setFile] = useState(null);
  const [photoUrl, setPhotoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [frameId, setFrameId] = useState(null);
  const [color, setColor] = useState("#1a1714");
  const abortRef = useRef(null);
  const resultsRef = useRef(null);

  const recs = useMemo(() => (result ? getRecommendations(result.face_shape) : []), [result]);

  useEffect(() => () => photoUrl && URL.revokeObjectURL(photoUrl), [photoUrl]);

  async function analyze(f) {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    setFile(f);
    setPhotoUrl(URL.createObjectURL(f));
    setResult(null);
    setFrameId(null);
    setError("");
    setLoading(true);
    try {
      const data = await predictFaceShape(f, ctrl.signal);
      setResult(data);
      setFrameId(getRecommendations(data.face_shape)[0].id);
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
    } catch (e) {
      if (e.name !== "AbortError") setError(e.message);
    } finally {
      if (abortRef.current === ctrl) setLoading(false);
    }
  }

  function reset() {
    abortRef.current?.abort();
    setFile(null);
    setPhotoUrl("");
    setResult(null);
    setFrameId(null);
    setError("");
    setLoading(false);
  }

  const step = result ? (frameId ? 3 : 2) : loading ? 1 : 0;

  return (
    <>
      <header className="site-header">
        <a className="brand" href="/" onClick={(e) => { e.preventDefault(); reset(); }}>
          <svg width="30" height="30" viewBox="0 0 64 64" aria-hidden="true">
            <rect width="64" height="64" rx="14" fill="#221d19" />
            <circle cx="21" cy="33" r="10" fill="none" stroke="#e8b86a" strokeWidth="4" />
            <circle cx="43" cy="33" r="10" fill="none" stroke="#e8b86a" strokeWidth="4" />
            <path d="M31 32q1-3 2 0" stroke="#e8b86a" strokeWidth="3" fill="none" />
          </svg>
          <span>FrameFit</span>
        </a>
        <ol className="steps" aria-label="Langkah">
          {STEPS.map((s, i) => (
            <li key={s} className={i === step ? "is-now" : i < step ? "is-done" : ""}>
              <span>{i + 1}</span>{s}
            </li>
          ))}
        </ol>
      </header>

      <main>
        {!photoUrl && (
          <section className="hero">
            <div className="hero-copy">
              <p className="eyebrow">Rekomendasi kacamata berbasis AI</p>
              <h1>Temukan kacamata yang <em>pas</em> untuk bentuk wajahmu.</h1>
              <p className="lead">
                Unggah satu foto. AI kami mengenali bentuk wajahmu, menyarankan frame yang cocok,
                lalu kamu bisa mencobanya langsung — sebelum membeli.
              </p>
            </div>
            <Uploader onPick={analyze} busy={loading} />
          </section>
        )}

        {photoUrl && (
          <div className="flow" ref={resultsRef}>
            <div className="flow-bar">
              <button className="btn btn-ghost" onClick={reset}>← Foto lain</button>
              {file && !loading && !result && error && (
                <button className="btn btn-primary" onClick={() => analyze(file)}>Coba lagi</button>
              )}
            </div>

            {loading && (
              <div className="card analyzing" role="status" aria-live="polite">
                <img src={photoUrl} alt="Fotomu" />
                <div>
                  <span className="spinner big" />
                  <h2>Menganalisis bentuk wajah…</h2>
                  <p className="muted">Biasanya hanya beberapa detik.</p>
                </div>
              </div>
            )}

            {error && <div className="card error-card" role="alert"><h2>Analisis gagal</h2><p>{error}</p></div>}

            {result && (
              <>
                <Result photoUrl={photoUrl} result={result} />
                <FrameCatalog items={recs} selectedId={frameId} onSelect={setFrameId} color={color} />
                {frameId && <TryOn photoUrl={photoUrl} frameId={frameId} color={color} onColor={setColor} onFrame={setFrameId} recommendedIds={recs.map((r) => r.id)} />}
              </>
            )}
          </div>
        )}
      </main>

      <footer className="site-footer">
        <p>FrameFit · Proyek Pemrograman Internet II · Politeknik Negeri Lampung</p>
        <p className="muted small">Hasil bersifat saran visual, bukan pengganti pemeriksaan optik.</p>
      </footer>
    </>
  );
}
