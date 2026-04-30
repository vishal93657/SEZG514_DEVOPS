__version__ = "1.1.0"
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
        "version": __version__}}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# ------------------ Database ------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
    """)

    # Clients (UPDATED)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER,
            membership_status TEXT,
            membership_end TEXT
        )
    """)

    # Progress
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
    """)

    # Workouts
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
    """)

    # Exercises
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            name TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    """)

    # Metrics
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            weight REAL,
            waist REAL,
            bodyfat REAL
        )
    """)

    # Default admin
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users VALUES ('admin','admin','Admin')")

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
    """
    return jsonify({"message": "ACEest Fitness & Gym API Running"})


# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    """
    Login user
    ---
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=? AND password=?",
                (data.get("username"), data.get("password")))
    row = cur.fetchone()
    conn.close()

    if row:
        return jsonify({"message": "Login successful", "role": row[0]})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/programs", methods=["GET"])
def get_programs():
    """
    Get all program names
    ---
    responses:
      200:
        description: List of available programs
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
          properties:
            name:
              type: string
            age:
              type: integer
            height:
              type: number
            weight:
              type: number
            program:
              type: string
    responses:
      200:
        description: Client saved successfully
    """
    data = request.get_json()

    name = data.get("name")
    program = data.get("program")
    weight = data.get("weight")

    if not name:
        return jsonify({"error": "Name required"}), 400

    calories = int(weight * programs[program]["factor"]) if weight and program in programs else None

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO clients
        (name, age, height, weight, program, calories, target_weight, target_adherence, membership_status, membership_end)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        data.get("age"),
        data.get("height"),
        weight,
        program,
        calories,
        data.get("target_weight"),
        data.get("target_adherence"),
        data.get("membership_status", "Active"),
        data.get("membership_end")
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Client saved", "calories": calories})


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

    return jsonify({
        "name": row[1],
        "age": row[2],
        "height": row[3],
        "weight": row[4],
        "program": row[5],
        "calories": row[6],
        "membership_status": row[9]
    })


@app.route("/progress", methods=["POST"])
def save_progress():
    """
    Save weekly adherence for a client
    ---
    parameters:
      - in: body
        name: progress
        schema:
          type: object
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
    data = request.get_json()
    week = datetime.now().strftime("Week %U - %Y")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO progress (client_name, week, adherence)
        VALUES (?, ?, ?)
    """, (data.get("name"), week, data.get("adherence", 0)))

    conn.commit()
    conn.close()

    return jsonify({"message": "Progress saved"})


@app.route("/progress/<name>", methods=["GET"])
def get_progress(name):
    """
    Get progress records
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
    responses:
      200:
        description: Progress list
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT week, adherence FROM progress WHERE client_name=?", (name,))
    rows = cur.fetchall()
    conn.close()

    return jsonify([{"week": w, "adherence": a} for w, a in rows])


# ---------- WORKOUT ----------
@app.route("/workout", methods=["POST"])
def add_workout():
    """
    Add workout
    ---
    parameters:
      - in: body
        name: workout
        schema:
          type: object
          properties:
            name:
              type: string
            date:
              type: string
            type:
              type: string
            duration:
              type: integer
            notes:
              type: string
    responses:
      200:
        description: Workout added
    """
    data = request.get_json()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("date"),
        data.get("type"),
        data.get("duration"),
        data.get("notes")
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Workout added"})


@app.route("/workout/<name>", methods=["GET"])
def get_workouts(name):
    """
    Get workouts for client
    ---
    parameters:
      - name: name
        in: path
        type: string
    responses:
      200:
        description: Workout list
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT date, workout_type, duration_min, notes
        FROM workouts WHERE client_name=?
    """, (name,))
    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {"date": d, "type": t, "duration": dur, "notes": n}
        for d, t, dur, n in rows
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
