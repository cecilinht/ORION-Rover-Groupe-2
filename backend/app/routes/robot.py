import time
from app.routes.sensors import esp32_heartbeat

from flask import Blueprint, request, jsonify

robot_bp = Blueprint("robot", __name__)

robot_state = {
    "status": "ATTENTE",
    "connected": False,
    "emergency_stop": False,
    "current_mission": None
}


# Consulter l'etat du robot
@robot_bp.route("/api/status", methods=["GET"])
def get_status():

    return jsonify({
        "success": True,
        "esp32_connected": (time.time() - esp32_heartbeat["last_seen"]) < 5.0, "esp32_ip": esp32_heartbeat["ip"], "data": robot_state
    })


# Modifier l'etat du robot
@robot_bp.route("/api/robot", methods=["POST"])
def update_robot():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "JSON invalide"
        }), 400

    if robot_state["emergency_stop"]:
        return jsonify({
            "success": False,
            "message": "Arret d'urgence actif"
        }), 409

    if "status" in data:
        allowed_status = [
            "ATTENTE",
            "EN_MISSION",
            "LIVRAISON",
            "ERREUR"
        ]

        if data["status"] not in allowed_status:
            return jsonify({
                "success": False,
                "message": "Etat du robot invalide"
            }), 400

        robot_state["status"] = data["status"]

    if "connected" in data:
        if not isinstance(data["connected"], bool):
            return jsonify({
                "success": False,
                "message": "Valeur de connexion invalide"
            }), 400

        robot_state["connected"] = data["connected"]

    if "current_mission" in data:
        robot_state["current_mission"] = data["current_mission"]

    return jsonify({
        "success": True,
        "message": "Etat du robot mis a jour",
        "esp32_connected": (time.time() - esp32_heartbeat["last_seen"]) < 5.0, "esp32_ip": esp32_heartbeat["ip"], "data": robot_state
    })


# Activer l'arret d'urgence logiciel
@robot_bp.route("/api/emergency-stop", methods=["POST"])
def emergency_stop():

    robot_state["emergency_stop"] = True
    robot_state["status"] = "ERREUR"

    return jsonify({
        "success": True,
        "message": "Arret d'urgence logiciel active",
        "esp32_connected": (time.time() - esp32_heartbeat["last_seen"]) < 5.0, "esp32_ip": esp32_heartbeat["ip"], "data": robot_state
    })


# Reinitialiser l'arret d'urgence logiciel
@robot_bp.route("/api/emergency-reset", methods=["POST"])
def emergency_reset():

    robot_state["emergency_stop"] = False
    robot_state["status"] = "ATTENTE"

    return jsonify({
        "success": True,
        "message": "Arret d'urgence logiciel reinitialise",
        "esp32_connected": (time.time() - esp32_heartbeat["last_seen"]) < 5.0, "esp32_ip": esp32_heartbeat["ip"], "data": robot_state
    })
