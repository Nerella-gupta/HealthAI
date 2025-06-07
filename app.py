from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory user storage
users = {}

# Translation dictionary
translations = {
    "en": {
        "Treatment": "Treatment",
        "Diet": "Diet",
        "Exercises": "Exercises",
        "Ingredients": "Ingredients",
        "Preparation": "Preparation"
    },
    "hi": {
        "Treatment": "उपचार",
        "Diet": "आहार",
        "Exercises": "व्यायाम",
        "Ingredients": "सामग्री",
        "Preparation": "तैयारी"
    },
    "te": {
        "Treatment": "చికిత్స",
        "Diet": "ఆహారం",
        "Exercises": "వ్యాయామాలు",
        "Ingredients": "పదార్థాలు",
        "Preparation": "తయారీ"
    }
}

# Juice recipes
juice_recipes = {
    "Giloy juice": {
        "ingredients": ["Fresh Giloy stem", "1 glass water"],
        "preparation": "Boil chopped Giloy stems in water for 15 mins. Strain and drink warm."
    },
    "Arjuna bark decoction": {
        "ingredients": ["Arjuna bark (1 tsp)", "2 cups water"],
        "preparation": "Boil Arjuna bark in water until reduced to half. Strain and drink."
    },
    "Tulsi-Kadha": {
        "ingredients": ["Tulsi leaves", "Ginger", "Black pepper", "Water"],
        "preparation": "Boil Tulsi leaves, ginger, and pepper in water for 10 mins. Strain and sip warm."
    }
}

# Symptom-treatment data
symptom_treatments = {
    "fever": {
        "Ayurveda": {
            "treatment": "Use Giloy juice or decoction. Stay hydrated.",
            "diet": "Fresh fruits and cooling foods like cucumber.",
            "exercises": "Rest and mild breathing exercises only.",
            "juice": "Giloy juice"
        },
        "Allopathy": {
            "treatment": "Take paracetamol 500mg every 6 hours if fever persists.",
            "diet": "Light diet, plenty of water, avoid oily food.",
            "exercises": "Rest is best; avoid exercises."
        },
        "Homeopathy": {
            "treatment": "Practice Sheetali Pranayama and rest.",
            "diet": "Hydrating liquids and fresh fruits.",
            "exercises": "Rest and breathing exercises."
        }
    },
    "cold": {
        "Ayurveda": {
            "treatment": "Drink Tulsi-Kadha and inhale steam with turmeric.",
            "diet": "Eat warm, easy-to-digest foods like khichdi.",
            "exercises": "Practice Pranayama and gentle yoga.",
            "juice": "Tulsi-Kadha"
        },
        "Allopathy": {
            "treatment": "Use antihistamines like cetirizine. Stay hydrated.",
            "diet": "Consume warm soups and fluids.",
            "exercises": "Avoid strenuous exercise; try light stretching."
        },
        "Homeopathy": {
            "treatment": "Practice Pranayama (Anulom Vilom) and Kapalbhati.",
            "diet": "Include fresh fruits and warm fluids.",
            "exercises": "Pranayama and gentle asanas like Vajrasana."
        }
    }
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    phone = data.get("phone")
    name = data.get("name")

    if phone in users:
        return jsonify({"status": "exists", "message": "User already exists."})

    users[phone] = {
        "name": name,
        "phone": phone,
        "symptom_queries": [],
        "total_queries": 0
    }

    return jsonify({"status": "success", "message": "User signed up successfully."})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip().lower()
    stage = data.get("stage", "")
    symptom = data.get("symptom", "").strip().lower()
    phone = data.get("phone", "").strip()
    lang = data.get("lang", "en")

    if phone not in users:
        return jsonify({"status": "error", "message": "User not found."})

    # Initial stage: match symptom
    if stage == "initial":
        if message in symptom_treatments:
            return jsonify({
                "status": "options",
                "options": list(symptom_treatments[message].keys()),
                "symptom": message
            })
        return jsonify({
            "status": "text",
            "response": "Symptom not recognized. Try: fever, cold, stomach pain."
        })

    # Treatment stage
    elif stage == "treatment-details":
        treatments = symptom_treatments.get(symptom)
        if treatments:
            treatment_info = treatments.get(message.title())
            if treatment_info:
                # Update user query count
                users[phone]["symptom_queries"].append(symptom)
                users[phone]["total_queries"] += 1

                t = translations.get(lang, translations["en"])
                response = (
                    f"{t['Treatment']}: {treatment_info['treatment']}\n\n"
                    f"{t['Diet']}: {treatment_info['diet']}\n\n"
                    f"{t['Exercises']}: {treatment_info['exercises']}"
                )

                juice = treatment_info.get("juice")
                if juice and juice in juice_recipes:
                    recipe = juice_recipes[juice]
                    response += (
                        f"\n\n{juice} -\n"
                        f"{t['Ingredients']}: {', '.join(recipe['ingredients'])}\n"
                        f"{t['Preparation']}: {recipe['preparation']}"
                    )

                return jsonify({"status": "details", "response": response})

        return jsonify({"status": "text", "response": "Treatment info not found."})

    return jsonify({"status": "text", "response": "Something went wrong."})

@app.route("/userdata/<phone>", methods=["GET"])
def get_user_data(phone):
    if phone not in users:
        return jsonify({"status": "error", "message": "User not found."})
    return jsonify(users[phone])

if __name__ == "__main__":
    app.run(debug=True)
