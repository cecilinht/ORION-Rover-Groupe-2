
from flask import Flask, jsonify, render_template
from flask_cors import CORS

from app.routes.sensors import sensors_bp
from app.routes.robot import robot_bp
from app.routes.commands import commands_bp
from app.routes.navigation import navigation_bp
from app.routes.ai import ai_bp
from app.routes.video import video_bp


# Initialisation de Flask
app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

# Autoriser les requêtes entre différentes origines
CORS(app)


# Enregistrement des routes
app.register_blueprint(sensors_bp)
app.register_blueprint(robot_bp)
app.register_blueprint(commands_bp)
app.register_blueprint(navigation_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(video_bp)


# Page principale : tableau de bord
@app.route("/")
def home():
    return render_template("dashboard.html")


# Vérification du fonctionnement du backend
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "message": "ORION-Rover API fonctionne correctement"
    })


# Informations sur le projet
@app.route("/api/project", methods=["GET"])
def project():
    return jsonify({
        "project": "ORION-Rover",
        "group": "Groupe 2",
        "university": "ORION UNIVERSITY",
        "status": "Backend operationnel"
    })


# Démarrage du serveur
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
