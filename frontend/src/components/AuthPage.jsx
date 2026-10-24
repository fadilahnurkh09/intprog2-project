import { useState } from "react";
import { useAuth } from "../auth.jsx";

export default function AuthPage() {
  const { login, register, notice } = useAuth();
  const [mode, setMode] = useState("login"); // login | register
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [showPw, setShowPw] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const isRegister = mode === "register";
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (isRegister && form.password.length < 8) {
      setError("Kata sandi minimal 8 karakter.");
      return;
    }
    setBusy(true);
    try {
      if (isRegister) await register(form.name.trim(), form.email.trim(), form.password);
      else await login(form.email.trim(), form.password);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <section className="hero auth-hero">
      <div className="hero-copy">
        <p className="eyebrow">Rekomendasi kacamata berbasis AI</p>
        <h1>Temukan kacamata yang <em>pas</em> untuk bentuk wajahmu.</h1>
        <p className="lead">
          Masuk untuk menganalisis bentuk wajah, melihat rekomendasi frame, dan mencobanya langsung sebelum membeli.
        </p>
      </div>

      <div className="card auth-card">
        <div className="auth-tabs" role="tablist">
          <button role="tab" aria-selected={!isRegister} className={!isRegister ? "on" : ""} onClick={() => { setMode("login"); setError(""); }}>
            Masuk
          </button>
          <button role="tab" aria-selected={isRegister} className={isRegister ? "on" : ""} onClick={() => { setMode("register"); setError(""); }}>
            Daftar
          </button>
        </div>

        <form onSubmit={submit} noValidate={false}>
          {notice && !error && <p className="notice" role="status">{notice}</p>}

          {isRegister && (
            <label className="field">
              <span>Nama</span>
              <input value={form.name} onChange={set("name")} required minLength={2} maxLength={60} autoComplete="name" />
            </label>
          )}
          <label className="field">
            <span>Email</span>
            <input type="email" value={form.email} onChange={set("email")} required autoComplete="email" inputMode="email" />
          </label>
          <label className="field">
            <span>Kata sandi</span>
            <div className="pw">
              <input
                type={showPw ? "text" : "password"}
                value={form.password}
                onChange={set("password")}
                required
                minLength={isRegister ? 8 : undefined}
                autoComplete={isRegister ? "new-password" : "current-password"}
              />
              <button type="button" className="pw-toggle" onClick={() => setShowPw((v) => !v)} aria-pressed={showPw}>
                {showPw ? "Sembunyikan" : "Tampilkan"}
              </button>
            </div>
            {isRegister && <small className="muted">Minimal 8 karakter.</small>}
          </label>

          {error && <p className="error" role="alert">{error}</p>}

          <button className="btn btn-primary btn-block" disabled={busy}>
            {busy ? "Memproses…" : isRegister ? "Buat akun" : "Masuk"}
          </button>
        </form>

        <p className="muted small auth-switch">
          {isRegister ? "Sudah punya akun?" : "Belum punya akun?"}{" "}
          <button className="link" onClick={() => { setMode(isRegister ? "login" : "register"); setError(""); }}>
            {isRegister ? "Masuk" : "Daftar"}
          </button>
        </p>
      </div>
    </section>
  );
}
