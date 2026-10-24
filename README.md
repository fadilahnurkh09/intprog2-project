# intprog2-project

Sistem Rekomendasi Kacamata dan Virtual Try-On Berbasis Analisis Bentuk Wajah

Proyek ini merupakan aplikasi berbasis Artificial Intelligence (AI) dan Computer Vision yang dikembangkan untuk membantu pengguna dalam memilih kacamata yang sesuai dengan bentuk wajah mereka.

Pengguna cukup mengunggah foto wajah, kemudian sistem akan melakukan analisis untuk mengenali bentuk wajah dan memberikan beberapa rekomendasi jenis kacamata yang sesuai. Setelah memilih kacamata yang diinginkan, pengguna juga dapat mencoba tampilan kacamata tersebut secara virtual melalui fitur Virtual Try-On.

Dengan adanya sistem ini, pengguna dapat memperoleh gambaran mengenai kacamata yang cocok tanpa harus mencoba berbagai frame secara langsung.

Konsep Utama

Upload Foto → Analisis Bentuk Wajah → Rekomendasi Kacamata → Virtual Try-On

## Menjalankan

```bash
# Backend (dari root proyek) — disarankan Python 3.12
python -m venv venv312
venv312\Scripts\activate            # Windows  (Linux/macOS: source venv312/bin/activate)
pip install -r requirements.txt
python -m uvicorn app.main:app --reload     # http://localhost:8000  (dokumentasi: /docs)

# Frontend
cd frontend && npm install && npm run dev   # http://localhost:5173
```

## Endpoint API

| Method | Path | Login | Keterangan |
|---|---|---|---|
| POST | `/auth/register` | - | Daftar (`name`, `email`, `password` min. 8 karakter); langsung mengembalikan token |
| POST | `/auth/login` | - | Masuk (`email`, `password`) -> `access_token` |
| GET | `/auth/me` | ya | Data user yang sedang masuk |
| POST | `/predict` | ya | Foto -> bentuk wajah + confidence |
| POST | `/analyze` | ya | Foto -> bentuk wajah + rekomendasi frame |
| POST | `/recommendations` | ya | `face_shape` -> rekomendasi frame |
| POST | `/try-on` | ya | Foto + `glasses_style` -> gambar PNG hasil try-on |
| GET | `/assets/...` | - | Gambar kacamata (thumbnail katalog) |

Endpoint bertanda "ya" memakai header `Authorization: Bearer <token>`. Di `/docs`, klik **Authorize** lalu isi email di kolom *username*.

## Konfigurasi (environment variable, opsional)

| Variabel | Fungsi |
|---|---|
| `FRAMEFIT_SECRET_KEY` | Kunci penandatangan token. Jika kosong dibuat otomatis di `data/.secret_key`. **Wajib diisi di produksi.** |
| `FRAMEFIT_CORS_ORIGINS` | Domain frontend tambahan, dipisah koma |
| `FRAMEFIT_TOKEN_TTL_HOURS` | Masa berlaku token (default 24) |
| `FRAMEFIT_DB_PATH` | Lokasi database SQLite (default `data/framefit.db`) |

Data akun disimpan di SQLite (`data/framefit.db`, tidak ikut git); kata sandi di-hash dengan PBKDF2-SHA256 + salt.

