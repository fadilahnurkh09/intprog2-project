# FrameFit — Frontend

React + Vite. Alur: unggah/ambil foto → `POST /predict` → bentuk wajah + confidence → rekomendasi frame → Virtual Try-On.

## Menjalankan
```bash
# 1. Backend (dari root proyek)
uvicorn app.main:app --reload          # http://localhost:8000

# 2. Frontend
cd frontend
npm install
npm run dev                            # http://localhost:5173
```
Alamat backend diatur di `.env` (`VITE_API_URL`, lihat `.env.example`).
Saat deploy, tambahkan domain frontend ke `allow_origins` di `app/main.py`.

## Struktur
- `src/api.js` — pemanggilan `/predict`
- `src/data/frames.js` — katalog frame (SVG) dan aturan rekomendasi per bentuk wajah
- `src/components/` — Uploader, CameraCapture, Result, FrameCatalog, TryOn
- `src/faceLandmarks.js` — deteksi posisi mata (MediaPipe Face Landmarker, berjalan di browser)

## Catatan
- Rekomendasi dan try-on dijalankan di browser, karena backend saat ini baru punya `/predict`.
  Jika nanti ada endpoint rekomendasi/try-on di backend, ganti `getRecommendations()` dan `TryOn.jsx`.
- Auto-align mata memerlukan internet (model MediaPipe dimuat dari CDN). Jika gagal, frame bisa diatur manual.
- Kamera butuh HTTPS atau `localhost`.
