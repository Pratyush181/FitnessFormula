from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/calculate', methods=['POST'])
def fitness_plan():
    try:
        # Ensure the request is JSON
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()  # Use get_json() instead of request.json

        # Extract required fields
        required_fields = ["age", "height", "weight", "gender", "muscle_level", "fat_level", "goal", "workout_type"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        age = int(data["age"])
        height = int(data["height"])
        weight = int(data["weight"])
        gender = data["gender"]
        muscle_level = data["muscle_level"]
        fat_level = data["fat_level"]
        goal = data["goal"]
        workout_type = data["workout_type"]

        def calculate_calories(age, weight, height, gender, goal):
            if gender.lower() == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            # Assuming moderate activity (1.55x BMR)
            tdee = bmr * 1.55

            if goal == "fat_loss":
                return round(tdee - 400)  # Calorie deficit
            elif goal == "muscle_gain":
                return round(tdee + 300)  # Calorie surplus
            else:
                return round(tdee)  # Maintenance


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
                    "strength": ("Full Body Circuit Training", "https://www.example.com/full-body-circuit"),
                    "cardio": ("HIIT Workouts", "https://www.example.com/hiit"),
                    "mixed": ("Hybrid Fat Loss Plan", "https://www.example.com/hybrid-plan"),
                },
                "muscle_gain": {
                    "strength": ("Push-Pull-Legs (PPL)", "https://www.example.com/ppl"),
                    "cardio": ("Strength + Cardio Hybrid", "https://www.example.com/strength-cardio"),
                    "mixed": ("Athletic Strength Plan", "https://www.example.com/athletic-strength"),
                },
                "maintenance": {
                    "strength": ("Upper-Lower Split", "https://www.example.com/upper-lower"),
                    "cardio": ("Active Lifestyle Plan", "https://www.example.com/active-lifestyle"),
                    "mixed": ("Balanced Fitness Routine", "https://www.example.com/balanced-fitness"),
                }
            }

            return plans.get(goal, {}).get(workout_type, ("General Fitness Plan", "https://www.example.com/general-fitness"))


        # Calculate values
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
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
