import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Scikit-learn Machine Learning components
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# Import Gemini Fallback Handler from fallbacks.py
from fallbacks import GeminiFallbackHandler

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Gemini Fallback Handler
gemini_handler = GeminiFallbackHandler()

# =====================================================================
# 1. DATABASE SETUP (SQLite)
# =====================================================================
DB_FILE = "database.db"

def init_db():
    """Initializes the SQLite database table for logging queries."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sender_number TEXT NOT NULL,
            user_query TEXT NOT NULL,
            matched_intent TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            route_used TEXT NOT NULL,
            bot_response TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("[Database]: SQLite database initialized successfully.")

def log_interaction(sender_number, user_query, matched_intent, confidence_score, route_used, bot_response):
    """Saves a single WhatsApp interaction into database.db."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO query_logs (timestamp, sender_number, user_query, matched_intent, confidence_score, route_used, bot_response)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sender_number,
            user_query,
            matched_intent,
            float(confidence_score),
            route_used,
            bot_response
        ))
        conn.commit()
        conn.close()
        print(f"[Database]: Logged interaction for {sender_number} ({route_used})")
    except Exception as e:
        print(f"[Database Error]: Failed to log interaction: {e}")

# Initialize Database on app start
init_db()

# =====================================================================
# 2. LOCAL INTENTS DATASET (Zetech University Administrative FAQs)
# =====================================================================
INTENTS_DATA = [
    # EXAMINATIONS & ACADEMICS
    {
        "intent": "supp_exam_registration",
        "patterns": [
            "How do I register for supplementary exams?",
            "Supplementary exam registration process",
            "Special exams registration",
            "When are supplementary exams done?",
            "How to apply for retakes or supps"
        ],
        "response": "To register for supplementary or special examinations, log into the student portal (https://portal.zetech.ac.ke), navigate to 'Examinations', select 'Supplementary Registration', choose your units, and complete the registration fee payment before the deadline."
    },
    {
        "intent": "portal_password_reset",
        "patterns": [
            "How do I reset my student portal password?",
            "I forgot my portal password",
            "Cannot log in to student portal",
            "Portal password recovery",
            "Reset credentials for portal"
        ],
        "response": "To reset your student portal password, visit https://portal.zetech.ac.ke and click on 'Forgot Password'. Enter your student admission number and follow the reset link sent to your registered official email address. For ICT support, email ictsupport@zetech.ac.ke."
    },

    # ADMISSIONS & INTAKES
    {
        "intent": "intakes",
        "patterns": [
            "When are your intakes?",
            "What months do you admit students?",
            "When is the next intake at Zetech?",
            "Can I apply for May intake?",
            "January September intakes"
        ],
        "response": "Zetech University has three main intakes every year: January, May, and September. Applications are open for full-time, part-time, and online/distance learning modes."
    },
    {
        "intent": "application_process",
        "patterns": [
            "How do I apply for a course?",
            "What is the application link?",
            "How can I apply online?",
            "Sajili portal online application",
            "Where do I submit my application forms?"
        ],
        "response": "You can apply online via the Sajili portal at https://sajili.zetech.ac.ke by filling out the form and attaching your academic certificates. Applications can also be submitted physically at any Zetech campus."
    },
    {
        "intent": "kuccps_admissions",
        "patterns": [
            "How do I access my KUCCPS admission letter?",
            "I was placed at Zetech through KUCCPS",
            "KUCCPS government sponsored fee structure",
            "KUCCPS admission letter download"
        ],
        "response": "KUCCPS government-sponsored students can download their official Zetech admission letters from the online admissions portal at https://www.zetech.ac.ke under the KUCCPS section. For queries, email admissions@zetech.ac.ke or call 0721211174."
    },

    # FEES & PAYMENT POLICIES
    {
        "intent": "fee_payment_policy",
        "patterns": [
            "Do you accept fee payment in installments?",
            "What is the 40-40-20 fee policy?",
            "How do I pay my fees?",
            "Installment plan for tuition fees"
        ],
        "response": "Yes! Zetech University operates a flexible 40-40-20% fee payment policy: 40% upon reporting in month 1, 40% in month 2, and the remaining 20% cleared before sitting for final semester exams."
    },
    {
        "intent": "fee_balance_check",
        "patterns": [
            "How can I check my fee balance?",
            "Where do I view my fee statement?",
            "Check my balance on portal",
            "Student portal fee statement"
        ],
        "response": "You can check your live fee balance and statement anytime by logging into the student portal at https://portal.zetech.ac.ke using your student credentials."
    },

    # CAMPUS LOCATIONS & CONTACTS
    {
        "intent": "campus_locations",
        "patterns": [
            "Where are your campuses located?",
            "Where is Zetech main campus?",
            "Do you have a Nairobi CBD campus?",
            "Ruiru campus location",
            "Mang'u Technology Park"
        ],
        "response": "Zetech University has 3 main campuses:\n1. Main Campus: Mang'u Technology Park (along Thika Superhighway, next to Mang'u High School).\n2. Ruiru Campus: Along Thika Superhighway, Ruiru.\n3. Nairobi City Campus: Stanbank Building & Pioneer Building along Moi Avenue, Nairobi CBD."
    },
    {
        "intent": "contact_info",
        "patterns": [
            "What is the official phone number for Zetech?",
            "How can I contact the university?",
            "Zetech email address and WhatsApp number",
            "Call center opening hours"
        ],
        "response": "You can reach Zetech University via:\n• Call Center: 0719034500 or 0706622557\n• Email: info@zetech.ac.ke or courses@zetech.ac.ke\n• Call Center Hours: Mon-Fri (7am–7pm), Sat (9am–2pm)."
    },

    # ACCOMMODATION & HOSTELS
    {
        "intent": "hostel_accommodation",
        "patterns": [
            "Do you offer hostels for students?",
            "Is there accommodation on campus?",
            "Where do students stay?",
            "Zetech hostel booking and partners"
        ],
        "response": "Yes, Zetech University offers university hostels and has partnered with verified private accommodation service providers near the campuses. Learn more at https://www.zetech.ac.ke/accommodation/."
    },

    # E-LEARNING & BLENDED MODE
    {
        "intent": "elearning_support",
        "patterns": [
            "What is blended learning?",
            "Do you offer online classes?",
            "Who do I contact for e-learning portal issues?",
            "Distance learning day and evening classes"
        ],
        "response": "Zetech Digital School offers full-time, online, and blended learning (combining face-to-face and virtual classes). For e-learning support or login issues, contact elearning@zetech.ac.ke or call 0714588863."
    }
]

