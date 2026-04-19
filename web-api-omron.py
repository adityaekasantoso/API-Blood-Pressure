from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
from datetime import datetime, timedelta
import configparser
import os

app = Flask(__name__)
CORS(app)

config = configparser.ConfigParser()

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.ini")

if not os.path.exists(CONFIG_PATH):
    raise Exception("config.ini tidak ditemukan")

config.read(CONFIG_PATH, encoding="utf-8")

if "DATABASE_MAIN" not in config.sections():
    raise Exception("Section DATABASE_MAIN tidak ditemukan")

DB_CONFIG = {
    "server": config.get("DATABASE_MAIN", "server"),
    "database": config.get("DATABASE_MAIN", "database"),
    "username": config.get("DATABASE_MAIN", "user"),
    "password": config.get("DATABASE_MAIN", "password"),
    "driver": config.get("DATABASE_MAIN", "driver"),
}

def get_db_connection():
    conn_str = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

@app.route("/api/devices", methods=["POST"])
def create_device():
    data = request.get_json()

    employee_id = data.get("employee_id")
    device_id = data.get("device_id")

    if not employee_id or not device_id:
        return jsonify({"status": "error"}), 400

    created_at = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO devices (employee_id, device_id, created_at)
        VALUES (?, ?, ?)
    """, (employee_id, device_id, created_at))

    conn.commit()

    cursor.execute("SELECT SCOPE_IDENTITY()")
    new_id = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "id": new_id,
            "employee_id": employee_id,
            "device_id": device_id,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201

@app.route("/api/devices", methods=["GET"])
def get_latest_device():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 1 id, employee_id, device_id, created_at
        FROM devices
        ORDER BY created_at DESC
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({})

    data = {
        "id": row[0],
        "employee_id": row[1],
        "device_id": row[2],
        "created_at": row[3].strftime("%Y-%m-%d %H:%M:%S")
    }

    created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M:%S")

    if (datetime.now() - created_at) <= timedelta(seconds=5):
        return jsonify({"data": data})

    return jsonify({})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)