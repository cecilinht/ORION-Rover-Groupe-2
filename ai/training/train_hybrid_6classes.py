import json
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight

BASE_DIR = Path(__file__).resolve().parent.parent.parent
GTSRB_DIR = BASE_DIR / "ai" / "dataset" / "raw" / "GTSRB" / "GTSRB" / "Final_Training" / "Images"
CUSTOM_DIR = BASE_DIR / "ai" / "dataset" / "custom"
MODEL_DIR = BASE_DIR / "ai" / "models"
EVAL_DIR = BASE_DIR / "ai" / "evaluation"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "orion_rover_first_cnn.keras"
LABELS_PATH = MODEL_DIR / "orion_rover_first_labels.json"
REPORT_PATH = EVAL_DIR / "rapport_evaluation_hybride_6classes.txt"

CLASSES = ["STOP", "LEFT", "RIGHT", "SLOW", "ARRIVAL", "NO_SIGN"]
GTSRB_MAP = {
    "STOP": 14,
    "LEFT": 34,
    "RIGHT": 33,
    "SLOW": 18  # Panneau triangle danger / ralentir dans GTSRB
}
MAX_GTSRB_PER_CLASS = 400
IMAGE_SIZE = 128
BATCH_SIZE = 16
EPOCHS = 30

np.random.seed(42)
tf.random.set_seed(42)

def load_gtsrb_subset():
    images, labels = [], []
    if not GTSRB_DIR.exists():
        print("Dossier GTSRB introuvable, utilisation uniquement du dataset custom.")
        return images, labels

    for class_name, gtsrb_id in GTSRB_MAP.items():
        class_idx = CLASSES.index(class_name)
        folder = GTSRB_DIR / f"{gtsrb_id:05d}"
        csv_path = folder / f"GT-{gtsrb_id:05d}.csv"
        if not folder.exists() or not csv_path.exists():
            continue

        df = pd.read_csv(csv_path, sep=";").sample(frac=1, random_state=42).head(MAX_GTSRB_PER_CLASS)
        count = 0
        for _, row in df.iterrows():
            img = cv2.imread(str(folder / row["Filename"]))
            if img is None:
                continue
            h, w = img.shape[:2]
            x1 = max(0, min(int(row["Roi.X1"]), w - 1))
            x2 = max(x1 + 1, min(int(row["Roi.X2"]), w))
            y1 = max(0, min(int(row["Roi.Y1"]), h - 1))
            y2 = max(y1 + 1, min(int(row["Roi.Y2"]), h))
            crop = img[y1:y2, x1:x2]
            if crop.size == 0:
                continue
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            crop = cv2.resize(crop, (IMAGE_SIZE, IMAGE_SIZE))
            images.append(crop)
            labels.append(class_idx)
            count += 1
        print(f"[GTSRB]  {class_name:<8} : {count} images chargees")
    return images, labels

def load_custom_dataset():
    images, labels = [], []
    for class_idx, class_name in enumerate(CLASSES):
        folder = CUSTOM_DIR / class_name
        files = sorted(folder.glob("*.jpg"))
        count = 0
        for img_path in files:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (IMAGE_SIZE, IMAGE_SIZE))
            images.append(img)
            labels.append(class_idx)
            count += 1
        print(f"[CUSTOM] {class_name:<8} : {count} images chargees")
    return images, labels

print("=== ENTRAINEMENT HYBRIDE (GTSRB + WEBCAM) - 6 CLASSES ===")
X_g, y_g = load_gtsrb_subset()
X_c, y_c = load_custom_dataset()

X = np.array(X_g + X_c, dtype=np.uint8)
y = np.array(y_g + y_c, dtype=np.int32)
print(f"\nTotal combine : {len(X)} images")

X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

weights = compute_class_weight(class_weight="balanced", classes=np.unique(y_train), y=y_train)
class_weights = {int(i): float(w) for i, w in enumerate(weights)}

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3)),
    tf.keras.layers.Rescaling(1.0 / 255),

    tf.keras.layers.RandomRotation(0.04),
    tf.keras.layers.RandomZoom(0.08),
    tf.keras.layers.RandomBrightness(0.10, value_range=(0.0, 1.0)),
    tf.keras.layers.RandomContrast(0.10),

    tf.keras.layers.Conv2D(32, (3, 3), padding="same", activation="relu"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(64, (3, 3), padding="same", activation="relu"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(128, (3, 3), padding="same", activation="relu"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(128, (3, 3), padding="same", activation="relu"),
    tf.keras.layers.GlobalAveragePooling2D(),

    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dropout(0.30),
    tf.keras.layers.Dense(len(CLASSES), activation="softmax")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5)
]

model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    class_weight=class_weights,
    callbacks=callbacks,
    verbose=1
)

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
preds = np.argmax(model.predict(X_test, batch_size=BATCH_SIZE, verbose=0), axis=1)

report_txt = classification_report(y_test, preds, target_names=CLASSES, digits=4, zero_division=0)
cm = confusion_matrix(y_test, preds)

summary = (
    f"=== EVALUATION CNN HYBRIDE ORION-ROVER (6 CLASSES) ===\n"
    f"Test Accuracy : {test_acc * 100:.2f}%\n"
    f"Test Loss     : {test_loss:.4f}\n\n"
    f"Rapport par classe :\n{report_txt}\n"
    f"Matrice de confusion (ordre: {CLASSES}) :\n{cm}\n"
)

print("\n" + summary)
REPORT_PATH.write_text(summary, encoding="utf-8")

model.save(MODEL_PATH)
LABELS_PATH.write_text(
    json.dumps({str(i): name for i, name in enumerate(CLASSES)}, indent=4, ensure_ascii=False),
    encoding="utf-8"
)
print(f"Modele sauvegarde : {MODEL_PATH}")
print(f"Rapport sauvegarde : {REPORT_PATH}")
