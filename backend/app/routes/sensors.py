import time
esp32_heartbeat = {'last_seen': 0.0, 'ip': None}

from flask import Blueprint, request, jsonify

from app.services.database import (
    save_sensor_reading,
    get_sensor_history
)

sensors_bp = Blueprint("sensors", __name__)

sensor_data = {
    "ultrasonic": {
        "front": None,
        "left": None,
        "right": None
    },
    "infrared": {
        "s1": None,
        "s2": None,
        "s3": None,
        "s4": None,
        "s5": None
    }
}


# Recevoir les donnees des capteurs
@sensors_bp.route("/api/sensors", methods=["POST"])
def receive_sensors():

    global sensor_data

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "JSON invalide"
        }), 400

    if "ultrasonic" in data:

        if not isinstance(data["ultrasonic"], dict):
            return jsonify({
                "success": False,
                "message": "Donnees ultrasoniques invalides"
            }), 400

        for key, value in data["ultrasonic"].items():

            if key not in ["front", "left", "right"]:
                return jsonify({
                    "success": False,
                    "message": "Capteur ultrasonique inconnu"
                }), 400

            if value is not None:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    return jsonify({
                        "success": False,
                        "message": "Distance invalide"
                    }), 400

                if not 0 <= value <= 400:
                    return jsonify({
                        "success": False,
                        "message": "Distance hors limites"
                    }), 400

            sensor_data["ultrasonic"][key] = value

    if "infrared" in data:

        if not isinstance(data["infrared"], dict):
            return jsonify({
                "success": False,
                "message": "Donnees infrarouges invalides"
            }), 400

        for key, value in data["infrared"].items():

            if key not in ["s1", "s2", "s3", "s4", "s5"]:
                return jsonify({
                    "success": False,
                    "message": "Capteur infrarouge inconnu"
                }), 400

            if value not in [0, 1]:
                return jsonify({
                    "success": False,
                    "message": "Valeur infrarouge invalide"
                }), 400

            sensor_data["infrared"][key] = value

    # Enregistrer les mesures dans SQLite
    save_sensor_reading(sensor_data)

    return jsonify({
        "success": True,
        "message": "Donnees des capteurs recues et enregistrees",
        "data": sensor_data
    })


# Consulter les dernieres donnees
@sensors_bp.route("/api/sensors", methods=["GET"])
def get_sensors():

    return jsonify({
        "success": True,
        "data": sensor_data
    })


# Consulter l'historique des mesures
@sensors_bp.route("/api/sensors/history", methods=["GET"])
def sensor_history():

    history = get_sensor_history()

    return jsonify({
        "success": True,
        "count": len(history),
        "history": history
    })
