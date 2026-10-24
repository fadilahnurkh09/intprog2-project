export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

// ---------------------------------------------------------------- token
const TOKEN_KEY = "framefit.token";

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}
export function setToken(token) {
  try {
    token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* penyimpanan diblokir — sesi hanya berlaku selama tab terbuka */
  }
}

// Dipanggil saat server menjawab 401 (token kedaluwarsa/tidak valid)
let onUnauthorized = () => {};
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

// ---------------------------------------------------------------- helper
function detailToText(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    // error validasi FastAPI/pydantic (422)
    return detail
      .map((d) => String(d.msg || "").replace(/^Value error, /, ""))
      .filter(Boolean)
      .join(" ") || fallback;
  }
  if (typeof detail === "object") return detail.message || fallback;
  return fallback;
}

async function request(path, { method = "GET", json, form, signal, auth = true, expect = "json" } = {}) {
  const headers = {};
  const token = getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;
  let body;
  if (json) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  } else if (form) {
    body = form;
  }

  let res;
  try {
    res = await fetch(`${API_URL}${path}`, { method, headers, body, signal });
  } catch (err) {
    if (err.name === "AbortError") throw err;
    throw new Error(
      `Tidak bisa terhubung ke server (${API_URL}). Pastikan backend sudah berjalan dan kamu sedang online.`
    );
  }

  if (!res.ok) {
    let data = null;
    try {
      data = await res.json();
    } catch {
      /* bukan JSON */
    }
    if (res.status === 401 && auth) onUnauthorized();
    throw new Error(detailToText(data?.detail, `Server mengembalikan error ${res.status}.`));
  }
  return expect === "blob" ? res.blob() : res.json();
}

// ---------------------------------------------------------------- auth
export const login = (email, password) =>
  request("/auth/login", { method: "POST", json: { email, password }, auth: false });

export const register = (name, email, password) =>
  request("/auth/register", { method: "POST", json: { name, email, password }, auth: false });

export const fetchMe = () => request("/auth/me");

// ---------------------------------------------------------------- fitur
/** POST /analyze → { face_shape, confidence, recommendations: [{id,name,style,description}] } */
export function analyzeFace(file, signal) {
  const form = new FormData();
  form.append("file", file, file.name || "foto.jpg");
  return request("/analyze", { method: "POST", form, signal });
}

/** POST /try-on → Blob PNG foto dengan kacamata terpasang */
export function virtualTryOn(file, glassesStyle, signal) {
  const form = new FormData();
  form.append("file", file, file.name || "foto.jpg");
  form.append("glasses_style", glassesStyle);
  return request("/try-on", { method: "POST", form, signal, expect: "blob" });
}
