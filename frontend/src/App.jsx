import { useEffect, useRef, useState } from "react";
import Uploader from "./components/Uploader.jsx";
import Result from "./components/Result.jsx";
import FrameCatalog from "./components/FrameCatalog.jsx";
import TryOn from "./components/TryOn.jsx";
import AuthPage from "./components/AuthPage.jsx";
import { analyzeFace } from "./api.js";
import { useAuth } from "./auth.jsx";
import { prepareImage } from "./imageUtil.js";
import { useInstallPrompt, useOnline } from "./pwa.js";

const STEPS = ["Unggah foto", "Analisis AI", "Rekomendasi", "Coba virtual"];

export default function App() {
  const { user, checking, logout } = useAuth();
  const online = useOnline();
  const pwa = useInstallPrompt();

  const [file, setFile] = useState(null);
  const [photoUrl, setPhotoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [style, setStyle] = useState(null);
  const abortRef = useRef(null);
  const resultsRef = useRef(null);

  useEffect(() => () => photoUrl && URL.revokeObjectURL(photoUrl), [photoUrl]);

  function reset() {
    abortRef.current?.abort();
    setFile(null);
    setPhotoUrl("");
    setResult(null);
    setStyle(null);
    setError("");
    setLoading(false);
  }

  // Keluar → bersihkan data foto/hasil dari memori
  function handleLogout() {
    reset();
    logout();
  }

  async function analyze(original) {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    setResult(null);
    setStyle(null);
    setError("");
    setLoading(true);
    setPhotoUrl(URL.createObjectURL(original));
    try {
      const f = await prepareImage(original);
      setFile(f);
      const data = await analyzeFace(f, ctrl.signal);
      setResult(data);
      setStyle(data.recommendations?.[0]?.style || "round");
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
    } catch (e) {
      if (e.name !== "AbortError") setError(e.message);
    } finally {
      if (abortRef.current === ctrl) setLoading(false);
    }
  }

  const recs = result?.recommendations || [];
  const step = !user ? 0 : result ? (style ? 3 : 2) : loading ? 1 : 0;

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

        {user && (
          <ol className="steps" aria-label="Langkah">
            {STEPS.map((s, i) => (
              <li key={s} className={i === step ? "is-now" : i < step ? "is-done" : ""}>
                <span>{i + 1}</span>{s}
              </li>
            ))}
          </ol>
        )}

        <div className="header-actions">
          {pwa.canInstall && <button className="btn btn-small" onClick={pwa.install}>Pasang aplikasi</button>}
          {user && (
            <>
              <span className="user-chip" title={user.email}>{user.name}</span>
              <button className="btn btn-small" onClick={handleLogout}>Keluar</button>
            </>
          )}
        </div>
      </header>

      {!online && (
        <div className="offline-bar" role="status">
          Kamu sedang offline. Analisis dan try-on butuh koneksi ke server.
        </div>
      )}

      <main>
        {checking ? (
          <div className="splash" role="status"><span className="spinner big" /> Memeriksa sesi…</div>
        ) : !user ? (
          <AuthPage />
        ) : (
          <>
            {!photoUrl && (
              <section className="hero">
                <div className="hero-copy">
                  <p className="eyebrow">Halo, {user.name.split(" ")[0]} 👋</p>
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
                  {!loading && !result && error && file && (
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
                    <FrameCatalog items={recs} selected={style} onSelect={setStyle} />
                    {style && file && (
                      <TryOn
                        photoFile={file}
                        photoUrl={photoUrl}
                        style={style}
                        onStyle={setStyle}
                        recommended={recs.map((r) => r.style)}
                      />
                    )}
                  </>
                )}
              </div>
            )}
          </>
        )}
      </main>

      <footer className="site-footer">
        <p>FrameFit · Proyek Pemrograman Internet II · Politeknik Negeri Lampung</p>
        <p className="muted small">Hasil bersifat saran visual, bukan pengganti pemeriksaan optik.</p>
        {pwa.iosHint && (
          <p className="muted small">Di iPhone/iPad: ketuk tombol Bagikan lalu pilih “Tambah ke Layar Utama” untuk memasang aplikasi.</p>
        )}
      </footer>
    </>
  );
}
