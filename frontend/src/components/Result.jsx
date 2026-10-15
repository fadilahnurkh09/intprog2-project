import { FACE_SHAPES } from "../data/frames.js";

export default function Result({ photoUrl, result }) {
  const shape = FACE_SHAPES[result.face_shape] || { label: result.face_shape, desc: "", tip: "" };
  const pct = Math.round(result.confidence * 100);
  const level = pct >= 75 ? "tinggi" : pct >= 50 ? "sedang" : "rendah";

  return (
    <section className="card result" aria-labelledby="hasil-title">
      <img className="result-photo" src={photoUrl} alt="Fotomu yang dianalisis" />
      <div className="result-body">
        <p className="eyebrow">Bentuk wajahmu</p>
        <h2 id="hasil-title" className="shape-name">{shape.label}</h2>
        <p>{shape.desc}</p>

        <div className="meter" role="img" aria-label={`Tingkat keyakinan AI ${pct} persen`}>
          <div className="meter-head">
            <span>Keyakinan AI</span>
            <b>{pct}%</b>
          </div>
          <div className="meter-track"><div className="meter-fill" style={{ width: `${pct}%` }} /></div>
          {level === "rendah" && (
            <p className="note">
              Keyakinan rendah — coba foto lain dengan wajah menghadap lurus dan cahaya yang lebih merata.
            </p>
          )}
        </div>

        <p className="tip"><b>Tips:</b> {shape.tip}</p>
      </div>
    </section>
  );
}
