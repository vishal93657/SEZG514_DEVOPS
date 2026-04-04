from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from

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

programs = {
    "Fat Loss (FL)": {
        "workout": "Mon: 5x5 Back Squat + AMRAP\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: 10RFT Deadlifts/Box Jumps\nFri: 30min Active Recovery",
        "diet": "B: 3 Egg Whites + Oats Idli\nL: Grilled Chicken + Brown Rice\nD: Fish Curry + Millet Roti\nTarget: 2,000 kcal",
        "color": "#e74c3c",
        "calorie_factor": 22},
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "B: 4 Eggs + PB Oats\nL: Chicken Biryani (250g Chicken)\nD: Mutton Curry + Jeera Rice\nTarget: 3,200 kcal",
        "color": "#2ecc71",
        "calorie_factor": 35},
    "Beginner (BG)": {
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups.\nFocus: Technique Mastery & Form (90% Threshold)",
        "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\nProtein: 120g/day",
                "color": "#3498db",
        "calorie_factor": 26}}


@app.route("/")
def home():
    """
    Home Endpoint
    ---
    responses:
      200:
        description: API is running
        content:
          application/json:
            example: {"message": "ACEest Fitness & Gym Running"}
    """
    return jsonify({"message": "ACEest Fitness & Gym Running"})


@app.route("/programs")
def get_programs():
    """
    List all programs
    ---
    responses:
      200:
        description: Returns list of program names
        content:
          application/json:
            example: ["Fat Loss (FL)", "Muscle Gain (MG)", "Beginner (BG)"]
    """
    return jsonify(list(programs.keys()))


@app.route("/program/<name>")
def get_program(name):
    """
    Get details for a specific program
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Name of the program
    responses:
      200:
        description: Program details returned
        content:
          application/json:
            example:
              workout: "Mon: 5x5 Back Squat + AMRAP..."
              diet: "B: 3 Egg Whites + Oats Idli..."
              color: "#e74c3c"
      404:
        description: Program not found
        content:
          application/json:
            example: {"error": "Program not found"}
    """
    if name in programs:
        return jsonify(programs[name])
    return jsonify({"error": "Program not found"}), 404


@app.route("/client", methods=["POST"])
def client_profile():
    """
    Submit client profile and get estimated calories
    ---
    requestBody:
      required: true
      content:
        application/json:
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
              adherence:
                type: integer
    responses:
      200:
        description: Client info with calories
      400:
        description: Invalid program
    """
    data = request.get_json()
    program_name = data.get("program")
    if program_name not in programs:
        return jsonify({"error": "Invalid program"}), 400

    weight = data.get("weight")
    calories = int(weight * programs[program_name]
                   ["calorie_factor"]) if weight else None

    return jsonify({
        "name": data.get("name"),
        "program": program_name,
        "calories": calories,
        "adherence": data.get("adherence")
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
