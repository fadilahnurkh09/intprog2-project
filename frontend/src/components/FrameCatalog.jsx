import { frameDataUrl } from "../data/frames.js";

export default function FrameCatalog({ items, selectedId, onSelect, color }) {
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
            className={`frame-card ${selectedId === f.id ? "is-selected" : ""}`}
            onClick={() => onSelect(f.id)}
            aria-pressed={selectedId === f.id}
          >
            {i === 0 && <span className="badge">Paling cocok</span>}
            <img src={frameDataUrl(f.id, color)} alt="" />
            <h3>{f.name}</h3>
            <span className="kind">{f.kind}</span>
            <p>{f.reason}</p>
          </button>
        ))}
      </div>
    </section>
  );
}
