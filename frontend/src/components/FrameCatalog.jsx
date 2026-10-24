import { FRAMES, styleInfo } from "../data/frames.js";
import { FrameThumb } from "./TryOn.jsx";

export default function FrameCatalog({ items, selected, onSelect }) {
  if (!items.length) {
    return (
      <section>
        <div className="section-head"><h2>Rekomendasi frame untukmu</h2></div>
        <p className="muted">Belum ada rekomendasi untuk bentuk wajah ini.</p>
      </section>
    );
  }
  return (
    <section aria-labelledby="rekom-title">
      <div className="section-head">
        <h2 id="rekom-title">Rekomendasi frame untukmu</h2>
        <p className="muted">Pilih salah satu untuk mencobanya langsung di fotomu.</p>
      </div>
      <div className="catalog">
        {items.map((f, i) => (
          <button
            key={f.id}
            className={`frame-card ${selected === f.style ? "is-selected" : ""}`}
            onClick={() => onSelect(f.style)}
            aria-pressed={selected === f.style}
          >
            {i === 0 && <span className="badge">Paling cocok</span>}
            <FrameThumb style={f.style} />
            <h3>{f.name}</h3>
            <span className="kind">{FRAMES[styleInfo(f.style).svg]?.kind}</span>
            <p>{f.description}</p>
          </button>
        ))}
      </div>
    </section>
  );
}
