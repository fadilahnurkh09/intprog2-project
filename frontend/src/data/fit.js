// Aturan pemasangan kacamata — HARUS SAMA dengan konstanta di backend (app/routes/try_on.py)
// supaya hasil mode "Otomatis" (server) dan "Atur manual" (browser) identik.
//
//  FIT_WIDTH_RATIO     : lebar bingkai = jarak sudut luar kedua mata × nilai ini
//  FIT_VERTICAL_ANCHOR : posisi garis mata di dalam tinggi bingkai (0 = tepi atas, 0.5 = tengah)
export const FIT_WIDTH_RATIO = 1.6;
export const FIT_VERTICAL_ANCHOR = 0.5;
