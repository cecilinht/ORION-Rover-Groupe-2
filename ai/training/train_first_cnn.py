
import os
import json
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight

# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = (
    BASE_DIR / "ai" / "dataset" / "raw" /
    "GTSRB" / "GTSRB" / "Final_Training" / "Images"
)

MODEL_DIR = BASE_DIR / "ai" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "orion_rover_first_cnn.keras"
LABELS_PATH = MODEL_DIR / "orion_rover_first_labels.json"

IMAGE_SIZE = 128
BATCH_SIZE = 16
EPOCHS = 15

# Identifiants GTSRB et noms de nos catégories
CLASSES = {
    14: "STOP",
    34: "LEFT",
    33: "RIGHT"
}

np.random.seed(42)
tf.random.set_seed(42)


# ==========================================
# 2. CHARGEMENT DES IMAGES
# ==========================================

def load_dataset():

    images = []
    labels = []

    print("\nChargement des images...")

    for class_id, class_name in CLASSES.items():

        folder = DATASET_DIR / f"{class_id:05d}"
        csv_path = folder / f"GT-{class_id:05d}.csv"

        if not folder.exists() or not csv_path.exists():
            raise FileNotFoundError(
                f"Dossier ou CSV introuvable : {folder}"
            )

        data = pd.read_csv(csv_path, sep=";")

        print(f"\nClasse {class_name}")

        for _, row in data.iterrows():

            image_path = folder / row["Filename"]

            image = cv2.imread(str(image_path))

            if image is None:
                continue

            # Coordonnées de la zone du panneau
            x1 = int(row["Roi.X1"])
            y1 = int(row["Roi.Y1"])
            x2 = int(row["Roi.X2"])
            y2 = int(row["Roi.Y2"])

            height, width = image.shape[:2]

            # Vérification des coordonnées
            x1 = max(0, min(x1, width - 1))
            x2 = max(x1 + 1, min(x2, width))

            y1 = max(0, min(y1, height - 1))
            y2 = max(y1 + 1, min(y2, height))

            # Recadrage du panneau
            image = image[y1:y2, x1:x2]

            if image.size == 0:
                continue

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

            images.append(image)
            labels.append(list(CLASSES.keys()).index(class_id))

        print(
            f"Images chargees : "
            f"{labels.count(list(CLASSES.keys()).index(class_id))}"
        )

    X = np.array(images, dtype=np.uint8)
    y = np.array(labels, dtype=np.int32)

    return X, y


# ==========================================
# 3. PREPARATION DES DONNEES
# ==========================================

print("===================================")
print("       ORION-ROVER CNN")
print("===================================")

X, y = load_dataset()

if len(X) == 0:
    raise ValueError("Aucune image chargee.")

print("\nNombre total d'images :", len(X))

# 70 % entrainement, 15 % validation, 15 % test
X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)

print("\nRepartition des donnees :")
print("Entrainement :", len(X_train))
print("Validation :", len(X_val))
print("Test :", len(X_test))


# ==========================================
# 4. EQUILIBRAGE DES CLASSES
# ==========================================

weights = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(y_train),
    y=y_train
)

class_weights = {
    int(index): float(weight)
    for index, weight in enumerate(weights)
}


# ==========================================
# 5. CONSTRUCTION DU CNN
# ==========================================

print("\nConstruction du modele CNN...")

model = tf.keras.Sequential([

    tf.keras.layers.Input(
        shape=(IMAGE_SIZE, IMAGE_SIZE, 3)
    ),

    tf.keras.layers.Rescaling(1.0 / 255),

    # Augmentation legere sans inversion gauche/droite
    tf.keras.layers.RandomRotation(0.03),
    tf.keras.layers.RandomContrast(0.10),

    tf.keras.layers.Conv2D(
        32, (3, 3), activation="relu"
    ),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(
        64, (3, 3), activation="relu"
    ),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(
        128, (3, 3), activation="relu"
    ),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Flatten(),

    tf.keras.layers.Dense(
        128, activation="relu"
    ),

    tf.keras.layers.Dropout(0.40),

    tf.keras.layers.Dense(
        len(CLASSES), activation="softmax"
    )
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()


# ==========================================
# 6. ENTRAINEMENT
# ==========================================

callbacks = [

    tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=4,
        restore_best_weights=True
    ),

    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=2,
        min_lr=0.00001
    )
]

print("\nDebut de l'entrainement...")

history = model.fit(
    X_train,
    y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    class_weight=class_weights,
    callbacks=callbacks,
    verbose=1
)


# ==========================================
# 7. EVALUATION FINALE
# ==========================================

print("\nEvaluation sur les images de test...")

test_loss, test_accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=0
)

predictions = model.predict(
    X_test,
    batch_size=BATCH_SIZE,
    verbose=0
)

predicted_classes = np.argmax(
    predictions,
    axis=1
)

class_names = list(CLASSES.values())

print("\n===================================")
print("       RESULTATS DU CNN")
print("===================================")

print(f"Test accuracy : {test_accuracy * 100:.2f}%")
print(f"Test loss : {test_loss:.4f}")

print("\nRapport de classification :")

print(
    classification_report(
        y_test,
        predicted_classes,
        labels=[0, 1, 2],
        target_names=class_names,
        zero_division=0
    )
)

print("\nMatrice de confusion :")

print(
    confusion_matrix(
        y_test,
        predicted_classes,
        labels=[0, 1, 2]
    )
)


# ==========================================
# 8. SAUVEGARDE DU MODELE
# ==========================================

model.save(MODEL_PATH)

with open(LABELS_PATH, "w", encoding="utf-8") as file:
    json.dump(
        {
            str(index): name
            for index, name in enumerate(class_names)
        },
        file,
        indent=4,
        ensure_ascii=False
    )

print("\n===================================")
print("ENTRAINEMENT TERMINE")
print("===================================")

print("Modele :", MODEL_PATH)
print("Classes :", LABELS_PATH)
print("Accuracy test :", round(test_accuracy * 100, 2), "%")
