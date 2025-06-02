from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)  # Log to console

# Define fuzzy variables
muscle_level = ctrl.Antecedent(np.arange(0, 6, 1), 'muscle_level')
fat_level = ctrl.Antecedent(np.arange(0, 6, 1), 'fat_level')
workout_intensity = ctrl.Consequent(np.arange(0, 11, 1), 'workout_intensity')

# Membership functions for muscle_level (0-5 scale: very_low to very_high)
muscle_level['very_low'] = fuzz.trimf(muscle_level.universe, [0, 0, 1])
muscle_level['low'] = fuzz.trimf(muscle_level.universe, [0, 1, 2])
muscle_level['medium'] = fuzz.trimf(muscle_level.universe, [1, 2, 3])
muscle_level['high'] = fuzz.trimf(muscle_level.universe, [2, 3, 4])
muscle_level['very_high'] = fuzz.trimf(muscle_level.universe, [3, 4, 5])

# Membership functions for fat_level (0-5 scale: very_low to very_high)
fat_level['very_low'] = fuzz.trimf(fat_level.universe, [0, 0, 1])
fat_level['low'] = fuzz.trimf(fat_level.universe, [0, 1, 2])
fat_level['medium'] = fuzz.trimf(fat_level.universe, [1, 2, 3])
fat_level['high'] = fuzz.trimf(fat_level.universe, [2, 3, 4])
fat_level['very_high'] = fuzz.trimf(fat_level.universe, [3, 4, 5])

# Membership functions for workout_intensity (0-10 scale: low to high)
workout_intensity['low'] = fuzz.trimf(workout_intensity.universe, [0, 0, 5])
workout_intensity['medium'] = fuzz.trimf(workout_intensity.universe, [2, 5, 8])
workout_intensity['high'] = fuzz.trimf(workout_intensity.universe, [5, 10, 10])

# Expanded fuzzy rules to cover all combinations
rule1 = ctrl.Rule(muscle_level['very_low'] & fat_level['very_high'], workout_intensity['low'])
rule2 = ctrl.Rule(muscle_level['low'] & fat_level['high'], workout_intensity['low'])
rule3 = ctrl.Rule(muscle_level['medium'] & fat_level['medium'], workout_intensity['medium'])
rule4 = ctrl.Rule(muscle_level['high'] & fat_level['low'], workout_intensity['medium'])
rule5 = ctrl.Rule(muscle_level['very_high'] & fat_level['very_low'], workout_intensity['high'])
rule6 = ctrl.Rule(muscle_level['very_low'] & fat_level['very_low'], workout_intensity['medium'])
rule7 = ctrl.Rule(muscle_level['high'] & fat_level['high'], workout_intensity['medium'])
rule8 = ctrl.Rule(muscle_level['low'] & fat_level['low'], workout_intensity['medium'])
rule9 = ctrl.Rule(muscle_level['very_high'] & fat_level['very_high'], workout_intensity['low'])

# Add missing combinations
rule10 = ctrl.Rule(muscle_level['very_low'] & fat_level['medium'], workout_intensity['low'])
rule11 = ctrl.Rule(muscle_level['very_low'] & fat_level['low'], workout_intensity['medium'])
rule12 = ctrl.Rule(muscle_level['low'] & fat_level['medium'], workout_intensity['low'])
rule13 = ctrl.Rule(muscle_level['low'] & fat_level['very_low'], workout_intensity['medium'])
rule14 = ctrl.Rule(muscle_level['low'] & fat_level['very_high'], workout_intensity['low'])
rule15 = ctrl.Rule(muscle_level['medium'] & fat_level['very_low'], workout_intensity['medium'])
rule16 = ctrl.Rule(muscle_level['medium'] & fat_level['low'], workout_intensity['medium'])
rule17 = ctrl.Rule(muscle_level['medium'] & fat_level['high'], workout_intensity['medium'])
rule18 = ctrl.Rule(muscle_level['medium'] & fat_level['very_high'], workout_intensity['low'])
rule19 = ctrl.Rule(muscle_level['high'] & fat_level['very_low'], workout_intensity['medium'])
rule20 = ctrl.Rule(muscle_level['high'] & fat_level['medium'], workout_intensity['medium'])
rule21 = ctrl.Rule(muscle_level['high'] & fat_level['very_high'], workout_intensity['medium'])
rule22 = ctrl.Rule(muscle_level['very_high'] & fat_level['low'], workout_intensity['high'])
rule23 = ctrl.Rule(muscle_level['very_high'] & fat_level['medium'], workout_intensity['high'])
rule24 = ctrl.Rule(muscle_level['very_high'] & fat_level['high'], workout_intensity['medium'])

