
from flask import Blueprint, request, jsonify

from app.services.database import (
    init_db,
    create_delivery,
    get_current_delivery,
    get_delivery_history,
    complete_delivery
)

commands_bp = Blueprint("commands", __name__)

# Initialiser la base de donnees
init_db()


# Creer une nouvelle commande de livraison
@commands_bp.route("/api/command", methods=["POST"])
def create_command():

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

    # Verifier si une livraison est deja en cours
    current = get_current_delivery()

    if current is not None:
        return jsonify({
            "success": False,
            "message": "Une livraison est deja en cours"
        }), 409

    # Enregistrer la livraison dans SQLite
    delivery = create_delivery(destination.strip())

    return jsonify({
        "success": True,
        "message": "Commande de livraison creee",
        "data": delivery
    }), 201


# Consulter les livraisons
@commands_bp.route("/api/deliveries", methods=["GET"])
def get_deliveries():

    return jsonify({
        "success": True,
        "current_delivery": get_current_delivery(),
        "history": get_delivery_history()
    })


# Terminer une livraison
@commands_bp.route("/api/delivery/complete", methods=["POST"])
def finish_delivery():

    current = get_current_delivery()

    if current is None:
        return jsonify({
            "success": False,
            "message": "Aucune livraison en cours"
        }), 404

    delivery = complete_delivery(current["id"])

    return jsonify({
        "success": True,
        "message": "Livraison terminee",
        "data": delivery
    })
