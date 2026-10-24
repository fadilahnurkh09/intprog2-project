"""Demo inference image-to-label after training with the EXACT same face crop.

Run: python -m training.infer_face --image photo.jpg --mode strict
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from .prepare_faces import Landmarker, strict_face_crop, crop_then_resize, LABELS


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image',type=Path,required=True)
    p.add_argument('--model',type=Path,default=Path('models/training_results/faces/faceshape_mobilenetv2_best.keras'))
    p.add_argument('--landmarker',type=Path,default=Path('models/face_landmarker.task'))
    p.add_argument('--mode',choices=['strict','crop-then-resize'],default='strict')
    a=p.parse_args()
    import tensorflow as tf
    with Image.open(a.image) as f:
        image=ImageOps.exif_transpose(f).convert('RGB')
    detector=Landmarker(a.landmarker)
    try: box=detector.detect_box(image)
    finally: detector.close()
    patch=strict_face_crop(image,box) if a.mode=='strict' else crop_then_resize(image,box)
    # Do NOT call MobileNetV2 preprocess_input here: normalization is in model!
    model=tf.keras.models.load_model(a.model)
    probs=model.predict(np.asarray(patch,dtype=np.float32)[None],verbose=0)[0]
    idx=int(np.argmax(probs))
    print(json.dumps({'class_names':LABELS,'prediction':LABELS[idx],
        'confidence':float(probs[idx]),
        'probabilities':{name:float(score) for name,score in zip(LABELS,probs)}},
        indent=2,ensure_ascii=False))

if __name__=='__main__':main()
