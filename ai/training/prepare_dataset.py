
import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split

# ==========================================
# ORION-ROVER : PREPARATION DU DATASET IA
# ==========================================

# Chemin du dossier contenant les images
DATASET_DIR = "ai/dataset/raw"

# Taille standard des images
IMAGE_SIZE = 128

# Les 6 classes de panneaux
CLASSES = [
    "STOP",
    "LEFT",
    "RIGHT",
    "SLOW",
    "ARRIVAL",
    "NO_SIGN"
]

# Listes pour stocker les images et leurs etiquettes
images = []
labels = []

print("Preparation du dataset ORION-Rover...")

# Parcourir chaque classe
for label, class_name in enumerate(CLASSES):

    class_path = os.path.join(DATASET_DIR, class_name)

    if not os.path.exists(class_path):
        print("Dossier introuvable :", class_path)
        continue

    image_count = 0

    # Lire les images du dossier
    for filename in os.listdir(class_path):

        image_path = os.path.join(class_path, filename)

        # Lire l'image avec OpenCV
        image = cv2.imread(image_path)

        # Ignorer les fichiers qui ne sont pas des images valides
        if image is None:
            continue

        # Convertir BGR vers RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Redimensionner en 128 x 128
        image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE))

        # Ajouter l'image et son etiquette
        images.append(image)
        labels.append(label)

        image_count += 1

    print(class_name, ":", image_count, "images")

# Verifier si des images ont ete trouvees
if len(images) == 0:
    print("\nAucune image trouvee.")
    print("Ajoute des images dans les dossiers ai/dataset/raw.")
    raise SystemExit

# Convertir les listes en tableaux NumPy
X = np.array(images, dtype=np.float32)
y = np.array(labels, dtype=np.int32)

# Normaliser les pixels entre 0 et 1
X = X / 255.0

# Separaison entrainement / validation
# Stratify conserve les proportions de chaque classe
counts = np.bincount(y, minlength=len(CLASSES))
can_stratify = len(counts) > 1 and np.all(counts[counts > 0] >= 2)

if can_stratify:
    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
else:
    print("Attention : certaines classes ont moins de 2 images.")
    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

# Creer le dossier de sortie
OUTPUT_DIR = "ai/dataset/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sauvegarder les donnees preparees
np.savez_compressed(
    os.path.join(OUTPUT_DIR, "dataset.npz"),
    X_train=X_train,
    X_val=X_val,
    y_train=y_train,
    y_val=y_val,
    class_names=np.array(CLASSES)
)

print("\nPreparation terminee !")
print("Images totales :", len(X))
print("Images entrainement :", len(X_train))
print("Images validation :", len(X_val))
print("Fichier cree : ai/dataset/processed/dataset.npz")
