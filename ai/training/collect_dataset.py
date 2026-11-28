import time
from pathlib import Path
import cv2

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_DIR = BASE_DIR / "ai" / "dataset" / "custom"

CLASSES = ["STOP", "LEFT", "RIGHT", "SLOW", "ARRIVAL", "NO_SIGN"]
TARGET_COUNT = 220  # > 200 images par classe comme exige par le reglement
IMAGE_SIZE = 128

def extract_center_square(frame):
    h, w = frame.shape[:2]
    size = min(h, w)
    x1 = (w - size) // 2
    y1 = (h - size) // 2
    crop = frame[y1:y1 + size, x1:x1 + size]
    return cv2.resize(crop, (IMAGE_SIZE, IMAGE_SIZE)), (x1, y1, size)

def main():
    for c in CLASSES:
        (DATASET_DIR / c).mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erreur : impossible d'ouvrir la webcam.")
        return

    current_idx = 0
    capturing = False
    last_save = 0.0

    print("=== COLLECTE DATASET ORION-ROVER (6 CLASSES) ===")
    print("Touches :")
    print("  [ESPACE] : Demarrer / Mettre en pause la capture auto")
    print("  [N]      : Classe suivante")
    print("  [P]      : Classe precedente")
    print("  [Q]      : Quitter")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_class = CLASSES[current_idx]
        class_dir = DATASET_DIR / current_class
        existing = len(list(class_dir.glob("*.jpg")))

        square_img, (x1, y1, size) = extract_center_square(frame)

        # Capture automatique toutes les 0.12s (env. 8 images/sec -> 220 images en 27s)
        if capturing and (time.time() - last_save) >= 0.12:
            if existing < TARGET_COUNT:
                filename = class_dir / f"{current_class.lower()}_{int(time.time() * 1000)}.jpg"
                cv2.imwrite(str(filename), square_img)
                existing += 1
                last_save = time.time()
            else:
                capturing = False

        # Affichage interface
        display = frame.copy()
        color = (0, 255, 0) if capturing else (0, 165, 255)
        cv2.rectangle(display, (x1, y1), (x1 + size, y1 + size), color, 2)

        status = "CAPTURE EN COURS..." if capturing else "PAUSE (Appuyez sur ESPACE)"
        cv2.putText(display, f"Classe [{current_idx+1}/6]: {current_class} ({existing}/{TARGET_COUNT})",
                    (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(display, status, (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("ORION-Rover - Collecte Dataset", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):
            capturing = not capturing
        elif key == ord("n"):
            capturing = False
            current_idx = (current_idx + 1) % len(CLASSES)
        elif key == ord("p"):
            capturing = False
            current_idx = (current_idx - 1) % len(CLASSES)
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\nBilan du dataset :")
    for c in CLASSES:
        count = len(list((DATASET_DIR / c).glob("*.jpg")))
        print(f"  - {c}: {count} images")

if __name__ == "__main__":
    main()
