// Katalog frame + aturan rekomendasi (rule-based) per bentuk wajah.
// Semua frame digambar sebagai SVG (viewBox 300x100). Pusat lensa kiri/kanan
// ada di x=75 dan x=225 (jarak 150 unit) agar mudah disejajarkan dengan mata.

export const FACE_SHAPES = {
  Oval: {
    label: "Oval",
    desc: "Wajah seimbang dengan dahi sedikit lebih lebar dari dagu dan rahang melengkung lembut.",
    tip: "Bentuk wajah paling fleksibel — hampir semua frame cocok. Pilih sesuai gaya, asal lebar frame tidak melebihi lebar wajah.",
  },
  Round: {
    label: "Bulat",
    desc: "Lebar dan panjang wajah hampir sama, dengan pipi penuh dan garis rahang lembut.",
    tip: "Frame bersudut dan agak lebar menambah kesan tegas serta membuat wajah tampak lebih ramping.",
  },
  Square: {
    label: "Persegi",
    desc: "Dahi, pipi, dan rahang hampir selebar sama dengan rahang yang tegas.",
    tip: "Frame melengkung melembutkan sudut rahang. Hindari frame kotak tebal yang menambah kesan kaku.",
  },
  Heart: {
    label: "Hati",
    desc: "Dahi lebar yang menyempit ke dagu yang lebih runcing.",
    tip: "Frame yang lebih ringan di bagian atas dan melebar di bawah menyeimbangkan dahi dan dagu.",
  },
  Oblong: {
    label: "Lonjong",
    desc: "Wajah lebih panjang daripada lebar, dengan pipi lurus dan dahi tinggi.",
    tip: "Frame tinggi dan besar memperpendek proporsi wajah; detail di sisi (temple) menambah kesan lebar.",
  },
};

// Aturan kecocokan: bentuk wajah -> daftar frame (urut prioritas) + alasan
export const RECOMMENDATIONS = {
  Oval: [
    ["wayfarer", "Garis tegas Wayfarer menambah karakter tanpa mengganggu proporsi seimbang wajahmu."],
    ["aviator", "Bentuk tetesan Aviator menyatu dengan lengkung alami wajah oval."],
    ["browline", "Browline menonjolkan alis dan memberi kesan rapi serta klasik."],
    ["geometric", "Wajah oval cukup seimbang untuk tampil berani dengan frame heksagonal."],
    ["round", "Frame bulat menjaga kesan lembut dan harmonis di wajah oval."],
  ],
  Round: [
    ["rectangle", "Garis persegi panjang menambah kesan tegas dan membuat wajah tampak lebih ramping."],
    ["wayfarer", "Sudut Wayfarer memberi kontras terhadap lengkung pipi yang penuh."],
    ["cateye", "Ujung atas yang terangkat memberi efek mengangkat dan menirus pada wajah."],
    ["geometric", "Sudut heksagonal menciptakan struktur pada wajah yang lembut."],
  ],
  Square: [
    ["round", "Lensa bulat melembutkan garis rahang yang tegas."],
    ["oval", "Lengkung oval menyeimbangkan sudut wajah tanpa terlihat kaku."],
    ["aviator", "Bentuk tetesan menambah lengkung di antara garis rahang yang kuat."],
    ["cateye", "Sapuan ke atas menambah dimensi dan melembutkan wajah."],
  ],
  Heart: [
    ["oval", "Frame oval menyeimbangkan dahi lebar dengan dagu yang lebih kecil."],
    ["aviator", "Bagian bawah yang lebih lebar menyeimbangkan dagu yang runcing."],
    ["round", "Lensa bulat tipis tidak menambah beban pada dahi."],
    ["rectangle", "Frame ramping memberi garis bersih tanpa memperlebar dahi."],
  ],
  Oblong: [
    ["wayfarer", "Frame tinggi dan tebal membantu memperpendek proporsi wajah."],
    ["round", "Lensa bulat besar menambah kesan lebar dan menyeimbangkan panjang wajah."],
    ["geometric", "Frame lebar dengan sudut membuat wajah tampak lebih proporsional."],
    ["cateye", "Aksen di sisi frame menambah lebar visual wajah."],
  ],
};

