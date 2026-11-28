
from flask import Blueprint, request, jsonify

from app.services.ai_service import predict_sign

# ==========================================
# ORION-ROVER : ROUTE API DE RECONNAISSANCE
# ==========================================

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai/predict", methods=["POST"])
def predict():

    # Verifier si une image est presente
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "Aucune image envoyee"
        }), 400

    image_file = request.files["image"]

    if image_file.filename == "":
        return jsonify({
            "success": False,
            "message": "Nom de fichier invalide"
        }), 400

    try:
        # Lire les donnees de l'image
        image_bytes = image_file.read()

        # Appeler le service IA
        result = predict_sign(image_bytes)

        return jsonify({
            "success": True,
            "prediction": result
        }), 200

    except FileNotFoundError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 503

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Erreur pendant la reconnaissance IA",
            "details": str(error)
        }), 500