# Control system
workout_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9,
                                 rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17,
                                 rule18, rule19, rule20, rule21, rule22, rule23, rule24])
workout_simulation = ctrl.ControlSystemSimulation(workout_ctrl)

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

        gender = data["gender"].lower()  # Ensure case-insensitive
        muscle_level = data["muscle_level"].lower()  # Ensure case-insensitive
        fat_level = data["fat_level"].lower()  # Ensure case-insensitive
        goal = data["goal"].replace("build_muscle", "muscle_gain").replace("lose_fat", "fat_loss").replace("body_recomp", "maintenance")
        workout_type = data["workout_type"].lower()  # Ensure case-insensitive

        # Fuzzy logic input (map string to numeric for simulation)
        muscle_map = {"very_low": 0, "low": 1, "medium": 2, "high": 3, "very_high": 4}
        fat_map = {"very_low": 0, "low": 1, "medium": 2, "high": 3, "very_high": 4}
        workout_simulation.input['muscle_level'] = muscle_map.get(muscle_level, 2)  # Default to medium if invalid
        workout_simulation.input['fat_level'] = fat_map.get(fat_level, 2)  # Default to medium if invalid
        workout_simulation.compute()

        # Get fuzzy output
        intensity = workout_simulation.output['workout_intensity']
        logging.debug(f"Computed intensity: {intensity}")  # Debug to track intensity

        # Adjust calorie and protein based on intensity
        def calculate_calories(age, weight, height, gender, goal):
            # Calculate BMR using Mifflin-St Jeor Equation
            if gender == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
            # Adjust activity level based on workout intensity
            if intensity < 4:  # Low intensity
                activity_multiplier = 1.375  # Lightly active
            elif intensity > 7:  # High intensity
                activity_multiplier = 1.725  # Very active
            else:
                activity_multiplier = 1.55  # Moderately active
            
            # Calculate TDEE
            tdee = bmr * activity_multiplier
            
            # Adjust calories based on goal
            if goal == "fat_loss":
                # Create a 20% deficit for fat loss
                return round(tdee * 0.8)
            elif goal == "muscle_gain":
                # Add 10% surplus for muscle gain
                return round(tdee * 1.1)
            else:  # maintenance
                return round(tdee)

        def calculate_protein(weight, muscle_level, goal):
            base_protein = 1.5 if goal == "maintenance" else 1.8 if goal == "fat_loss" else 2.0
            if intensity < 4:  # Low intensity
                return round(weight * (base_protein - 0.2))
            elif intensity > 7:  # High intensity
                return round(weight * (base_protein + 0.2))
            return round(weight * base_protein)

        def calculate_steps(weight, fat_level, goal):
            fat_levels = {"very_low": 1, "low": 2, "medium": 3, "high": 4, "very_high": 5}
            fat_factor = fat_levels.get(fat_level, 3)
            if goal == "fat_loss":
                return 10000 + (fat_factor * 500)
            elif goal == "muscle_gain":
                return 7000 + (fat_factor * 250)
            else:
                return 9000 + (fat_factor * 300)

        def get_user_status(weight, muscle_level, fat_level, goal):
            status = []
            low_fat = fat_level in ["very_low", "low"]
            high_fat = fat_level in ["high", "very_high"]
            low_muscle = muscle_level in ["very_low", "low"]
            high_muscle = muscle_level in ["high", "very_high"]
            light_weight = weight < 60
            heavy_weight = weight > 100

            if goal == "fat_loss":
                if high_fat: status.append("Elevated fat suggests excess weight focus.")
                elif low_fat: status.append("Low fat indicates minimal loss needed.")
                else: status.append("Moderate fat for balanced fat loss.")
                status.append("Fat loss via deficit and activity.")
                if low_muscle: status.append("Preserve muscle mass.")

            elif goal == "muscle_gain":
                if low_muscle: status.append("Low muscle offers growth potential.")
                elif high_muscle: status.append("High muscle supports further gains.")
                else: status.append("Moderate muscle for growth.")
                status.append("Muscle gain with caloric surplus and training.")
                if heavy_weight: status.append("Heavy weight aids intensity.")

            elif goal == "maintenance":
                if high_fat and low_muscle: status.append("Mixed composition for balance.")
                elif low_fat and high_muscle: status.append("Lean build suits maintenance.")
                else: status.append("Balanced physique for refinement.")
                status.append("Maintain with moderate plan.")

            return status

        def get_workout_plan(goal, workout_type, intensity):
            plans = {
                "fat_loss": {
                    "gym": {"name": "Full Body Circuit", "freq": "4-5", "summary": "High-intensity fat burn.", "url": "/FitnessPlanDetails.html#full-body-circuit-training"},
                    "calisthenics": {"name": "HIIT Bodyweight", "freq": "4-5", "summary": "Intense fat loss intervals.", "url": "/FitnessPlanDetails.html#hiit-bodyweight-workouts"}
                },
                "muscle_gain": {
                    "gym": {"name": "Push-Pull-Legs", "freq": "5-6", "summary": "Compound lifts for growth.", "url": "/FitnessPlanDetails.html#push-pull-legs"},
                    "calisthenics": {"name": "Progressive Calisthenics", "freq": "4-5", "summary": "Progressive muscle build.", "url": "/FitnessPlanDetails.html#progressive-calisthenicss"}
                },
                "maintenance": {
                    "gym": {"name": "Upper-Lower Split", "freq": "3-4", "summary": "Balanced strength.", "url": "/FitnessPlanDetails.html#upper-lower-split"},
                    "calisthenics": {"name": "Balanced Bodyweight", "freq": "3-4", "summary": "Moderate fitness.", "url": "/FitnessPlanDetails.html#balanced-bodyweight-routine"}
                }
            }
            plan = plans.get(goal, {}).get(workout_type, {"name": "General Plan", "freq": "3-5", "summary": "Basic fitness.", "url": "/FitnessPlanDetails.html#push-pull-legs"})
            if intensity is None or not 0 <= intensity <= 10:  # Fallback if intensity fails
                intensity = 5  # Default to medium
            if intensity < 4:
                plan["freq"] = str(int(plan["freq"].split("-")[0]) - 1) + "-" + plan["freq"].split("-")[1]
            elif intensity > 7:
                plan["freq"] = plan["freq"].split("-")[0] + "-" + str(int(plan["freq"].split("-")[1]) + 1)
            return plan

        # Calculate results with fuzzy adjustments
        calories = calculate_calories(age, weight, height, gender, goal)
        protein = calculate_protein(weight, muscle_level, goal)
        steps = calculate_steps(weight, fat_level, goal)
        workout_plan = get_workout_plan(goal, workout_type, intensity)
        user_status = get_user_status(weight, muscle_level, fat_level, goal)

        return jsonify({
            "user_status": user_status,
            "workout_plan": {
                "name": workout_plan["name"],
                "frequency": f"{workout_plan['freq']} days/week",
                "summary": workout_plan["summary"],
                "url": workout_plan["url"]
            },
            "daily_steps": steps,
            "calories": calories,
            "protein": protein,
            "fuzzy_intensity": round(intensity, 1) if intensity is not None else 5.0
        }), 200

    except Exception as e:
        logging.error("Error processing request: %s", str(e))
        return jsonify({"error": f"Unexpected input: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)