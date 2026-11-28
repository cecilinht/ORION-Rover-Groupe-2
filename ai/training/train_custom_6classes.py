import json
from pathlib import Path
import cv2
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_DIR = BASE_DIR / "ai" / "dataset" / "custom"
MODEL_DIR = BASE_DIR / "ai" / "models"
EVAL_DIR = BASE_DIR / "ai" / "evaluation"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "orion_rover_first_cnn.keras"
LABELS_PATH = MODEL_DIR / "orion_rover_first_labels.json"
REPORT_PATH = EVAL_DIR / "rapport_evaluation_6classes.txt"

CLASSES = ["STOP", "LEFT", "RIGHT", "SLOW", "ARRIVAL", "NO_SIGN"]
IMAGE_SIZE = 128
BATCH_SIZE = 16
EPOCHS = 20

np.random.seed(42)
tf.random.set_seed(42)

def load_custom_dataset():
    images, labels = [], []
    for idx, class_name in enumerate(CLASSES):
        folder = DATASET_DIR / class_name
        files = sorted(folder.glob("*.jpg"))
        print(f"Chargement {class_name:<8} : {len(files)} images")
        for img_path in files:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (IMAGE_SIZE, IMAGE_SIZE))
            images.append(img)
            labels.append(idx)
    return np.array(images, dtype=np.uint8), np.array(labels, dtype=np.int32)

print("=== ENTRAINEMENT CNN ORION-ROVER (6 CLASSES) ===")
X, y = load_custom_dataset()
print(f"\nTotal images chargees : {len(X)}")

# 70% train, 15% validation, 15% test
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3)),
    tf.keras.layers.Rescaling(1.0 / 255),

    # Data Augmentation adaptee (pas de flip horizontal !)
    tf.keras.layers.RandomRotation(0.05),
    tf.keras.layers.RandomZoom(0.10),
    tf.keras.layers.RandomBrightness(0.15),
    tf.keras.layers.RandomContrast(0.15),

    tf.keras.layers.Conv2D(32, (3, 3), activation="relu"),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(128, (3, 3), activation="relu"),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.40),
    tf.keras.layers.Dense(len(CLASSES), activation="softmax")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-5)
]

model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1
)

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
preds = np.argmax(model.predict(X_test, batch_size=BATCH_SIZE, verbose=0), axis=1)

report_txt = classification_report(y_test, preds, target_names=CLASSES, digits=4)
cm = confusion_matrix(y_test, preds)

summary = (
    f"=== EVALUATION CNN ORION-ROVER (6 CLASSES) ===\n"
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
