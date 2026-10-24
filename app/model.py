import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

MODEL_PATH = "./models/training_results/faces/faceshape_mobilenetv2_best.keras"

model = tf.keras.models.load_model(
    MODEL_PATH,
    custom_objects={
        "preprocess_input": preprocess_input
    }
)

CLASS_NAMES = [
    "Heart",
    "Oblong",
    "Oval",
    "Round",
    "Square"
]