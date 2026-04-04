"""
Flask API for ACEest Fitness & Gym.
Converted from Tkinter desktop app to REST API with Swagger UI.
"""
from flask import Flask, request, jsonify
from flasgger import Swagger
import sqlite3
import os
from datetime import datetime

DB_NAME = os.environ.get("FLASK_DB_NAME", "aceest_fitness.db")
app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "swagger",
            "route": "/swagger.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "ACEest Fitness & Gym",
        "description": "API for accessing fitness programs, workouts, and nutrition plans.",
        "version": "1.0.0"}}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# ------------------ Database ------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            weight REAL,
            program TEXT,
            calories INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------ Programs ------------------
programs = {
    "Fat Loss (FL)": {"factor": 22},
    "Muscle Gain (MG)": {"factor": 35},
    "Beginner (BG)": {"factor": 26}
}

# ------------------ Routes ------------------
@app.route("/")
def home():
    """
    Home endpoint
    ---
    responses:
      200:
        description: API is running
        schema:
          type: object
          properties:
            message:
              type: string
              example: ACEest Fitness & Gym API Running
    """
    return jsonify({"message": "ACEest Fitness & Gym API Running"})


@app.route("/programs", methods=["GET"])
def get_programs():
    """
    Get all program names
    ---
    responses:
      200:
        description: List of available programs
        schema:
          type: array
          items:
            type: string
            example: ["Fat Loss (FL)", "Muscle Gain (MG)", "Beginner (BG)"]
    """
    return jsonify(list(programs.keys()))


@app.route("/client", methods=["POST"])
def save_client():
    """
    Save a client profile
    ---
    parameters:
      - in: body
        name: client
        required: true
        schema:
          type: object
          required:
            - name
            - program
          properties:
            name:
              type: string
            age:
              type: integer
            weight:
              type: number
            program:
              type: string
    responses:
      200:
        description: Client saved successfully
      400:
        description: Missing or invalid data
      415:
        description: Request must be JSON
      500:
        description: Database error
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON with Content-Type 'application/json'"}), 415

    data = request.get_json()
    name = data.get("name")
    age = data.get("age")
    weight = data.get("weight")
    program = data.get("program")

    if not name or not program or program not in programs:
        return jsonify({"error": "Name and valid Program required"}), 400

    calories = int(weight * programs[program]["factor"]) if weight else None

    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO clients (name, age, weight, program, calories)
            VALUES (?, ?, ?, ?, ?)
        """, (name, age, weight, program, calories))
        conn.commit()
        conn.close()
        return jsonify({"message": "Client saved", "calories": calories})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/client/<name>", methods=["GET"])
def load_client(name):
    """
    Get client profile by name
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
    responses:
      200:
        description: Client data
        schema:
          type: object
          properties:
            name:
              type: string
            age:
              type: integer
            weight:
              type: number
            program:
              type: string
            calories:
              type: integer
      404:
        description: Client not found
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE name=?", (name,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Client not found"}), 404

    _, name, age, weight, program, calories = row
    return jsonify({
        "name": name,
        "age": age,
        "weight": weight,
        "program": program,
        "calories": calories
    })


@app.route("/progress", methods=["POST"])
def save_progress():
    """
    Save weekly adherence for a client
    ---
    parameters:
      - in: body
        name: progress
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
            adherence:
              type: integer
    responses:
      200:
        description: Progress saved
      415:
        description: Request must be JSON
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON with Content-Type 'application/json'"}), 415

    data = request.get_json()
    name = data.get("name")
    adherence = data.get("adherence", 0)
    week = datetime.now().strftime("Week %U - %Y")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO progress (client_name, week, adherence)
        VALUES (?, ?, ?)
    """, (name, week, adherence))
    conn.commit()
    conn.close()

    return jsonify({"message": "Progress saved", "week": week, "adherence": adherence})


@app.route("/progress/<name>", methods=["GET"])
def get_progress(name):
    """
    Get all progress records for a client
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
    responses:
      200:
        description: List of weekly adherence records
        schema:
          type: array
          items:
            type: object
            properties:
              week:
                type: string
              adherence:
                type: integer
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT week, adherence FROM progress WHERE client_name=?", (name,))
    rows = cur.fetchall()
    conn.close()

    data = [{"week": w, "adherence": a} for w, a in rows]
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
