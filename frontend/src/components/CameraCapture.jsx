import { useEffect, useRef, useState } from "react";

export default function CameraCapture({ onCapture, onClose }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!navigator.mediaDevices?.getUserMedia) {
        setError("Browser ini tidak mendukung akses kamera. Silakan unggah foto saja.");
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 960 } },
          audio: false,
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        const v = videoRef.current;
        if (v) {
          v.srcObject = stream;
          await v.play().catch(() => {});
        }
      } catch (e) {
        setError(
          e.name === "NotAllowedError"
            ? "Izin kamera ditolak. Aktifkan izin kamera di browser, lalu coba lagi."
            : "Kamera tidak ditemukan atau sedang dipakai aplikasi lain."
        );
      }
    })();
    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  function snap() {
    const v = videoRef.current;
    if (!v || !v.videoWidth) return;
    const c = document.createElement("canvas");
    c.width = v.videoWidth;
    c.height = v.videoHeight;
    const ctx = c.getContext("2d");
    // Cerminkan agar hasil sama dengan pratinjau (efek selfie)
    ctx.translate(c.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(v, 0, 0);
    c.toBlob(
      (blob) => blob && onCapture(new File([blob], "kamera.jpg", { type: "image/jpeg" })),
      "image/jpeg",
      0.92
    );
  }

  return (
    <div className="modal" role="dialog" aria-modal="true" aria-label="Ambil foto dengan kamera">
      <div className="modal-card">
        <div className="cam-frame">
          {error ? (
            <p className="cam-error">{error}</p>
          ) : (
            <>
              <video ref={videoRef} playsInline muted onLoadedData={() => setReady(true)} />
              <div className="cam-guide" aria-hidden="true" />
            </>
          )}
        </div>
        <p className="muted small">Posisikan wajah di dalam oval dan hadap lurus ke kamera.</p>
        <div className="btn-row">
          <button className="btn btn-primary" onClick={snap} disabled={!ready || !!error}>
            Ambil foto
          </button>
          <button className="btn btn-ghost" onClick={onClose}>Batal</button>
        </div>
      </div>
    </div>
  );
}
