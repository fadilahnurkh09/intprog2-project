export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

/**
 * Kirim foto ke backend FastAPI (POST /predict, multipart/form-data).
 * Respons: { success, face_shape, confidence }
 */
export async function predictFaceShape(file, signal) {
  const body = new FormData();
  body.append("file", file, file.name || "foto.jpg");

  let res;
  try {
    res = await fetch(`${API_URL}/predict`, { method: "POST", body, signal });
  } catch (err) {
    if (err.name === "AbortError") throw err;
    throw new Error(
      `Tidak bisa terhubung ke server (${API_URL}). Pastikan backend sudah berjalan dan CORS aktif.`
    );
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    /* respons bukan JSON */
  }

  if (!res.ok) {
    throw new Error(data?.detail || `Server mengembalikan error ${res.status}.`);
  }
  if (!data?.face_shape) throw new Error("Respons server tidak sesuai format yang diharapkan.");
  return data;
}
