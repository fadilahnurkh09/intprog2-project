// Backend membatasi foto maksimal 5 MB. Foto dari HP biasanya 3–10 MB, jadi
// kita kecilkan di browser (maks 1600 px, JPEG) sebelum diunggah — lebih cepat dan hemat kuota.
const MAX_SIDE = 1600;
const TARGET_BYTES = 1.5 * 1024 * 1024;

export async function prepareImage(file) {
  let bitmap;
  try {
    bitmap = await createImageBitmap(file); // otomatis memperbaiki orientasi EXIF
  } catch {
    return file; // biarkan backend yang memvalidasi
  }
  const { width, height } = bitmap;
  const scale = Math.min(1, MAX_SIDE / Math.max(width, height));
  if (scale === 1 && file.size <= TARGET_BYTES && file.type === "image/jpeg") {
    bitmap.close?.();
    return file;
  }
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(width * scale);
  canvas.height = Math.round(height * scale);
  canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close?.();
  const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.9));
  if (!blob) return file;
  const name = (file.name || "foto").replace(/\.\w+$/, "") + ".jpg";
  return new File([blob], name, { type: "image/jpeg" });
}
