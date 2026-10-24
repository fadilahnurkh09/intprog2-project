"""Prepare aligned image/mask pairs for glasses-frame binary segmentation.

The data must provide paired masks already; classification labels are NOT masks.
True 224x224 CENTER CROPS are applied to BOTH image and mask with identical
coordinates, without shrinking the whole picture.
"""
import argparse
import csv
import random
from pathlib import Path
from PIL import Image, ImageOps

EXTS={'.png','.jpg','.jpeg','.webp'}


def center_crop_pair(image, mask, size=224):
    if image.size != mask.size:
        raise ValueError(f'Ukuran gambar {image.size} != mask {mask.size}.')
    w,h=image.size
    if w<size or h<size:
        raise ValueError('Dimensi <224; crop tanpa resize tidak mungkin.')
    x=(w-size)//2; y=(h-size)//2
    box=(x,y,x+size,y+size)
    return image.crop(box), mask.crop(box)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images',type=Path,required=True,help='Folder gambar sumber')
    p.add_argument('--masks',type=Path,required=True,help='Folder mask frames berpasangan')
    p.add_argument('--mask-suffix',default='',help='Contoh: _frames pada nama file mask')
    p.add_argument('--output',type=Path,default=Path('datasets/processed/glasses'))
    p.add_argument('--seed',type=int,default=42)
    a=p.parse_args()
    image_files=sorted(x for x in a.images.rglob('*') if x.is_file() and x.suffix.lower() in EXTS)
    masks={x.stem:x for x in a.masks.rglob('*') if x.is_file() and x.suffix.lower() in EXTS}
    pairs=[];rejected=[]
    for x in image_files:
        m=masks.get(x.stem+a.mask_suffix)
        if m is None:
            rejected.append([str(x),'Pasangan mask tidak ditemukan']);continue
        pairs.append((x,m))
    random.Random(a.seed).shuffle(pairs)
    n=len(pairs)
    if n<30:
        raise ValueError(f'Hanya {n} pasangan ditemukan, cek penamaan mask dan folder.')
    ntest=round(n*.15);nval=round(n*.15)
    splits={'test':pairs[:ntest],'val':pairs[ntest:ntest+nval],'train':pairs[ntest+nval:]}
    rows=[]
    for split, files in splits.items():
        for i,(photo,mask_file) in enumerate(files):
            try:
                with Image.open(photo) as img, Image.open(mask_file) as m:
                    # Avoid separate EXIF transforms that would break mask alignment.
                    if img.getexif().get(274,1) != 1 or m.getexif().get(274,1) != 1:
                        raise ValueError('EXIF orientation non-standar; normalisasi gambar dan mask bersama.')
                    img=img.convert('RGB');m=m.convert('L')
                    x,y=center_crop_pair(img,m)
                    y=y.point(lambda pixel: 255 if pixel>=128 else 0)
                    # Reject all-background/all-foreground masks: typically data pairing errors.
                    box=y.getbbox()
                    if box is None:
                        raise ValueError('Mask kosong.')
                    import numpy as np
                    if np.asarray(y).mean() > 245:
                        raise ValueError('Mask hampir seluruhnya foreground.')
                    name=f'{split}_{i:07d}.png'
                    xd=a.output/split/'images'/name;yd=a.output/split/'masks'/name
                    xd.parent.mkdir(parents=True,exist_ok=True);yd.parent.mkdir(parents=True,exist_ok=True)
                    x.save(xd);y.save(yd)
                    rows.append([split,str(photo),str(mask_file),str(xd),str(yd)])
            except (OSError, ValueError) as exc:
                rejected.append([str(photo),str(exc)])
    a.output.mkdir(parents=True,exist_ok=True)
    with (a.output/'manifest.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['split','source_image','source_mask','image','mask']);w.writerows(rows)
    with (a.output/'rejected.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['source','reason']);w.writerows(rejected)
    print(f'Pasangan valid={len(rows)}, ditolak={len(rejected)}; lihat manifest.csv/rejected.csv')
    counts={s:sum(1 for r in rows if r[0]==s) for s in splits}
    print(counts)
    if min(counts.values()) == 0:
        raise RuntimeError('Ada split kosong: periksa nama dan ukuran mask.')

if __name__=='__main__':
    main()
