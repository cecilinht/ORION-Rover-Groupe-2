
from flask import Blueprint, jsonify, request

from app.services.robot_logic import analyze_obstacles
from app.services.database import (
    save_navigation_decision,
    get_navigation_history
)

from app.routes.sensors import sensor_data
from app.routes.robot import robot_state


navigation_bp = Blueprint("navigation", __name__)


@navigation_bp.route("/api/navigation/decision", methods=["GET", "POST"])
def navigation_decision():

    # Recuperer les donnees des capteurs
    if request.method == "POST":

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "message": "JSON invalide"
            }), 400

    else:
        data = sensor_data

    # Verifier l'arret d'urgence
    if robot_state["emergency_stop"]:

        result = {
            "decision": "STOP",
            "reason": "Arret d'urgence actif",
            "speed": 0,
            "direction": "NONE"
        }

    else:

        # Analyser les obstacles
        result = analyze_obstacles(data)

    # Enregistrer uniquement les decisions envoyees en POST
    if request.method == "POST":
        save_navigation_decision(result)

    # Recuperer les distances ultrasoniques
    ultrasonic = data.get("ultrasonic", {})

    return jsonify({
        "success": True,
        "message": "Analyse de navigation terminee",

        "robot": {
            "status": robot_state["status"],
            "connected": robot_state["connected"],
            "emergency_stop": robot_state["emergency_stop"]
        },

        "sensors": {
            "ultrasonic": ultrasonic,
            "infrared": data.get("infrared", {})
        },

        "decision": result
    })


# Consulter l'historique des decisions
@navigation_bp.route("/api/navigation/history", methods=["GET"])
def navigation_history():

    history = get_navigation_history()

    return jsonify({
        "success": True,
        "count": len(history),
        "history": history
    })
