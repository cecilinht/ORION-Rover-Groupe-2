
import sqlite3
from pathlib import Path
from datetime import datetime


# ==========================================
# CONFIGURATION DE LA BASE DE DONNEES
# ==========================================

DATABASE_PATH = Path(__file__).resolve().parents[2] / "orion_rover.db"


# ==========================================
# CONNEXION SQLITE
# ==========================================

def get_connection():

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# INITIALISATION DES TABLES
# ==========================================

def init_db():

    connection = get_connection()

    try:

        # Table des livraisons
        connection.execute("""
            CREATE TABLE IF NOT EXISTS deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)

        # Table des mesures des capteurs
        connection.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                front REAL,
                left_distance REAL,
                right_distance REAL,
                s1 INTEGER,
                s2 INTEGER,
                s3 INTEGER,
                s4 INTEGER,
                s5 INTEGER
            )
        """)

        # Table de l'historique de navigation
        connection.execute("""
            CREATE TABLE IF NOT EXISTS navigation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT,
                speed REAL,
                direction TEXT
            )
        """)

        connection.commit()

    finally:
        connection.close()


# ==========================================
# GESTION DES LIVRAISONS
# ==========================================

def create_delivery(destination):

    connection = get_connection()

    try:

        cursor = connection.execute("""
            INSERT INTO deliveries (
                destination,
                status,
                created_at
            )
            VALUES (?, ?, ?)
        """, (
            destination,
            "EN_COURS",
            datetime.now().isoformat()
        ))

        connection.commit()

        delivery_id = cursor.lastrowid

        return get_delivery_by_id(delivery_id)

    finally:
        connection.close()


def get_delivery_by_id(delivery_id):

    connection = get_connection()

    try:

        row = connection.execute("""
            SELECT * FROM deliveries
            WHERE id = ?
        """, (delivery_id,)).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


def get_current_delivery():

    connection = get_connection()

    try:

        row = connection.execute("""
            SELECT * FROM deliveries
            WHERE status = 'EN_COURS'
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


def get_delivery_history():

    connection = get_connection()

    try:

        rows = connection.execute("""
            SELECT * FROM deliveries
            WHERE status = 'TERMINEE'
            ORDER BY id DESC
        """).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def complete_delivery(delivery_id):

    connection = get_connection()

    try:

        connection.execute("""
            UPDATE deliveries
            SET status = ?,
                completed_at = ?
            WHERE id = ?
              AND status = 'EN_COURS'
        """, (
            "TERMINEE",
            datetime.now().isoformat(),
            delivery_id
        ))

        connection.commit()

        row = connection.execute("""
            SELECT * FROM deliveries
            WHERE id = ?
        """, (delivery_id,)).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


# ==========================================
# HISTORIQUE DES CAPTEURS
# ==========================================

def save_sensor_reading(data):

    ultrasonic = data.get("ultrasonic", {})
    infrared = data.get("infrared", {})

    connection = get_connection()

    try:

        connection.execute("""
            INSERT INTO sensor_readings (
                timestamp,
                front,
                left_distance,
                right_distance,
                s1,
                s2,
                s3,
                s4,
                s5
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            ultrasonic.get("front"),
            ultrasonic.get("left"),
            ultrasonic.get("right"),
            infrared.get("s1"),
            infrared.get("s2"),
            infrared.get("s3"),
            infrared.get("s4"),
            infrared.get("s5")
        ))

        connection.commit()

    finally:
        connection.close()


def get_sensor_history(limit=100):

    connection = get_connection()

    try:

        rows = connection.execute("""
            SELECT * FROM sensor_readings
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


# ==========================================
# HISTORIQUE DES DECISIONS DE NAVIGATION
# ==========================================

def save_navigation_decision(result):

    connection = get_connection()

    try:

        connection.execute("""
            INSERT INTO navigation_history (
                timestamp,
                decision,
                reason,
                speed,
                direction
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            result.get("decision"),
            result.get("reason"),
            result.get("speed"),
            result.get("direction")
        ))

        connection.commit()

    finally:
        connection.close()


def get_navigation_history(limit=100):

    connection = get_connection()

    try:

        rows = connection.execute("""
            SELECT * FROM navigation_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()
