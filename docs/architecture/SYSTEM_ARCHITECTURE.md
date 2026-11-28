
# ORION-Rover — Architecture du système

## 1. Présentation

ORION-Rover est un robot mobile autonome conçu pour effectuer des livraisons sur le campus universitaire.

## 2. Architecture générale

Le système est organisé en trois parties :

### ESP32 — Commande embarquée
- Lecture des capteurs ultrasoniques HC-SR04.
- Lecture de la barrette infrarouge 5 voies.
- Commande des deux moteurs DC via le driver L298N.
- Gestion des états du robot.
- Communication Wi-Fi avec le serveur.

### Serveur informatique — Traitement
- Serveur Python Flask.
- Traitement des commandes de livraison.
- Gestion des données des capteurs.
- Traitement de l'intelligence artificielle.
- Stockage des informations.

### Interface web — Supervision
- Affichage de l'état du robot.
- Visualisation des distances.
- Commandes de démarrage et d'arrêt.
- Affichage de la trajectoire.
- Historique des livraisons.

## 3. Communication

L'ESP32 et le serveur communiquent par Wi-Fi sur le réseau local.

Le protocole HTTP sera utilisé pour les échanges avec l'API Flask. Une communication en temps réel pourra être ajoutée ultérieurement.

## 4. États du robot

- ATTENTE
- ROUTE
- ÉVITEMENT
- LIVRAISON
- RETOUR
- ARRÊT D'URGENCE

## 5. Sécurité

Le robot doit s'arrêter lorsqu'un obstacle est détecté à une distance inférieure à 15 cm.

Les moteurs et la logique électronique doivent utiliser des alimentations adaptées.
