"""Prepare the five face-shape classes with a landmark-centered TRUE pixel crop.

Use: python -m training.prepare_faces --source datasets/raw/faces --landmarker models/face_landmarker.task
Strict mode never resizes pixels. It rejects samples where the entire padded
face region cannot fit inside a 224x224 crop, rather than cutting off jawline.
Optional --mode crop-then-resize is provided ONLY if strict mode rejects too
many samples; it resizes the isolated face crop, never the whole photograph.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import random
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

LABELS = ['Heart', 'Oblong', 'Oval', 'Round', 'Square']
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
SPLIT_ALIASES = {'train': 'train', 'training': 'train', 'test': 'test', 'testing': 'test'}


def class_directories(root):
    if not root.is_dir():
        return {}
    dirs = {p.name.lower(): p for p in root.iterdir() if p.is_dir()}
    return {label: dirs[label.lower()] for label in LABELS if label.lower() in dirs}


def discover_source(root):
    """Find Kaggle train/test folder structure or unsplit class folders."""
    candidates = [root] + [p for p in root.rglob('*') if p.is_dir()]
    splits = {}
    for p in candidates:
        if p.name.lower() in SPLIT_ALIASES and len(class_directories(p)) == len(LABELS):
            splits.setdefault(SPLIT_ALIASES[p.name.lower()], p)
    if 'train' in splits and 'test' in splits:
        return {name: gather_class_files(p) for name, p in splits.items()}, True
    for p in candidates:
        if len(class_directories(p)) == len(LABELS):
            return {'all': gather_class_files(p)}, False
    raise ValueError('Tidak ditemukan 5 folder kelas Heart/Oblong/Oval/Round/Square di dataset.')


def gather_class_files(root):
    result = []
    for label, folder in class_directories(root).items():
        result += [(p, label) for p in sorted(folder.rglob('*')) if p.is_file() and p.suffix.lower() in EXTENSIONS]
    return result


def stratified_split(items, val_frac, test_frac, seed):
    by_label = {label: [] for label in LABELS}
    for p, label in items:
        by_label[label].append((p, label))
    rng = random.Random(seed)
    ans = {'train': [], 'val': [], 'test': []}
    for label, samples in by_label.items():
        rng.shuffle(samples)
        n = len(samples)
        if n < 8:
            raise ValueError(f'Kelas {label} hanya {n} foto; minimal 8 agar 3 split masuk akal.')
        ntest = round(n * test_frac)
        nval = round(n * val_frac)
        ans['test'].extend(samples[:ntest])
        ans['val'].extend(samples[ntest:ntest+nval])
        ans['train'].extend(samples[ntest+nval:])
    return ans


class Landmarker:
    def __init__(self, task_path):
        import mediapipe as mp
        if not Path(task_path).is_file():
            raise FileNotFoundError(f'Face landmarker tidak ditemukan: {task_path}')
        self.mp = mp
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(Path(task_path).resolve())),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1,
        )
        self.detector = mp.tasks.vision.FaceLandmarker.create_from_options(options)

    def detect_box(self, image):
        image = image.convert('RGB')
        data = np.asarray(image, dtype=np.uint8)
        result = self.detector.detect(self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=data))
        if len(result.face_landmarks) != 1:
            raise ValueError('Tidak ditemukan tepat satu wajah.')
        points = result.face_landmarks[0]
        x = np.asarray([p.x for p in points]) * image.width
        y = np.asarray([p.y for p in points]) * image.height
        # Jaga dahi/rahang agar label bentuk wajah tetap dapat dinilai.
        xmin, xmax, ymin, ymax = x.min(), x.max(), y.min(), y.max()
        w, h = xmax - xmin, ymax - ymin
        return (xmin - .22*w, ymin - .32*h, xmax + .22*w, ymax + .20*h)

    def close(self):
        self.detector.close()


def strict_face_crop(image, box, size=224):
    """Lossless-scale 224px crop. Reject if face+margin cannot fit."""
    left, top, right, bottom = box
    if right-left > size or bottom-top > size:
        raise ValueError('ROI wajah >224px: strict crop akan membuang dahi/rahang.')
    if image.width < size or image.height < size:
        raise ValueError('Foto lebih kecil dari 224px: strict crop tidak memungkinkan.')
    cx, cy = (left+right)/2, (top+bottom)/2
    x0 = max(0, min(image.width-size, round(cx-size/2)))
    y0 = max(0, min(image.height-size, round(cy-size/2)))
    if not (x0 <= left and x0+size >= right and y0 <= top and y0+size >= bottom):
        raise ValueError('ROI dekat tepi foto: strict crop akan memotong wajah.')
    return image.crop((x0, y0, x0+size, y0+size))


def crop_then_resize(image, box, size=224):
    """Alternative: isolate square face ROI first, then size ONLY that ROI."""
    left, top, right, bottom = box
    side = max(right-left, bottom-top)
    cx, cy = (left+right)/2, (top+bottom)/2
    x0, y0 = round(cx-side/2), round(cy-side/2)
    x1, y1 = round(cx+side/2), round(cy+side/2)
    # Pad rather than cutting off a face near the image border.
    pad = (max(0,-x0), max(0,-y0), max(0,x1-image.width), max(0,y1-image.height))
    if any(pad):
        from PIL import ImageOps
        image = ImageOps.expand(image, border=pad, fill=(0, 0, 0))
        x0 += pad[0]; y0 += pad[1]; x1 += pad[0]; y1 += pad[1]
    return image.crop((x0,y0,x1,y1)).resize((size,size), Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('datasets/processed/faces'))
    parser.add_argument('--landmarker', type=Path, default=Path('models/face_landmarker.task'))
    parser.add_argument('--mode', choices=['strict','crop-then-resize'], default='strict')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    groups, predefined_test = discover_source(args.source)
    if predefined_test:
        # Keep publisher's test set untouched. Split original training 87.5:12.5.
        result = stratified_split(groups['train'], .125, 0., args.seed)
        result['test'] = groups['test']
    else:
        result = stratified_split(groups['all'], .15, .15, args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    detector = Landmarker(args.landmarker)
    rows, rejected, seen = [], [], set()
    try:
        for split in ['train', 'val', 'test']:
            for path, label in result[split]:
                try:
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    if digest in seen:
                        raise ValueError('Duplikat byte gambar pada/antar split.')
                    seen.add(digest)
                    with Image.open(path) as src:
                        image = ImageOps.exif_transpose(src).convert('RGB')
                    box = detector.detect_box(image)
                    crop = strict_face_crop(image, box) if args.mode == 'strict' else crop_then_resize(image, box)
                    folder = args.output / split / label
                    folder.mkdir(parents=True, exist_ok=True)
                    output = folder / f'{digest[:20]}.png'
                    crop.save(output)
                    rows.append([split, label, str(path), str(output), digest])
                except (ValueError, OSError, RuntimeError) as exc:
                    rejected.append([split, label, str(path), str(exc)])
    finally:
        detector.close()
    with (args.output/'manifest.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['split','label','source','processed','sha256']);w.writerows(rows)
    with (args.output/'rejected.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['split','label','source','reason']);w.writerows(rejected)
    counts=Counter((split, label) for split,label,*_ in rows)
    print(f'Berhasil: {len(rows)}, ditolak: {len(rejected)}. Mode crop: {args.mode}.')
    for s in ['train','val','test']:
        print(s, {label: counts[(s,label)] for label in LABELS})
    print('Lihat rejected.csv. Jangan lanjut training bila data kelas terbuang tidak seimbang.')
    for s in ['train', 'val', 'test']:
        for label in LABELS:
            if counts[(s,label)] == 0:
                raise RuntimeError(f'Split {s} kelas {label} kosong. Gunakan foto resolusi sesuai atau mode crop-then-resize.')

if __name__ == '__main__':
    main()
