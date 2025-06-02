from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)  # Log to console

@app.route('/calculate', methods=['POST'])
def fitness_plan():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()
        logging.debug("Received data: %s", data)

        required_fields = ["age", "height", "weight", "gender", "muscle_level", "fat_level", "goal", "workout_type"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate and convert numeric inputs
        try:
            age = int(data["age"])
            height = int(data["height"])
            weight = int(data["weight"])
        except ValueError as e:
            return jsonify({"error": f"Invalid numeric input: {str(e)}"}), 400

        gender = data["gender"]
        muscle_level = data["muscle_level"]
        fat_level = data["fat_level"]
        goal = data["goal"].replace("build_muscle", "muscle_gain").replace("lose_fat", "fat_loss").replace("body_recomp", "maintenance")
        workout_type = data["workout_type"]

        def calculate_calories(age, weight, height, gender, goal):
            if gender.lower() == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            tdee = bmr * 1.55
            if goal == "fat_loss":
                return round(tdee - 400)
            elif goal == "muscle_gain":
                return round(tdee + 300)
            else:
                return round(tdee)

        def calculate_protein(weight, muscle_level, goal):
            if goal == "muscle_gain":
                protein_per_kg = 2.0
            elif goal == "fat_loss":
                protein_per_kg = 1.8
            else:
                protein_per_kg = 1.5
            return round(weight * protein_per_kg)

        def calculate_steps(weight, fat_level, goal):
            if goal == "fat_loss":
                return 12000
            elif goal == "muscle_gain":
                return 8000
            else:
                return 10000

        def get_workout_plan(goal, workout_type):
            plans = {
                "fat_loss": {
                    "gym": ("Full Body Circuit Training", "https://www.example.com/full-body-circuit"),
                    "calisthenics": ("HIIT Workouts", "https://www.example.com/hiit"),
                },
                "muscle_gain": {
                    "gym": ("Push-Pull-Legs (PPL)", "https://www.example.com/ppl"),
                    "calisthenics": ("Strength + Cardio Hybrid", "https://www.example.com/strength-cardio"),
                },
                "maintenance": {
                    "gym": ("Upper-Lower Split", "https://www.example.com/upper-lower"),
                    "calisthenics": ("Active Lifestyle Plan", "https://www.example.com/active-lifestyle"),
                }
            }
            return plans.get(goal, {}).get(workout_type, ("General Fitness Plan", "https://www.example.com/general-fitness"))

        calories = calculate_calories(age, weight, height, gender, goal)
        protein = calculate_protein(weight, muscle_level, goal)
        steps = calculate_steps(weight, fat_level, goal)
        workout, link = get_workout_plan(goal, workout_type)

        return jsonify({
            "workout_plan": workout,
            "workout_plan_url": link,
            "daily_steps": steps,
            "calories": calories,
            "protein": protein
        }), 200

    except Exception as e:
        logging.error("Error processing request: %s", str(e))
        return jsonify({"error": f"Unexpected input: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)