// Warna frame yang bisa dipilih di Virtual Try-On
export const COLORS = [
  { id: "black", name: "Hitam", value: "#1a1714" },
  { id: "tortoise", name: "Tortoise", value: "#7a4a22" },
  { id: "gold", name: "Emas", value: "#c8993e" },
  { id: "silver", name: "Perak", value: "#9aa3ad" },
  { id: "navy", name: "Navy", value: "#1f3552" },
  { id: "rose", name: "Rose", value: "#b0586b" },
];

// Setiap frame: nama, kategori, dan fungsi yang menghasilkan isi SVG (lensa + rangka).
// Lensa dibuat transparan agar foto wajah tetap terlihat.
const lensAttrs = (c, w) =>
  `fill="rgba(150,190,210,0.16)" stroke="${c}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;
const arms = (c) =>
  `<path d="M3 36 L-14 30 M297 36 L314 30" stroke="${c}" stroke-width="6" stroke-linecap="round" fill="none"/>`;

export const FRAMES = {
  wayfarer: {
    name: "Wayfarer",
    kind: "Eyeglasses / Sunglasses",
    svg: (c) => `
      <path d="M12 26 Q75 18 138 26 L134 62 Q130 80 100 80 L50 80 Q22 80 18 60 Z" ${lensAttrs(c, 9)}/>
      <path d="M162 26 Q225 18 288 26 L282 60 Q278 80 250 80 L200 80 Q170 80 166 62 Z" ${lensAttrs(c, 9)}/>
      <path d="M138 34 Q150 28 162 34" stroke="${c}" stroke-width="7" fill="none" stroke-linecap="round"/>${arms(c)}`,
  },
  round: {
    name: "Round",
    kind: "Eyeglasses",
    svg: (c) => `
      <circle cx="75" cy="50" r="40" ${lensAttrs(c, 5)}/>
      <circle cx="225" cy="50" r="40" ${lensAttrs(c, 5)}/>
      <path d="M115 46 Q150 30 185 46" stroke="${c}" stroke-width="5" fill="none" stroke-linecap="round"/>
      <path d="M35 44 L14 38 M265 44 L286 38" stroke="${c}" stroke-width="5" stroke-linecap="round"/>`,
  },
  rectangle: {
    name: "Rectangle",
    kind: "Eyeglasses",
    svg: (c) => `
      <rect x="10" y="30" width="130" height="52" rx="10" ${lensAttrs(c, 6)}/>
      <rect x="160" y="30" width="130" height="52" rx="10" ${lensAttrs(c, 6)}/>
      <path d="M140 42 Q150 36 160 42" stroke="${c}" stroke-width="6" fill="none" stroke-linecap="round"/>
      <path d="M10 40 L-8 34 M290 40 L308 34" stroke="${c}" stroke-width="6" stroke-linecap="round"/>`,
  },
  cateye: {
    name: "Cat-Eye",
    kind: "Eyeglasses / Sunglasses",
    svg: (c) => `
      <path d="M8 24 Q40 36 90 30 Q142 34 140 60 Q136 84 94 84 Q50 84 30 66 Q14 48 8 24 Z" ${lensAttrs(c, 7)}/>
      <path d="M292 24 Q260 36 210 30 Q158 34 160 60 Q164 84 206 84 Q250 84 270 66 Q286 48 292 24 Z" ${lensAttrs(c, 7)}/>
      <path d="M140 44 Q150 38 160 44" stroke="${c}" stroke-width="6" fill="none" stroke-linecap="round"/>
      <path d="M8 24 L-10 18 M292 24 L310 18" stroke="${c}" stroke-width="6" stroke-linecap="round"/>`,
  },
  aviator: {
    name: "Aviator",
    kind: "Sunglasses",
    svg: (c) => `
      <path d="M14 28 Q75 20 136 28 Q142 64 118 80 Q92 92 56 80 Q18 64 14 28 Z" ${lensAttrs(c, 4)}/>
      <path d="M164 28 Q225 20 286 28 Q282 64 244 80 Q208 92 182 80 Q158 64 164 28 Z" ${lensAttrs(c, 4)}/>
      <path d="M136 30 Q150 20 164 30 M146 38 Q150 34 154 38" stroke="${c}" stroke-width="4" fill="none" stroke-linecap="round"/>
      <path d="M14 30 L-6 28 M286 30 L306 28" stroke="${c}" stroke-width="4" stroke-linecap="round"/>`,
  },
  oval: {
    name: "Oval",
    kind: "Eyeglasses",
    svg: (c) => `
      <ellipse cx="75" cy="52" rx="58" ry="36" ${lensAttrs(c, 5)}/>
      <ellipse cx="225" cy="52" rx="58" ry="36" ${lensAttrs(c, 5)}/>
      <path d="M133 46 Q150 36 167 46" stroke="${c}" stroke-width="5" fill="none" stroke-linecap="round"/>
      <path d="M18 44 L0 38 M282 44 L300 38" stroke="${c}" stroke-width="5" stroke-linecap="round"/>`,
  },
  browline: {
    name: "Browline",
    kind: "Eyeglasses",
    svg: (c) => `
      <path d="M10 28 Q75 16 140 28 L140 34 L10 34 Z" fill="${c}" stroke="${c}" stroke-width="4" stroke-linejoin="round"/>
      <path d="M160 28 Q225 16 290 28 L290 34 L160 34 Z" fill="${c}" stroke="${c}" stroke-width="4" stroke-linejoin="round"/>
      <path d="M14 34 Q14 80 75 80 Q136 80 136 34" ${lensAttrs(c, 3)}/>
      <path d="M164 34 Q164 80 225 80 Q286 80 286 34" ${lensAttrs(c, 3)}/>
      <path d="M140 32 Q150 28 160 32" stroke="${c}" stroke-width="5" fill="none"/>
      <path d="M10 30 L-8 26 M290 30 L308 26" stroke="${c}" stroke-width="5" stroke-linecap="round"/>`,
  },
  geometric: {
    name: "Geometric",
    kind: "Eyeglasses / Sunglasses",
    svg: (c) => `
      <path d="M75 12 L124 30 L124 70 L75 88 L26 70 L26 30 Z" ${lensAttrs(c, 5)}/>
      <path d="M225 12 L274 30 L274 70 L225 88 L176 70 L176 30 Z" ${lensAttrs(c, 5)}/>
      <path d="M124 38 Q150 28 176 38" stroke="${c}" stroke-width="5" fill="none" stroke-linecap="round"/>
      <path d="M26 36 L8 30 M274 36 L292 30" stroke="${c}" stroke-width="5" stroke-linecap="round"/>`,
  },
};

export function frameSvgString(frameId, color) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 0 340 100" width="680" height="200">${FRAMES[frameId].svg(color)}</svg>`;
}

