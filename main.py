from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DB_NAME = "devices.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/api/devices", methods=["POST"])
def create_device():
    data = request.get_json()

    employee_id = data.get("employee_id")
    device_id = data.get("device_id")

    if not employee_id or not device_id:
        return jsonify({"status": "error", "message": "employee_id dan device_id wajib diisi"}), 400

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO devices (employee_id, device_id, created_at) VALUES (?, ?, ?)",
        (employee_id, device_id, created_at)
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "id": new_id,
            "employee_id": employee_id,
            "device_id": device_id,
            "created_at": created_at
        }
    }), 201

@app.route("/api/devices", methods=["GET"])
def get_latest_device():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM devices
        ORDER BY created_at DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row:
        data = dict(row)
        created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M:%S")
        now = datetime.now()

        # hanya ambil data 5 detik terakhir
        if (now - created_at) <= timedelta(seconds=5):
            return jsonify({"data": data})

    # jika kosong atau lebih dari 5 detik, kembalikan JSON kosong
    return jsonify({})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6100, debug=True)