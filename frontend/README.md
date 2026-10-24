# FrameFit — Frontend (PWA)

React + Vite. Alur: **masuk/daftar → unggah/ambil foto → `/analyze` → rekomendasi frame → `/try-on`**.

## Menjalankan (pengembangan)
```bash
# 1. Backend — dari root proyek (lihat README utama)
python -m uvicorn app.main:app --reload          # http://localhost:8000

# 2. Frontend
cd frontend
npm install
cp .env.example .env                             # Windows: copy .env.example .env
npm run dev                                      # http://localhost:5173
```
Alamat backend diatur di `frontend/.env` → `VITE_API_URL`.

## Fitur
- **Login / daftar** — token JWT disimpan di browser; semua endpoint analisis butuh login. Sesi dipulihkan saat halaman dibuka lagi, dan otomatis keluar bila token kedaluwarsa.
- **Analisis & rekomendasi** — memakai `POST /analyze` (rekomendasi datang dari backend).
- **Virtual Try-On** — hasil dari `POST /try-on` (MediaPipe + Pillow di server). Model tanpa aset di server (saat ini *Oval*) dan tombol **Atur manual** memakai try-on di browser (geser/ukuran/kemiringan/warna).
- Foto besar dikecilkan otomatis di browser (maks 1600 px) sebelum diunggah, karena batas server 5 MB.

## PWA
Aplikasi bisa **dipasang** (Chrome/Edge/Android: tombol *Pasang aplikasi*; iPhone: Bagikan → Tambah ke Layar Utama) dan memuat cepat dari cache.
```bash
npm run build && npm run preview     # uji PWA di http://localhost:4173 (service worker hanya aktif pada build)
```
- Yang di-cache: tampilan aplikasi (HTML/JS/CSS/ikon), font, dan model MediaPipe untuk mode manual.
- Yang **tidak** di-cache: login, analisis, try-on — butuh koneksi ke backend. Saat offline muncul banner.
- Pasang/kamera butuh **HTTPS** (atau `localhost`). Jika frontend di-HTTPS-kan, `VITE_API_URL` juga harus HTTPS.

## Deploy
1. Deploy backend (butuh Python + TensorFlow, jadi pakai VPS/Render/Railway/Hugging Face Spaces, bukan hosting statis). Set env `FRAMEFIT_SECRET_KEY` dan `FRAMEFIT_CORS_ORIGINS=https://domain-frontend-kamu`.
2. Build frontend dengan `VITE_API_URL=https://domain-backend-kamu npm run build`, lalu upload folder `dist/` ke hosting statis (Netlify, Vercel, GitHub Pages, Cloudflare Pages).
3. Pengguna cukup membuka URL dan memasang PWA — tidak perlu menjalankan backend atau mengunduh repo.

## Struktur
- `src/api.js` — klien API (token, `/auth/*`, `/analyze`, `/try-on`)
- `src/auth.jsx` — konteks login (AuthProvider)
- `src/pwa.js` — hook tombol pasang & status online
- `src/imageUtil.js` — pengecilan foto sebelum unggah
- `src/data/frames.js` — teks bentuk wajah, katalog SVG, pemetaan `style` backend → frame
- `src/components/` — AuthPage, Uploader, CameraCapture, Result, FrameCatalog, TryOn (server), ManualTryOn (browser)
- `vite.config.js` — konfigurasi PWA (manifest, service worker)