# =====================================================================
# 3. MODEL TRAINING (TF-IDF + Multinomial Naive Bayes)
# =====================================================================
print("[System Initialization]: Training Local Intent Classifier...")

X_train = []
y_train = []
intent_responses = {}

for item in INTENTS_DATA:
    intent_tag = item["intent"]
    intent_responses[intent_tag] = item["response"]
    for pattern in item["patterns"]:
        X_train.append(pattern)
        y_train.append(intent_tag)

# Create Pipeline
intent_model = make_pipeline(TfidfVectorizer(), MultinomialNB())
intent_model.fit(X_train, y_train)

print(f"[System Initialization]: Trained successfully on {len(X_train)} patterns across {len(intent_responses)} intent categories.\n")

# =====================================================================
# 4. ROUTING ENGINE WITH LOGGING
# =====================================================================
CONFIDENCE_THRESHOLD = 0.60

def process_query(user_query: str, sender_number: str = "Unknown") -> str:
    """
    Evaluates incoming student query against local Naive Bayes model.
    Routes to Gemini Fallback if confidence < 0.60 and logs result to SQLite.
    """
    if not user_query or not user_query.strip():
        return "Please enter a valid query."

    # Predict class probabilities
    probabilities = intent_model.predict_proba([user_query])[0]
    max_confidence = max(probabilities)
    predicted_intent = intent_model.classes_[probabilities.argmax()]

    print(f"[Query Analysis]: '{user_query}'")
    print(f"  ├─ Top Matched Intent: '{predicted_intent}'")
    print(f"  ├─ Confidence Score: {max_confidence:.4f}")

    if max_confidence >= CONFIDENCE_THRESHOLD:
        print("  └─ Decision: LOCAL INTENT MATCH (Confidence >= 0.60)")
        bot_response = intent_responses[predicted_intent]
        route_used = "Local Intent Match"
    else:
        print("  └─ Decision: FALLBACK TO GEMINI (Confidence < 0.60)")
        bot_response = gemini_handler.get_fallback_response(user_query)
        route_used = "Gemini Fallback"

    # Save interaction to SQLite database
    log_interaction(sender_number, user_query, predicted_intent, max_confidence, route_used, bot_response)

    return bot_response

# =====================================================================
# 5. FLASK WEBHOOK & LOGS ROUTES
# =====================================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Online",
        "service": "Zetech University AI Academic & Administrative Support Chatbot",
        "intents_trained": len(intent_responses),
        "database": DB_FILE
    }), 200

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Twilio WhatsApp Webhook Endpoint."""
    incoming_msg = request.values.get("Body", "").strip()
    sender_number = request.values.get("From", "Unknown")

    print(f"\n--- INCOMING WHATSAPP MESSAGE ---")
    print(f"From: {sender_number}")
    print(f"Body: {incoming_msg}")

    # Process query and log interaction
    bot_response = process_query(incoming_msg, sender_number)

    # Format response for Twilio WhatsApp
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(bot_response)

    return str(resp)

@app.route("/logs", methods=["GET"])
def view_logs():
    """API Endpoint to retrieve past chat logs in JSON format."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM query_logs ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        logs = [dict(row) for row in rows]
        conn.close()
        return jsonify({"count": len(logs), "logs": logs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================================================================
# 6. SERVER ENTRYPOINT
# =====================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)