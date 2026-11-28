
import run


def test_arret_urgence_prioritaire():

    client = run.app.test_client()

    # Activer l'arret d'urgence
    response = client.post("/api/emergency-stop")

    assert response.status_code == 200

    # Envoyer des donnees indiquant un chemin libre
    response = client.post(
        "/api/sensors",
        json={
            "ultrasonic": {
                "front": 100,
                "left": 80,
                "right": 80
            },
            "infrared": {
                "s1": 0,
                "s2": 0,
                "s3": 1,
                "s4": 0,
                "s5": 0
            }
        }
    )

    assert response.status_code == 200

    # Demander une decision de navigation
    response = client.get("/api/navigation/decision")

    result = response.get_json()

    assert result["success"] is True
    assert result["decision"]["decision"] == "STOP"
    assert result["decision"]["speed"] == 0

    # Reinitialiser l'arret d'urgence
    client.post("/api/emergency-reset")
