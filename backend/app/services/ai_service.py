
import json
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf


# Chemin principal du projet
BASE_DIR = Path(__file__).resolve().parents[3]

# Modèle CNN entraîné localement
MODEL_PATH = (
    BASE_DIR / "ai" / "models" /
    "orion_rover_first_cnn.keras"
)

# Fichier contenant les noms des classes
LABELS_PATH = (
    BASE_DIR / "ai" / "models" /
    "orion_rover_first_labels.json"
)

IMAGE_SIZE = 128

_model = None
_labels = None


# Charger le modèle une seule fois
def load_model():

    global _model, _labels

    if _model is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modele introuvable : {MODEL_PATH}"
            )

        if not LABELS_PATH.exists():
            raise FileNotFoundError(
                f"Fichier des classes introuvable : {LABELS_PATH}"
            )

        _model = tf.keras.models.load_model(MODEL_PATH)

        with open(LABELS_PATH, "r", encoding="utf-8") as file:
            _labels = json.load(file)

    return _model, _labels


# Préparer une image pour le CNN
def prepare_image(image_bytes):

    if not image_bytes:
        raise ValueError("Image vide")

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError("Format d'image invalide")

    # Extraire une zone carrée centrale
    height, width = image.shape[:2]

    size = min(height, width)

    x1 = (width - size) // 2
    y1 = (height - size) // 2

    image = image[
        y1:y1 + size,
        x1:x1 + size
    ]

    # Conversion BGR vers RGB
    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    # Redimensionnement
    image = cv2.resize(
        image,
        (IMAGE_SIZE, IMAGE_SIZE)
    )

    image = image.astype(np.float32)

    image = np.expand_dims(image, axis=0)

    return image


# Reconnaissance du panneau
def predict_sign(image_bytes):

    model, labels = load_model()

    image = prepare_image(image_bytes)

    predictions = model.predict(
        image,
        verbose=0
    )[0]

    if len(predictions) != len(labels):
        raise ValueError(
            "Le nombre de classes du modele est incorrect"
        )

    predicted_index = int(np.argmax(predictions))

    predicted_class = labels[str(predicted_index)]

    confidence = float(
        predictions[predicted_index]
    ) * 100

    return {
        "class": predicted_class,
        "confidence": round(confidence, 2),
        "message": "Panneau analyse par le modele CNN local"
    }
