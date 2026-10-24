import { useRef, useState } from "react";
import CameraCapture from "./CameraCapture.jsx";

const MAX_MB = 25; // foto besar dikecilkan otomatis sebelum diunggah (batas server 5 MB)

export default function Uploader({ onPick, busy }) {
  const inputRef = useRef(null);
  const [drag, setDrag] = useState(false);
  const [cameraOpen, setCameraOpen] = useState(false);
  const [localError, setLocalError] = useState("");

  function handleFile(file) {
    setLocalError("");
    if (!file) return;
    if (!/^image\/(jpe?g|png|webp)$/i.test(file.type)) {
      setLocalError("Format belum didukung. Gunakan foto JPG, PNG, atau WebP.");
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      setLocalError(`Ukuran foto maksimal ${MAX_MB} MB.`);
      return;
    }
    onPick(file);
  }

  return (
    <div className="uploader">
      <div
        className={`dropzone ${drag ? "is-drag" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          handleFile(e.dataTransfer.files?.[0]);
        }}
      >
        <div className="dz-icon" aria-hidden="true">
          <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="9.5" r="4.5" />
            <path d="M4 21c.8-4 4-6 8-6s7.2 2 8 6" />
          </svg>
        </div>
        <h3>Unggah foto wajahmu</h3>
        <p>Seret foto ke sini, atau pilih dari perangkat.</p>
        <div className="btn-row">
          <button className="btn btn-primary" disabled={busy} onClick={() => inputRef.current?.click()}>
            Pilih foto
          </button>
          <button className="btn btn-ghost" disabled={busy} onClick={() => setCameraOpen(true)}>
            Gunakan kamera
          </button>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          hidden
          onChange={(e) => {
            handleFile(e.target.files?.[0]);
            e.target.value = "";
          }}
        />
      </div>
      {localError && <p className="error" role="alert">{localError}</p>}

      <ul className="tips">
        <li><b>Hadap lurus</b> ke kamera, rambut disisir ke belakang.</li>
        <li><b>Cahaya cukup</b>, tidak terlalu gelap atau menyilaukan.</li>
        <li><b>Tanpa kacamata</b>, masker, atau penutup wajah lain.</li>
      </ul>

      {cameraOpen && (
        <CameraCapture
          onClose={() => setCameraOpen(false)}
          onCapture={(file) => {
            setCameraOpen(false);
            handleFile(file);
          }}
        />
      )}
    </div>
  );
}
