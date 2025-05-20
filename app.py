import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Firebase initialization
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

users_ref = db.collection("users")

# Symptom-treatment database
symptom_treatments = {
    "headache": {
        "Allopathy": {
            "treatment": "Take paracetamol 500mg. Rest in a dark room.",
            "diet": "Avoid caffeine and processed foods.",
            "exercises": "Practice neck stretches and relax with Shavasana."
        },
        "Ayurveda": {
            "treatment": "Use Brahmi or Ashwagandha with warm milk.",
            "diet": "Eat light meals, include fresh fruits and nuts.",
            "exercises": "Try gentle yoga and meditation for relaxation."
        },
        "Homeopathy": {
            "treatment": "Try Shavasana and deep breathing for 10 minutes.",
            "diet": "Include warm herbal teas.",
            "exercises": "Practice Shavasana, Pranayama, and gentle neck stretches."
        }
    },
    "cold": {
        "Allopathy": {
            "treatment": "Use antihistamines like cetirizine. Stay hydrated.",
            "diet": "Consume warm soups and fluids.",
            "exercises": "Avoid strenuous exercise; try light stretching."
        },
        "Ayurveda": {
            "treatment": "Drink Tulsi-Kadha and inhale steam with turmeric.",
            "diet": "Eat warm, easy-to-digest foods like khichdi.",
            "exercises": "Practice Pranayama and gentle yoga."
        },
        "Homeopathy": {
            "treatment": "Practice Pranayama (Anulom Vilom) and Kapalbhati.",
            "diet": "Include fresh fruits and warm fluids.",
            "exercises": "Pranayama and gentle asanas like Vajrasana."
        }
    },
    "fever": {
        "Allopathy": {
            "treatment": "Take paracetamol 500mg every 6 hours if fever persists.",
            "diet": "Light diet, plenty of water, avoid oily food.",
            "exercises": "Rest is best; avoid exercises."
        },
        "Ayurveda": {
            "treatment": "Use Giloy juice or decoction. Stay hydrated.",
            "diet": "Fresh fruits and cooling foods like cucumber.",
            "exercises": "Rest and mild breathing exercises only."
        },
        "Homeopathy": {
            "treatment": "Practice Sheetali Pranayama and rest.",
            "diet": "Hydrating liquids and fresh fruits.",
            "exercises": "Rest and breathing exercises."
        }
    },
    "stomach pain": {
        "Allopathy": {
            "treatment": "Take antacids or buscopan for cramps.",
            "diet": "Avoid spicy and heavy foods.",
            "exercises": "Try walking gently after meals."
        },
        "Ayurveda": {
            "treatment": "Use Hingvashtak Churna with warm water.",
            "diet": "Eat easily digestible foods, avoid fried items.",
            "exercises": "Pawanmuktasana and Vajrasana after meals."
        },
        "Homeopathy": {
            "treatment": "Try Pawanmuktasana and Vajrasana after meals.",
            "diet": "Warm liquids and small frequent meals.",
            "exercises": "Gentle yoga focusing on abdominal relief."
        }
    },
    "noise pain": {
        "Allopathy": {
            "treatment": "Use ear drops and consult ENT if persistent.",
            "diet": "No special diet required.",
            "exercises": "Avoid strenuous activity; rest ear muscles."
        },
        "Ayurveda": {
            "treatment": "Apply warm garlic oil drops in the ear.",
            "diet": "Avoid cold and damp foods.",
            "exercises": "Practice Bhramari Pranayama for ear relaxation."
        },
        "Homeopathy": {
            "treatment": "Practice Bhramari Pranayama for ear relaxation.",
            "diet": "Balanced diet, avoid excess salt.",
            "exercises": "Bhramari Pranayama and gentle neck stretches."
        }
    },
    "chest pain": {
        "Allopathy": {
            "treatment": "Seek immediate medical attention if severe. For mild, antacids may help.",
            "diet": "Avoid heavy, fatty foods.",
            "exercises": "Rest and avoid exertion."
        },
        "Ayurveda": {
            "treatment": "Use Arjuna bark decoction. Avoid heavy foods.",
            "diet": "Light meals, include fruits and vegetables.",
            "exercises": "Deep breathing and light yoga if mild."
        },
        "Homeopathy": {
            "treatment": "Practice deep breathing and relaxation techniques only if mild.",
            "diet": "Balanced diet, avoid stimulants.",
            "exercises": "Deep breathing exercises and gentle asanas."
        }
    }
}

# HTML home page
@app.route("/")
def home():
    return render_template("index.html")

# User signup route
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    phone = data.get("phone")
    name = data.get("name")

    user_doc = users_ref.document(phone)
    if user_doc.get().exists:
        return jsonify({"status": "exists", "message": "User already exists."})

    user_doc.set({
        "name": name,
        "phone": phone,
        "symptom_queries": [],
        "total_queries": 0
    })

    return jsonify({"status": "success", "message": "User signed up successfully."})

# Chat logic with tracking
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip().lower()
    stage = data.get("stage", "")
    symptom = data.get("symptom", "").strip().lower()
    phone = data.get("phone", "").strip()

    if not phone:
        return jsonify({"status": "error", "message": "Phone number required."})

    user_doc = users_ref.document(phone)
    user = user_doc.get()
    if not user.exists:
        return jsonify({"status": "error", "message": "User not found."})

    if stage == "initial":
        if message in symptom_treatments:
            return jsonify({
                "status": "options",
                "options": list(symptom_treatments[message].keys()),
                "symptom": message
            })
        else:
            return jsonify({
                "status": "text",
                "response": "Symptom not recognized. Try: headache, cold, fever, stomach pain, etc."
            })

    elif stage == "treatment-details":
        treatments = symptom_treatments.get(symptom)
        if treatments:
            treatment_info = treatments.get(message.title())
            if treatment_info:
                # Log query to Firebase
                user_doc.update({
                    "symptom_queries": firestore.ArrayUnion([symptom]),
                    "total_queries": firestore.Increment(1)
                })

                response_text = (
                    f"Treatment: {treatment_info['treatment']}\n\n"
                    f"Diet: {treatment_info['diet']}\n\n"
                    f"Exercises: {treatment_info['exercises']}"
                )
                return jsonify({"status": "details", "response": response_text})

        return jsonify({
            "status": "text",
            "response": "Treatment info not found."
        })

    return jsonify({
        "status": "text",
        "response": "Something went wrong."
    })

# Get user data
@app.route("/userdata/<phone>", methods=["GET"])
def get_user_data(phone):
    user = users_ref.document(phone).get()
    if not user.exists:
        return jsonify({"status": "error", "message": "User not found."})

    return jsonify(user.to_dict())

if __name__ == "__main__":
    app.run(debug=True)
