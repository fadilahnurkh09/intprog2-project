"""Experimental mask extraction from a glasses-source image (NOT try-on).

Inputs must resemble images used for segmentation training. A mask on a face
photo is NOT a clean standalone eyeglasses product PNG by itself.
"""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
from .train_glasses import bce_dice,dice_score


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image',type=Path,required=True)
    p.add_argument('--model',type=Path,default=Path('models/training_results/glasses/glasses_segmentation_best.keras'))
    p.add_argument('--output',type=Path,default=Path('glasses_cutout.png'))
    p.add_argument('--threshold',type=float,default=.5)
    a=p.parse_args()
    import tensorflow as tf
    with Image.open(a.image) as src:
        rgb=src.convert('RGB')
    if rgb.width<224 or rgb.height<224:
        raise ValueError('Gambar lebih kecil dari 224x224; crop tanpa resizing tidak memungkinkan.')
    x0=(rgb.width-224)//2;y0=(rgb.height-224)//2
    rgb=rgb.crop((x0,y0,x0+224,y0+224))
    model=tf.keras.models.load_model(a.model,custom_objects={'bce_dice':bce_dice,'dice_score':dice_score})
    mask=model.predict(np.asarray(rgb,dtype=np.float32)[None],verbose=0)[0,:,:,0]
    alpha=np.where(mask>=a.threshold,255,0).astype(np.uint8)
    out=np.dstack([np.asarray(rgb),alpha])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(out,'RGBA').save(a.output)
    print('Mask/cutout eksperimen:',a.output)
    print('Periksa manual; keluaran ini BELUM dijamin cocok sebagai aset try-on.')

if __name__=='__main__':main()
