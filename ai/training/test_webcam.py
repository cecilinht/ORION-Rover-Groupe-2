
import cv2
import json
import time
import numpy as np
import tensorflow as tf
from pathlib import Path

# Chemins du projet
BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ai" / "models" / "orion_rover_first_cnn.keras"
LABELS_PATH = BASE_DIR / "ai" / "models" / "orion_rover_first_labels.json"

IMAGE_SIZE = 128

# Charger le modèle
print("Chargement du modele ORION-Rover...")

model = tf.keras.models.load_model(MODEL_PATH)

with open(LABELS_PATH, "r", encoding="utf-8") as file:
    labels = json.load(file)

print("Modele charge avec succes !")

# Ouvrir la webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Erreur : impossible d'ouvrir la webcam.")
    exit()

print("Webcam activee.")
print("Place un panneau devant la camera.")
print("Appuie sur Q pour quitter.")

while True:

    success, frame = camera.read()

    if not success:
        print("Erreur de capture.")
        break

    # Obtenir les dimensions de l'image
    height, width = frame.shape[:2]

    # Definir une zone centrale carree
    size = min(height, width) // 2

    x1 = width // 2 - size // 2
    y1 = height // 2 - size // 2
    x2 = x1 + size
    y2 = y1 + size

    # Extraire la zone centrale
    roi = frame[y1:y2, x1:x2]

    # Preparer l'image pour le CNN
    image = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE))
    image = image.astype(np.float32)

    image = np.expand_dims(image, axis=0)

    # Prediction
    start_time = time.time()

    predictions = model.predict(image, verbose=0)[0]

    elapsed = (time.time() - start_time) * 1000

    predicted_index = int(np.argmax(predictions))

    predicted_class = labels[str(predicted_index)]

    confidence = float(predictions[predicted_index]) * 100

    # Afficher le resultat
    color = (0, 255, 0) if confidence >= 80 else (0, 165, 255)

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        color,
        2
    )

    cv2.putText(
        frame,
        f"{predicted_class}: {confidence:.1f}%",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        color,
        2
    )

    cv2.putText(
        frame,
        f"Temps: {elapsed:.0f} ms",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.imshow("ORION-ROVER - Reconnaissance IA", frame)

    # Quitter avec Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("Test webcam termine.")
