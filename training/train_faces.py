"""Two-stage MobileNetV2 face-shape training + single held-out test evaluation.

Run: python -m training.train_faces --data datasets/processed/faces
No part of this script uses the held-out testing set for hyperparameter choice.
"""
from __future__ import annotations
import argparse
import csv
import json
import random
import shutil
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support

LABELS=['Heart','Oblong','Oval','Round','Square']


def set_seed(seed):
    import tensorflow as tf
    random.seed(seed);np.random.seed(seed);tf.keras.utils.set_random_seed(seed)
    try: tf.config.experimental.enable_op_determinism()
    except Exception: pass


def load_images(data_dir, split, batch, shuffle):
    import tensorflow as tf
    directory=data_dir/split
    if not directory.is_dir(): raise ValueError(f'Split tidak ditemukan: {directory}')
    for label in LABELS:
        if not any((directory/label).glob('*.png')):
            raise ValueError(f'Kelas {label} kosong di split {split}.')
    ds=tf.keras.utils.image_dataset_from_directory(
        directory,labels='inferred',label_mode='categorical',class_names=LABELS,
        image_size=(224,224),batch_size=batch,shuffle=shuffle,seed=42,
        interpolation='nearest',
    )
    return ds


def build_model():
    import tensorflow as tf
    k=tf.keras
    backbone=k.applications.MobileNetV2(
        input_shape=(224,224,3),include_top=False,weights='imagenet')
    backbone.trainable=False
    inp=k.Input(shape=(224,224,3),name='face_rgb_0_255')
    x=k.Sequential([
        k.layers.RandomFlip('horizontal'),
        k.layers.RandomContrast(0.08),
    ],name='training_only_augment')(inp)
    # MobileNetV2 requires [-1,+1], not [0,1]. Keep inside saved model!
    x=k.layers.Rescaling(1/127.5,offset=-1,name='mobilenetv2_preprocessing')(x)
    x=backbone(x,training=False)  # freeze moving BN statistics also in stage two
    x=k.layers.GlobalAveragePooling2D()(x)
    x=k.layers.Dense(128,activation='relu')(x)
    x=k.layers.Dropout(.35)(x)
    out=k.layers.Dense(5,activation='softmax',name='face_shape')(x)
    return k.Model(inp,out,name='framefit_face_shape')


def compile_model(model, lr):
    import tensorflow as tf
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
                  loss=tf.keras.losses.CategoricalCrossentropy(),
                  metrics=[tf.keras.metrics.CategoricalAccuracy(name='accuracy')])


def get_backbone(model):
    import tensorflow as tf
    for layer in model.layers:
        if isinstance(layer,tf.keras.Model) and layer.name.startswith('mobilenetv2'):
            return layer
    raise RuntimeError('MobileNetV2 backbone tidak ditemukan di model.')


def callbacks(out_dir, stage):
    import tensorflow as tf
    return [
        tf.keras.callbacks.ModelCheckpoint(str(out_dir/f'{stage}_best.keras'),
            monitor='val_loss',mode='min',save_best_only=True,verbose=1),
        tf.keras.callbacks.EarlyStopping(monitor='val_loss',mode='min',patience=5,
            restore_best_weights=True,verbose=1),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',factor=.5,patience=2,min_lr=1e-7),
        tf.keras.callbacks.CSVLogger(str(out_dir/f'{stage}_history.csv')),
        tf.keras.callbacks.TerminateOnNaN(),
    ]


def plot_history(out, first, second):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes=plt.subplots(1,2,figsize=(11,4))
    for ax,key in zip(axes,['loss','accuracy']):
        offset=0
        for name,h in [('head',first),('fine-tune',second)]:
            v=h.history.get(key,[])
            vv=h.history.get('val_'+key,[])
            ax.plot(range(offset+1,offset+len(v)+1),v,label=name+' train')
            ax.plot(range(offset+1,offset+len(vv)+1),vv,label=name+' val',linestyle='--')
            offset+=len(v)
        ax.set_title(key);ax.set_xlabel('Epoch');ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/'training_history.png',dpi=150);plt.close(fig)


