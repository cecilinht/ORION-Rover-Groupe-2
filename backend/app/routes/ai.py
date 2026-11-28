import subprocess
import threading
import time
from flask import Blueprint, request, jsonify
from app.services.ai_service import predict_sign

ai_bp = Blueprint("ai", __name__)

_last_spoken_sign = ""
_last_spoken_time = 0.0

SIGN_PHRASES = {
    "STOP": "Attention, panneau Stop détecté.",
    "LEFT": "Panneau tourner à gauche.",
    "RIGHT": "Panneau tourner à droite.",
    "SLOW": "Ralentissement demandé.",
    "ARRIVAL": "Zone d'arrivée atteinte, livraison prête."
}

def speak_windows_async(text):
    def _run():
        try:
            ps_cmd = (
                "Add-Type -AssemblyName System.Speech; "
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$s.Rate = 1; "
                f"$s.Speak('{text}');"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()


@ai_bp.route("/api/ai/predict", methods=["POST"])
def predict():
    global _last_spoken_sign, _last_spoken_time

    if "image" not in request.files:
        return jsonify({"success": False, "message": "Aucune image envoyee"}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"success": False, "message": "Nom de fichier invalide"}), 400

    try:
        image_bytes = image_file.read()
        result = predict_sign(image_bytes)

        # Annonce vocale Windows hors-ligne si confiance >= 80% et panneau valide
        sign_class = result.get("class", "")
        confidence = float(result.get("confidence", 0))
        now = time.time()

        if sign_class in SIGN_PHRASES and confidence >= 65.0:
            if sign_class != _last_spoken_sign or (now - _last_spoken_time) >= 4.0:
                _last_spoken_sign = sign_class
                _last_spoken_time = now
                speak_windows_async(SIGN_PHRASES[sign_class])

        return jsonify({
            "success": True,
            "prediction": result
        }), 200

    except FileNotFoundError as error:
        return jsonify({"success": False, "message": str(error)}), 503
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Erreur pendant la reconnaissance IA",
            "details": str(error)
        }), 500