export function frameDataUrl(frameId, color) {
  return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(frameSvgString(frameId, color));
}

export function getRecommendations(faceShape) {
  const rules = RECOMMENDATIONS[faceShape] || RECOMMENDATIONS.Oval;
  return rules.map(([id, reason]) => ({ id, reason, ...FRAMES[id] }));
}

// ---------------------------------------------------------------------------
// Pemetaan model kacamata dari backend (field "style" di /recommendations)
// ke frame SVG lokal dan ke nama aset/parameter Virtual Try-On di backend.
//   svg     : id di FRAMES (untuk thumbnail cadangan & mode manual)
//   tryOn   : nilai `glasses_style` untuk POST /try-on (null = belum ada aset di backend)
//   asset   : nama file thumbnail di /assets/glasses/<asset>_test.png
// ---------------------------------------------------------------------------
export const STYLE_MAP = {
  rectangular: { svg: "rectangle", tryOn: "rectangular", asset: "rectangular" },
  round: { svg: "round", tryOn: "round", asset: "round" },
  "cat-eye": { svg: "cateye", tryOn: "cateye", asset: "cateye" },
  aviator: { svg: "aviator", tryOn: "aviator", asset: "aviator" },
  oval: { svg: "oval", tryOn: null, asset: null },
};

export const STYLE_ORDER = ["rectangular", "round", "cat-eye", "aviator", "oval"];

export function styleInfo(style) {
  return STYLE_MAP[style] || { svg: "round", tryOn: null, asset: null };
}
