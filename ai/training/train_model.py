
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

# ==========================================
# ORION-ROVER : ENTRAINEMENT DU MODELE CNN
# ==========================================

# Chemins des fichiers
DATASET_PATH = "ai/dataset/processed/dataset.npz"
MODEL_DIR = "ai/models"
MODEL_PATH = os.path.join(MODEL_DIR, "orion_rover_cnn.keras")

# Parametres du modele
IMAGE_SIZE = 128
BATCH_SIZE = 16
EPOCHS = 20
NUM_CLASSES = 6

# Noms des classes
CLASS_NAMES = [
    "STOP",
    "LEFT",
    "RIGHT",
    "SLOW",
    "ARRIVAL",
    "NO_SIGN"
]

print("ORION-Rover : entrainement du modele CNN")

# Verifier la presence du dataset
if not os.path.exists(DATASET_PATH):
    print("Dataset introuvable :", DATASET_PATH)
    print("Ajoute et prepare les images avant l'entrainement.")
    raise SystemExit

# Charger les donnees
data = np.load(DATASET_PATH)

X_train = data["X_train"]
X_val = data["X_val"]
y_train = data["y_train"]
y_val = data["y_val"]

# Verifier les donnees
if len(X_train) == 0 or len(X_val) == 0:
    print("Dataset vide : entrainement impossible.")
    raise SystemExit

if len(np.unique(y_train)) < NUM_CLASSES:
    print("Attention : les six classes ne sont pas presentes.")
    raise SystemExit

print("Images entrainement :", len(X_train))
print("Images validation :", len(X_val))

# Creer le modele CNN
model = models.Sequential([
    layers.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3)),

    # Premier bloc convolutionnel
    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    # Deuxieme bloc convolutionnel
    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    # Troisieme bloc convolutionnel
    layers.Conv2D(128, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    # Classification
    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(NUM_CLASSES, activation="softmax")
])

# Compiler le modele
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# Afficher architecture du modele
model.summary()

# Creer le dossier du modele
os.makedirs(MODEL_DIR, exist_ok=True)

# Sauvegarder le meilleur modele
checkpoint = tf.keras.callbacks.ModelCheckpoint(
    MODEL_PATH,
    monitor="val_accuracy",
    save_best_only=True,
    mode="max",
    verbose=1
)

# Arreter si le modele ne progresse plus
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

# Entrainement
print("\nDebut de l'entrainement...")

history = model.fit(
    X_train,
    y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=[checkpoint, early_stopping]
)

# Evaluation
loss, accuracy = model.evaluate(X_val, y_val, verbose=0)

print("\nEntrainement termine.")
print("Loss :", loss)
print("Accuracy validation :", accuracy)

# Sauvegarder le modele final
model.save(MODEL_PATH)

print("Modele sauvegarde :", MODEL_PATH)
