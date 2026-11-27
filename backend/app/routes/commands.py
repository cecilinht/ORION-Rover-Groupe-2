
from flask import Blueprint, request, jsonify
from datetime import datetime

commands_bp = Blueprint("commands", __name__)

delivery_history = []
current_delivery = None


# Envoyer une nouvelle commande de livraison
@commands_bp.route("/api/command", methods=["POST"])
def create_command():

    global current_delivery

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "JSON invalide"
        }), 400

    destination = data.get("destination")

    if not isinstance(destination, str) or not destination.strip():
        return jsonify({
            "success": False,
            "message": "Destination obligatoire"
        }), 400

    if current_delivery is not None:
        return jsonify({
            "success": False,
            "message": "Une livraison est deja en cours"
        }), 409

    current_delivery = {
        "id": len(delivery_history) + 1,
        "destination": destination.strip(),
        "status": "EN_COURS",
        "created_at": datetime.now().isoformat()
    }

    return jsonify({
        "success": True,
        "message": "Commande de livraison creee",
        "data": current_delivery
    }), 201


# Consulter les livraisons
@commands_bp.route("/api/deliveries", methods=["GET"])
def get_deliveries():

    return jsonify({
        "success": True,
        "current_delivery": current_delivery,
        "history": delivery_history
    })


# Terminer une livraison
@commands_bp.route("/api/delivery/complete", methods=["POST"])
def complete_delivery():

    global current_delivery

    if current_delivery is None:
        return jsonify({
            "success": False,
            "message": "Aucune livraison en cours"
        }), 404

    current_delivery["status"] = "TERMINEE"
    current_delivery["completed_at"] = datetime.now().isoformat()

    delivery_history.append(current_delivery.copy())

    completed_delivery = current_delivery
    current_delivery = None

    return jsonify({
        "success": True,
        "message": "Livraison terminee",
        "data": completed_delivery
    })