def evaluate_final(model,ds,out,accept_accuracy=.85):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import tensorflow as tf
    loss,acc=model.evaluate(ds,verbose=1)
    y_true=np.concatenate([np.argmax(y.numpy(),axis=1) for _,y in ds],axis=0)
    probs=model.predict(ds,verbose=1)
    y_pred=probs.argmax(axis=1)
    metrics=classification_report(y_true,y_pred,labels=range(5),target_names=LABELS,
                                  output_dict=True,zero_division=0)
    macro_p,macro_r,macro_f,_=precision_recall_fscore_support(y_true,y_pred,labels=range(5),average='macro',zero_division=0)
    overall_acc=accuracy_score(y_true,y_pred)
    confusion=confusion_matrix(y_true,y_pred,labels=list(range(5)))
    pairs=sorted([{'actual':LABELS[i],'predicted':LABELS[j],'count':int(confusion[i,j])}
        for i in range(5) for j in range(5) if i!=j and confusion[i,j]>0],
        key=lambda x:x['count'],reverse=True)
    summary={'test_samples':len(y_true),'test_loss':float(loss),'test_accuracy':float(overall_acc),
             'test_macro_precision':float(macro_p),'test_macro_recall':float(macro_r),
             'test_macro_f1':float(macro_f),'target_accuracy_gt_85_met':bool(overall_acc>accept_accuracy),
             'classification_report':metrics,'most_confused_class_pairs':pairs[:10],
             'labels':LABELS,
             'note':'Test set dievaluasi sesudah pemilihan model berdasarkan validation loss.'}
    (out/'face_test_metrics.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    with (out/'face_per_class_metrics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['label','precision','recall','f1_score','support'])
        for name in LABELS:
            row=metrics[name];w.writerow([name,row['precision'],row['recall'],row['f1-score'],row['support']])
    with (out/'face_test_predictions.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['filename','true_label','predicted_label','confidence','correct'])
        paths=getattr(ds,'file_paths',[])
        for i,(truth,pred) in enumerate(zip(y_true,y_pred)):
            w.writerow([str(paths[i]) if i<len(paths) else f'index_{i}',LABELS[truth],LABELS[pred],
                        float(probs[i,pred]),int(truth==pred)])
    fig,ax=plt.subplots(figsize=(7,6)); im=ax.imshow(confusion,cmap='Blues')
    ax.set(xticks=range(5),yticks=range(5),xticklabels=LABELS,yticklabels=LABELS,
           xlabel='Prediksi',ylabel='Label sebenarnya',title='Confusion Matrix - Testing')
    for i in range(5):
        for j in range(5):
            ax.text(j,i,str(confusion[i,j]),ha='center',va='center',
                    color='white' if confusion[i,j]>confusion.max()/2 else 'black')
    fig.colorbar(im,ax=ax,shrink=.8);fig.tight_layout();fig.savefig(out/'face_confusion_matrix.png',dpi=180);plt.close(fig)
    print(json.dumps({k:summary[k] for k in ('test_loss','test_accuracy','test_macro_precision','test_macro_recall','test_macro_f1','target_accuracy_gt_85_met','most_confused_class_pairs')},indent=2))
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path('datasets/processed/faces'))
    p.add_argument('--output',type=Path,default=Path('models/training_results/faces'))
    p.add_argument('--batch',type=int,default=32)
    p.add_argument('--head-epochs',type=int,default=20)
    p.add_argument('--fine-epochs',type=int,default=20)
    p.add_argument('--unfreeze-last',type=int,default=35)
    p.add_argument('--seed',type=int,default=42)
    args=p.parse_args()
    import tensorflow as tf
    set_seed(args.seed);args.output.mkdir(parents=True,exist_ok=True)
    train=load_images(args.data,'train',args.batch,True).prefetch(tf.data.AUTOTUNE)
    val=load_images(args.data,'val',args.batch,False)
    test=load_images(args.data,'test',args.batch,False)
    model=build_model();compile_model(model,1e-3)
    head=model.fit(train,validation_data=val,epochs=args.head_epochs,
                   callbacks=callbacks(args.output,'head'))
    head_best=tf.keras.models.load_model(args.output/'head_best.keras')
    head_val_loss,head_val_acc=head_best.evaluate(val,verbose=0)
    # The test data is deliberately never used at this point.
    ft=head_best
    base=get_backbone(ft);base.trainable=True
    for layer in base.layers:
        layer.trainable=False
    for layer in base.layers[-args.unfreeze_last:]:
        if not isinstance(layer,tf.keras.layers.BatchNormalization): layer.trainable=True
    compile_model(ft,1e-5)  # RE-COMPILE is mandatory after unfreezing
    fine=ft.fit(train,validation_data=val,epochs=args.fine_epochs,
                callbacks=callbacks(args.output,'fine'))
    fine_best=tf.keras.models.load_model(args.output/'fine_best.keras')
    fine_val_loss,fine_val_acc=fine_best.evaluate(val,verbose=0)
    choice='fine' if fine_val_loss<head_val_loss else 'head'
    winner=fine_best if choice=='fine' else head_best
    final_path=args.output/'faceshape_mobilenetv2_best.keras'
    winner.save(final_path)
    (args.output/'class_names.json').write_text(json.dumps(LABELS,indent=2),encoding='utf-8')
    (args.output/'validation_comparison.json').write_text(json.dumps({
        'head':{'val_loss':float(head_val_loss),'val_accuracy':float(head_val_acc)},
        'fine':{'val_loss':float(fine_val_loss),'val_accuracy':float(fine_val_acc)},
        'selected_stage':choice,'best_model_path':str(final_path)},indent=2),encoding='utf-8')
    plot_history(args.output,head,fine)
    evaluate_final(winner,test,args.output)
    print(f'Best model: {final_path}. Pilihan berdasarkan validation loss: {choice}.')

if __name__=='__main__':
    main()
