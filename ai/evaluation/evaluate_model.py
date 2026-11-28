
import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score
)

# ==========================================
# ORION-ROVER : EVALUATION DU MODELE IA
# ==========================================

DATASET_PATH = "ai/dataset/processed/dataset.npz"
MODEL_PATH = "ai/models/orion_rover_cnn.keras"
OUTPUT_DIR = "ai/evaluation"

CLASS_NAMES = [
    "STOP",
    "LEFT",
    "RIGHT",
    "SLOW",
    "ARRIVAL",
    "NO_SIGN"
]

print("Evaluation du modele ORION-Rover...")

# Verifier les fichiers necessaires
if not os.path.exists(DATASET_PATH):
    print("Dataset introuvable :", DATASET_PATH)
    raise SystemExit

if not os.path.exists(MODEL_PATH):
    print("Modele introuvable :", MODEL_PATH)
    raise SystemExit

# Charger les donnees de validation
data = np.load(DATASET_PATH)

X_val = data["X_val"]
y_val = data["y_val"]

if len(X_val) == 0:
    print("Aucune image de validation disponible.")
    raise SystemExit

# Charger le modele entraine
model = tf.keras.models.load_model(MODEL_PATH)

# Faire les predictions
predictions = model.predict(X_val, verbose=0)

# Recuperer la classe ayant la probabilite la plus elevee
y_pred = np.argmax(predictions, axis=1)

# Calculer l'accuracy
accuracy = accuracy_score(y_val, y_pred)

print("\nAccuracy :", round(accuracy * 100, 2), "%")

# Rapport de classification
print("\nRapport de classification :")

print(classification_report(
    y_val,
    y_pred,
    labels=list(range(len(CLASS_NAMES))),
    target_names=CLASS_NAMES,
    zero_division=0
))

# Creer la matrice de confusion
matrix = confusion_matrix(
    y_val,
    y_pred,
    labels=list(range(len(CLASS_NAMES)))
)

display = ConfusionMatrixDisplay(
    confusion_matrix=matrix,
    display_labels=CLASS_NAMES
)

display.plot(
    cmap="Blues",
    xticks_rotation=45,
    values_format="d"
)

plt.title("ORION-Rover - Matrice de confusion")
plt.tight_layout()

# Creer le dossier de sortie
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Enregistrer la matrice
matrix_path = os.path.join(
    OUTPUT_DIR,
    "confusion_matrix.png"
)

plt.savefig(matrix_path, dpi=300)

print("\nMatrice sauvegardee :", matrix_path)

plt.show()

print("\nEvaluation terminee.")
