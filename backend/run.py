
from flask import Flask, jsonify

from app.routes.sensors import sensors_bp
from app.routes.robot import robot_bp
from app.routes.commands import commands_bp


app = Flask(__name__)

# Enregistrer les routes
app.register_blueprint(sensors_bp)
app.register_blueprint(robot_bp)
app.register_blueprint(commands_bp)


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "Bienvenue sur le backend ORION-Rover"
    })


@app.route("/api/health")
def health():
    return jsonify({
        "success": True,
        "message": "Le serveur ORION-Rover fonctionne correctement"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
