// Deteksi posisi pupil (iris) dengan MediaPipe Face Landmarker, dijalankan di browser.
// Dimuat lazy supaya bundle awal tetap kecil. Jika gagal (offline / diblokir),
// pemanggil akan otomatis jatuh ke mode penempatan manual.

const WASM_URL = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";
const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";

let landmarkerPromise = null;

function getLandmarker() {
  if (!landmarkerPromise) {
    landmarkerPromise = (async () => {
      const { FaceLandmarker, FilesetResolver } = await import("@mediapipe/tasks-vision");
      const fileset = await FilesetResolver.forVisionTasks(WASM_URL);
      return FaceLandmarker.createFromOptions(fileset, {
        baseOptions: { modelAssetPath: MODEL_URL },
        runningMode: "IMAGE",
        numFaces: 1,
      });
    })().catch((e) => {
      landmarkerPromise = null; // izinkan coba lagi
      throw e;
    });
  }
  return landmarkerPromise;
}

/** @returns {{left:{x,y}, right:{x,y}} | null} koordinat ternormalisasi (0..1) */
export async function detectEyes(imageEl) {
  const lm = await getLandmarker();
  const res = lm.detect(imageEl);
  const pts = res.faceLandmarks?.[0];
  if (!pts || pts.length < 478) return null;
  // 468 & 473 = pusat iris kedua mata
  const a = pts[468];
  const b = pts[473];
  const [left, right] = a.x <= b.x ? [a, b] : [b, a];
  return { left: { x: left.x, y: left.y }, right: { x: right.x, y: right.y } };
}
