"""Two-stage MobileNetV2 encoder + U-Net-like glasses FRAME segmentation.

Masks must be paired frame-specific binary masks (not face-shape labels).
No testing sample is used to choose the model / epochs / learning rate.
"""
from __future__ import annotations
import argparse
import csv
import json
import random
from pathlib import Path
import numpy as np


def set_seed(seed):
    import tensorflow as tf
    random.seed(seed);np.random.seed(seed);tf.keras.utils.set_random_seed(seed)


def get_pairs(directory):
    images=sorted((directory/'images').glob('*.png'))
    if not images: raise ValueError(f'Tidak ada gambar di {directory}/images')
    pairs=[]
    for f in images:
        m=directory/'masks'/f.name
        if not m.exists():raise ValueError(f'Mask tidak ada untuk {f}')
        pairs.append((str(f),str(m)))
    return pairs


def dataset(pairs,batch,shuffle=False):
    import tensorflow as tf
    xpaths=[x for x,_ in pairs];ypaths=[y for _,y in pairs]
    ds=tf.data.Dataset.from_tensor_slices((xpaths,ypaths))
    if shuffle: ds=ds.shuffle(min(len(pairs),5000),seed=42,reshuffle_each_iteration=True)
    def load(xfile,yfile):
        x=tf.io.decode_png(tf.io.read_file(xfile),channels=3)
        y=tf.io.decode_png(tf.io.read_file(yfile),channels=1)
        x=tf.ensure_shape(tf.cast(x,tf.float32),(224,224,3))
        y=tf.ensure_shape(tf.cast(y>127,tf.float32),(224,224,1))
        return x,y
    ds=ds.map(load,num_parallel_calls=tf.data.AUTOTUNE)
    if shuffle:
        def aug(x,y):
            flip=tf.random.uniform(())<.5
            return tf.cond(flip,lambda: (tf.image.flip_left_right(x),tf.image.flip_left_right(y)),lambda:(x,y))
        ds=ds.map(aug,num_parallel_calls=tf.data.AUTOTUNE)
    return ds.batch(batch).prefetch(tf.data.AUTOTUNE)


def dice_score(y_true,y_pred):
    import tensorflow as tf
    y_true=tf.cast(y_true,tf.float32)
    y_pred=tf.cast(y_pred,tf.float32)
    axes=(1,2,3)
    return tf.reduce_mean((2*tf.reduce_sum(y_true*y_pred,axis=axes)+1.)/
        (tf.reduce_sum(y_true+y_pred,axis=axes)+1.))


def bce_dice(y_true,y_pred):
    import tensorflow as tf
    bce=tf.reduce_mean(tf.keras.losses.binary_crossentropy(y_true,y_pred))
    return .5*bce+.5*(1.-dice_score(y_true,y_pred))


def build_model():
    import tensorflow as tf
    k=tf.keras
    backbone=k.applications.MobileNetV2(input_shape=(224,224,3),include_top=False,weights='imagenet')
    layers=['block_1_expand_relu','block_3_expand_relu','block_6_expand_relu',
            'block_13_expand_relu','block_16_project']
    encoder=k.Model(backbone.input,[backbone.get_layer(n).output for n in layers],name='glasses_backbone')
    encoder.trainable=False
    inp=k.Input(shape=(224,224,3),name='glasses_rgb_0_255')
    x=k.layers.Rescaling(1/127.5,offset=-1)(inp)
    feats=encoder(x,training=False)
    x=feats[-1]
    for i,(skip,filters) in enumerate(zip(reversed(feats[:-1]),[192,128,64,32])):
        x=k.layers.Conv2DTranspose(filters,3,strides=2,padding='same',activation='relu',name=f'decoder_up_{i}')(x)
        x=k.layers.Concatenate()([x,skip])
        x=k.layers.Conv2D(filters,3,padding='same',activation='relu')(x)
    x=k.layers.Conv2DTranspose(16,3,strides=2,padding='same',activation='relu')(x)
    out=k.layers.Conv2D(1,1,activation='sigmoid',name='glasses_mask')(x)
    return k.Model(inp,out,name='framefit_glasses_segmentation')


def compile_model(model,lr):
    import tensorflow as tf
    model.compile(optimizer=tf.keras.optimizers.Adam(lr),loss=bce_dice,
        metrics=[tf.keras.metrics.BinaryAccuracy(name='pixel_accuracy'),
                 tf.keras.metrics.BinaryIoU(name='foreground_iou',target_class_ids=[1],threshold=.5),
                 dice_score,tf.keras.metrics.Precision(name='pixel_precision'),
                 tf.keras.metrics.Recall(name='pixel_recall')])


