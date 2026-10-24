# FrameFit — dua jalur training AI, dari nol eksperimen

Folder ini **tambahan** untuk proyek tim; source code frontend/backend asli tidak diubah.
Kedua model dimulai dari eksperimen/pelatihan baru, menggunakan **ImageNet-pretrained MobileNetV2** (bukan random initialization). Ini adalah *transfer learning*, bukan training seluruh backbone from scratch.

## Yang sudah ditemukan pada proyek tim

- Ada `models/faceshape_mobilenetv2.keras`, tetapi **tidak ada** notebook/pipeline training, confusion matrix, atau laporan pengujian dalam ZIP GitHub.
- `app/routes/predict.py` menjalankan deteksi wajah, lalu **resize seluruh foto**, bukan crop area wajah. Model inference nanti harus diperbarui agar **identik** dengan preprocessing training baru.
- `frontend/src/components/TryOn.jsx` membuat try-on memakai canvas dan SVG frame hasil kode frontend. `app/routes/try_on.py` juga menyediakan try-on backend dengan PNG. Keduanya belum menggunakan model segmentasi yang akan dilatih di sini.
- `models/face_landmarker.task` adalah model landmark siap pakai, bukan model kedua hasil training.

## 1. Siapkan virtual environment

Jalankan perintah di **root repo** (`app/`, `frontend/`, `models/` terletak di sana):

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r training/requirements.txt
```

Gunakan Python yang didukung TensorFlow pada OS masing-masing. Jika komputer tidak punya GPU, training tetap mungkin pada CPU tetapi sangat lambat. GPU Colab/Kaggle Notebook dianjurkan.

## 2. Dataset 1: bentuk wajah (klasifikasi 5 kelas)

Sumber usulan: https://www.kaggle.com/datasets/niten19/face-shape-dataset

Taruh dataset Kaggle yang sudah diekstrak di `datasets/raw/faces/`. Program mencari struktur `train` dan `test` (atau `training`, `testing`) dengan subfolder kelas, atau 5 subfolder kelas langsung.

Kelas **harus benar-benar ada**, bukan diubah dengan asumsi: `Heart`, `Oblong`, `Oval`, `Round`, `Square`. Jika dataset memakai label **Diamond**, itu BUKAN sinonim `Oblong`! Verifikasi label dataset sebelum training dan tentukan sumber label Oblong yang sah.

```bash
python -m training.prepare_faces --source datasets/raw/faces \
  --landmarker models/face_landmarker.task --mode strict
```

Mode `strict` **hanya crop 224×224 dari piksel asli**. Jika kontur wajah + padding tidak bisa dimuat di crop, sampel ditolak; cek `datasets/processed/faces/rejected.csv`. Mengecilkan **seluruh foto** dilarang.

Jika banyak wajah asli lebih besar dari 224 px, mode strict akan menolak banyak gambar. Untuk ML yang valid, gunakan **crop wajah dulu lalu resize hanya kotak wajah** (tidak resize foto seluruhnya):

```bash
python -m training.prepare_faces --source datasets/raw/faces \
  --landmarker models/face_landmarker.task --mode crop-then-resize
```

Lakukan inspeksi manual pada minimal 20 contoh **setiap kelas** dari train/val/test, khususnya dahi, pipi, rahang, dan rambut. Mode yang dipilih **wajib dipakai sama** ketika aplikasi melakukan prediksi.

Jika dataset menyediakan training/testing asli, testing asli dipertahankan, dan original training dibagi lagi train/validation (kira-kira 70/10/20 total). Bila tidak tersedia, dibagi per kelas 70/15/15. **Kelompokkan foto orang yang sama ke split yang sama** jika identitas/subjek tersedia; skrip ini hanya menghapus duplikat yang persis identik dan belum mencegah foto berbeda dari orang sama lintas split.

## 3. Training transfer learning dan fine-tuning wajah

```bash
python -m training.train_faces --data datasets/processed/faces \
  --head-epochs 20 --fine-epochs 20 --batch 32 --unfreeze-last 35
```

Parameter standar awal (bukan jaminan): `224×224×3`, batch 32, Adam 1e-3 untuk head, 1e-5 untuk fine-tuning, Categorical Crossentropy, 5 kelas Softmax. Head MobileNetV2 dibekukan dahulu; saat fine-tuning 35 layer akhir di-unfreeze (BatchNorm tetap frozen). EarlyStopping pada validation loss, ModelCheckpoint dan ReduceLROnPlateau aktif.

Keluaran `models/training_results/faces/`:

- `head_best.keras`, `fine_best.keras`, `faceshape_mobilenetv2_best.keras`
- `head_history.csv`, `fine_history.csv`, `training_history.png`
- `validation_comparison.json`, `class_names.json`
- `face_test_metrics.json` (accuracy, macro precision, recall, F1, loss, per kelas)
- `face_confusion_matrix.png`, `face_per_class_metrics.csv`, `face_test_predictions.csv`

Model terpilih menggunakan **validation loss**. Testing hanya dilakukan **sekali pada model terpilih**, setelah training selesai. Target *test accuracy* **>85%**, bukan sekadar train accuracy. Bila target gagal, jangan tuliskan angka seolah-olah lulus.

## 4. Dataset 2: segmentasi bingkai kacamata

Sumber usulan: https://www.kaggle.com/datasets/mantasu/glasses-segmentation-synthetic-dataset

Dataset ini memuat wajah orang berkacamata dan **mask**, termasuk kategori frames/shadows. Latih pada **mask bingkai kacamata (frames)**, bukan mask shadow atau label bentuk wajah. Struktur dataset asli mungkin berbeda; **susun dahulu pasangan** gambar dan mask yang sesuai sebagai:

```
datasets/raw/glasses/images/photo001.png
datasets/raw/glasses/images/photo002.png
datasets/raw/glasses/masks/photo001.png
datasets/raw/glasses/masks/photo002.png
```

Mask disimpan grayscale: 0 = latar belakang, 255 = bagian frame. Foto dan mask harus memiliki resolusi dan orientasi yang **sama**. Bila nama mask berbeda, gunakan `--mask-suffix _frames` misalnya.

```bash
python -m training.prepare_glasses \
  --images datasets/raw/glasses/images \
  --masks datasets/raw/glasses/masks
