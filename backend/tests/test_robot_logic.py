
from app.services.robot_logic import analyze_obstacles


# TEST 1 : Chemin libre
def test_chemin_libre():
    sensors = {
        "ultrasonic": {
            "front": 80,
            "left": 60,
            "right": 50
        }
    }

    result = analyze_obstacles(sensors)

    assert result["decision"] == "FORWARD"
    assert result["speed"] == 100


# TEST 2 : Obstacle a distance moyenne
def test_obstacle_moyen():
    sensors = {
        "ultrasonic": {
            "front": 30,
            "left": 60,
            "right": 50
        }
    }

    result = analyze_obstacles(sensors)

    assert result["decision"] == "SLOW"
    assert result["speed"] == 40


# TEST 3 : Passage libre a gauche
def test_passage_gauche():
    sensors = {
        "ultrasonic": {
            "front": 10,
            "left": 70,
            "right": 30
        }
    }

    result = analyze_obstacles(sensors)

    assert result["decision"] == "AVOID"
    assert result["direction"] == "LEFT"


# TEST 4 : Aucun passage securise
def test_aucun_passage():
    sensors = {
        "ultrasonic": {
            "front": 10,
            "left": 20,
            "right": 25
        }
    }

    result = analyze_obstacles(sensors)

    assert result["decision"] == "STOP"
    assert result["speed"] == 0


# TEST 5 : Capteur avant indisponible
def test_capteur_indisponible():
    sensors = {
        "ultrasonic": {
            "front": None,
            "left": 60,
            "right": 50
        }
    }

    result = analyze_obstacles(sensors)

    assert result["decision"] == "STOP"
    assert result["speed"] == 0


# TEST 6 : Distance negative
def test_distance_negative():
    sensors = {
        "ultrasonic": {
            "front": -10,
            "left": 60,
            "right": 50
        }
    }

    result = analyze_obstacles(sensors)

    assert result["decision"] == "STOP"
    assert result["speed"] == 0


# TEST 7 : Distance superieure a 400 cm
def test_distance_superieure_limite():
    sensors = {
        "ultrasonic": {
            "front": 500,
            "left": 60,
            "right": 50
        }
    }

    result = analyze_obstacles(sensors)

    assert result["decision"] == "STOP"
    assert result["speed"] == 0


# TEST 8 : Capteur gauche manquant
def test_capteur_gauche_manquant():
    sensors = {
        "ultrasonic": {
            "front": 80,
            "right": 50
        }
    }

    result = analyze_obstacles(sensors)

    assert result["decision"] == "STOP"
    assert result["speed"] == 0


# TEST 9 : Mesure NaN
def test_mesure_nan():
    sensors = {
        "ultrasonic": {
            "front": float("nan"),
            "left": 60,
            "right": 50
        }
    }

    result = analyze_obstacles(sensors)

    assert result["decision"] == "STOP"
    assert result["speed"] == 0
