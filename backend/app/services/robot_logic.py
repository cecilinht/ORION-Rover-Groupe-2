
# ORION-ROVER
# MODULE INTELLIGENT DE NAVIGATION ET DE SECURITE

DISTANCE_SAFE = 40
DISTANCE_DANGER = 15
MAX_DISTANCE = 400


def stop_robot(reason):
    return {
        "decision": "STOP",
        "reason": reason,
        "speed": 0,
        "direction": "NONE"
    }


def validate_distance(value):

    if value is None or isinstance(value, bool):
        return False

    try:
        distance = float(value)
    except (ValueError, TypeError):
        return False

    if not 0 <= distance <= MAX_DISTANCE:
        return False

    if distance != distance:
        return False

    if distance == float("inf") or distance == float("-inf"):
        return False

    return True


def analyze_obstacles(sensor_data):

    if not isinstance(sensor_data, dict):
        return stop_robot("Structure des capteurs invalide")

    ultrasonic = sensor_data.get("ultrasonic")

    if not isinstance(ultrasonic, dict):
        return stop_robot("Donnees ultrasoniques indisponibles")

    required_sensors = ["front", "left", "right"]
    distances = {}

    for sensor in required_sensors:

        if sensor not in ultrasonic:
            return stop_robot("Capteur manquant : " + sensor)

        value = ultrasonic[sensor]

        if not validate_distance(value):
            return stop_robot("Mesure invalide : " + sensor)

        distances[sensor] = float(value)

    front = distances["front"]
    left = distances["left"]
    right = distances["right"]

    # Chemin libre
    if front > DISTANCE_SAFE:
        return {
            "decision": "FORWARD",
            "reason": "Chemin libre",
            "speed": 100,
            "direction": "FORWARD"
        }

    # Obstacle a distance moyenne
    if front >= DISTANCE_DANGER:
        return {
            "decision": "SLOW",
            "reason": "Obstacle detecte devant",
            "speed": 40,
            "direction": "FORWARD"
        }

    # Recherche d'un passage securise
    left_is_safe = left > DISTANCE_SAFE
    right_is_safe = right > DISTANCE_SAFE

    if left_is_safe and not right_is_safe:
        return {
            "decision": "AVOID",
            "reason": "Passage securise a gauche",
            "speed": 35,
            "direction": "LEFT"
        }

    if right_is_safe and not left_is_safe:
        return {
            "decision": "AVOID",
            "reason": "Passage securise a droite",
            "speed": 35,
            "direction": "RIGHT"
        }

    if left_is_safe and right_is_safe:

        if left > right:
            return {
                "decision": "AVOID",
                "reason": "Passage plus large a gauche",
                "speed": 35,
                "direction": "LEFT"
            }

        if right > left:
            return {
                "decision": "AVOID",
                "reason": "Passage plus large a droite",
                "speed": 35,
                "direction": "RIGHT"
            }

    return stop_robot("Aucun passage securise")