def callback_list(out,phase):
    import tensorflow as tf
    return [
        tf.keras.callbacks.ModelCheckpoint(str(out/f'{phase}_best.keras'),monitor='val_loss',mode='min',save_best_only=True),
        tf.keras.callbacks.EarlyStopping(monitor='val_loss',mode='min',patience=5,restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',factor=.5,patience=2,min_lr=1e-7),
        tf.keras.callbacks.CSVLogger(str(out/f'{phase}_history.csv')),
        tf.keras.callbacks.TerminateOnNaN(),
    ]


def evaluate_test(model,ds,pairs,out):
    import tensorflow as tf
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    values=model.evaluate(ds,return_dict=True,verbose=1)
    tp=fp=fn=tn=0
    per=[]
    samples_dir=out/'segmentation_examples';samples_dir.mkdir(exist_ok=True)
    k=0
    for xb,yb in ds:
        predictions=model.predict(xb,verbose=0)
        xs=xb.numpy();ys=yb.numpy()
        for x,y,pred in zip(xs,ys,predictions):
            gt=y[:,:,0]>=.5; pr=pred[:,:,0]>=.5
            t=int(np.logical_and(gt,pr).sum())
            f=int(np.logical_and(~gt,pr).sum())
            miss=int(np.logical_and(gt,~pr).sum())
            true_neg=int(np.logical_and(~gt,~pr).sum())
            tp+=t;fp+=f;fn+=miss;tn+=true_neg
            iou=t/(t+f+miss) if (t+f+miss) else 1.0
            dice=2*t/(2*t+f+miss) if (2*t+f+miss) else 1.0
            per.append([pairs[k][0],iou,dice])
            if k<10:
                fig,axes=plt.subplots(1,3,figsize=(10,3))
                axes[0].imshow(x.astype('uint8'));axes[0].set_title('Citra asli')
                axes[1].imshow(gt,cmap='gray',vmin=0,vmax=1);axes[1].set_title('Mask label')
                axes[2].imshow(pred[:,:,0],cmap='gray',vmin=0,vmax=1);axes[2].set_title('Mask prediksi')
                for a in axes:a.axis('off')
                fig.tight_layout();fig.savefig(samples_dir/f'{k:03d}.png',dpi=120);plt.close(fig)
            k+=1
    precision=tp/max(1,tp+fp);recall=tp/max(1,tp+fn)
    f1=2*precision*recall/max(1e-9,precision+recall)
    result={'test_loss':float(values['loss']),
            'test_pixel_accuracy':(tp+tn)/max(1,tp+tn+fp+fn),
            'test_foreground_iou_global':tp/max(1,tp+fp+fn),
            'test_mean_image_iou':float(np.mean([row[1] for row in per])),
            'test_mean_image_dice':float(np.mean([row[2] for row in per])),
            'test_pixel_precision':precision,'test_pixel_recall':recall,
            'test_pixel_f1':f1,'confusion_pixels':{'TP':tp,'FP':fp,'FN':fn,'TN':tn},
            'note':'Accuracy pixel bisa tinggi karena mayoritas latar belakang. Utamakan foreground IoU dan Dice.'}
    (out/'glasses_test_metrics.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    with (out/'glasses_per_image_metrics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['image_path','iou','dice']);w.writerows(sorted(per,key=lambda x:x[1]))
    print(json.dumps(result,indent=2,ensure_ascii=False))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path('datasets/processed/glasses'))
    p.add_argument('--output',type=Path,default=Path('models/training_results/glasses'))
    p.add_argument('--batch',type=int,default=16)
    p.add_argument('--head-epochs',type=int,default=25)
    p.add_argument('--fine-epochs',type=int,default=20)
    p.add_argument('--unfreeze-last',type=int,default=35)
    p.add_argument('--seed',type=int,default=42)
    args=p.parse_args()
    import tensorflow as tf
    set_seed(args.seed);args.output.mkdir(parents=True,exist_ok=True)
    train_pairs=get_pairs(args.data/'train')
    val_pairs=get_pairs(args.data/'val')
    test_pairs=get_pairs(args.data/'test')
    train=dataset(train_pairs,args.batch,shuffle=True)
    val=dataset(val_pairs,args.batch)
    test=dataset(test_pairs,args.batch)
    model=build_model();compile_model(model,1e-3)
    model.fit(train,validation_data=val,epochs=args.head_epochs,
              callbacks=callback_list(args.output,'head'))
    head=tf.keras.models.load_model(args.output/'head_best.keras',custom_objects={'bce_dice':bce_dice,'dice_score':dice_score})
    v_head=head.evaluate(val,return_dict=True,verbose=0)
    encoder=head.get_layer('glasses_backbone');encoder.trainable=True
    for l in encoder.layers:l.trainable=False
    for l in encoder.layers[-args.unfreeze_last:]:
        if not isinstance(l,tf.keras.layers.BatchNormalization):l.trainable=True
    compile_model(head,1e-5)
    head.fit(train,validation_data=val,epochs=args.fine_epochs,
             callbacks=callback_list(args.output,'fine'))
    fine=tf.keras.models.load_model(args.output/'fine_best.keras',custom_objects={'bce_dice':bce_dice,'dice_score':dice_score})
    v_fine=fine.evaluate(val,return_dict=True,verbose=0)
    selected='fine' if v_fine['loss']<v_head['loss'] else 'head'
    winner=fine if selected=='fine' else tf.keras.models.load_model(args.output/'head_best.keras',custom_objects={'bce_dice':bce_dice,'dice_score':dice_score})
    target=args.output/'glasses_segmentation_best.keras';winner.save(target)
    (args.output/'validation_comparison.json').write_text(json.dumps({
        'head':{k:float(v) for k,v in v_head.items()},
        'fine':{k:float(v) for k,v in v_fine.items()},
        'selected_stage':selected},indent=2),encoding='utf-8')
    evaluate_test(winner,test,test_pairs,args.output)
    print('Model final:',target,'; selected:',selected)

if __name__=='__main__':
    main()