```

Program membuat **crop yang sama persis** pada foto dan mask: potongan tengah 224×224 tanpa mengecilkan gambar penuh. Periksa setiap pasangan secara visual; label mask yang bergeser adalah cacat dataset. Jika crop tengah memotong ujung kacamata, ubah kebijakan crop setelah inspeksi visual (gunakan ROI terarah yang diterapkan identik ke image/mask).

```bash
python -m training.train_glasses --data datasets/processed/glasses \
  --head-epochs 25 --fine-epochs 20 --batch 16 --unfreeze-last 35
```

Arsitektur: MobileNetV2 encoder pretrained + decoder mirip U-Net, keluaran sigmoid mask satu channel. Loss gabungan BCE + Dice. Model dipilih pada validation loss, baru dievaluasi pada test.

Keluaran `models/training_results/glasses/`:

- `glasses_segmentation_best.keras`, `head_best.keras`, `fine_best.keras`
- `head_history.csv`, `fine_history.csv`, `validation_comparison.json`
- `glasses_test_metrics.json` (test loss, foreground IoU, Dice, precision, recall, pixel F1, pixel accuracy)
- `glasses_per_image_metrics.csv` diurutkan dari IoU terburuk
- `segmentation_examples/*.png` untuk membandingkan gambar/label/prediksi

**Jangan memakai pixel accuracy >85% sebagai standar keberhasilan segmentasi**. Bila >90% piksel berlatar belakang, model yang memprediksi semua piksel sebagai latar belakang bisa mendapat accuracy tinggi namun gagal mendeteksi kacamata. Gunakan **foreground IoU, Dice/F1**, plus inspeksi contoh gagal.

## 5. Alur Virtual Try-On setelah training

1. Foto pengguna → deteksi landmark MediaPipe → **crop wajah (aturan sama persis dengan training)** → MobileNetV2 wajah → 5 probabilitas kelas.
2. Label wajah → aturan rekomendasi model frame.
3. Foto/model frame dan mask hasil model kedua → pemisahan aset bingkai dari sumber yang sesuai. **Mask gambar orang berkacamata bukan PNG produk transparan dengan sendirinya.** Aset katalog bersih tetap perlu disiapkan atau dikurasi.
4. MediaPipe Face Landmarker (model pretrained tersendiri) → mata & hidung → skala, posisi, sudut kacamata.
5. Overlay transparansi dari PNG frame ke foto wajah, cek presisi manual di beberapa wajah, baru tawarkan unduh lokal.

Proyek lama punya **dua engine try-on** (browser dan backend). Pilih satu yang menjadi sumber kebenaran saat integrasi nanti agar penggunaan kacamata, warna dan posisi konsisten.

## 6. Aturan mutu dan anti-kebocoran

- Audit label dan distribusi kelas **sebelum** training. Khusus lima bentuk wajah, periksa bahwa kelas Oblong sungguh tersedia.
- Split berdasarkan identitas jika ada beberapa foto subjek yang sama; hindari kebocoran train → test.
- Duplikat identik dibuang, tetapi **near-duplicate dan gambar orang yang sama masih memerlukan audit tambahan**.
- Augmentasi hanya untuk training, tidak pada validation/testing. Mask gambar dan mask harus diubah serempak.
- Gunakan crop + normalization yang identik di train dan inference. Normalisasi MobileNetV2 adalah **[-1, 1]**, sudah dimasukkan ke model terlatih.
- Hindari tuning berdasarkan test accuracy. Perbaikan hiperparameter hanya berdasarkan training dan validation.
- Laporan wajib memuat konfigurasi, pembagian data, tabel per kelas, confusion matrix, kurva loss/accuracy, foto kegagalan, hasil sebelum/sesudah fine-tuning.
- Audit lisensi dataset dan izin pemrosesan foto wajah sebelum menyebarluaskan dataset, model, atau hasilnya.

## Status pelaksanaan

**Kode fondasi tersedia, tetapi model baru BELUM dilatih**: kedua dataset mentah tidak terdapat pada ZIP proyek, dan lingkungan pembuatan paket tidak memiliki TensorFlow terpasang. Skrip telah diperiksa secara sintaks, bukan diuji training end-to-end. **Tidak ada klaim hasil akurasi 85%** sampai evaluation testing benar-benar dijalankan.

## 7. Contoh inference setelah model jadi

```bash
python -m training.infer_face --image contoh_foto.jpg --mode strict
python -m training.infer_glasses --image foto_berkacamata.png --output contoh_cutout.png
python -m unittest discover -s training/tests -v
```

