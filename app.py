import os
from flask import Flask, request, jsonify
from preprocessor import TextPreprocessor
from classifier import IntentClassifier
from fallbacks import GeminiFallbackHandler
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

preprocessor = TextPreprocessor()
classifier = IntentClassifier(confidence_threshold=0.60)
gemini_fallback = GeminiFallbackHandler()

# Initial training data
X_train = [
    "how do i register for supplementary exams",
    "when is the exam registration deadline",
    "what is my outstanding fee balance",
    "how to pay my fees online",
    "i cannot log in to student portal"
]
y_train = [
    "exam_registration",
    "exam_registration",
    "fee_balance",
    "fee_balance",
    "portal_issue"
]

classifier.train(X_train, y_train)

KNOWLEDGE_BASE = {
    "exam_registration": "To register for supplementary exams, log into the portal, navigate to 'Examinations', and complete the form.",
    "fee_balance": "Check your fee balance on the portal under 'Finance'. Payments are made via official M-Pesa Paybill.",
    "portal_issue": "For portal login errors, click 'Forgot Password' or visit the campus ICT helpdesk."
}

@app.route("/chat", methods=["POST"])
def web_chat():
    data = request.get_json() or {}
    user_query = data.get("message", "")
    
    cleaned = preprocessor.clean_text(user_query)
    intent, confidence = classifier.predict_with_confidence(cleaned)

    if intent != "general_fallback" and intent in KNOWLEDGE_BASE:
        reply = KNOWLEDGE_BASE[intent]
        source = "local_model"
    else:
        reply = gemini_fallback.get_fallback_response(user_query)
        source = "gemini_free_api"

    return jsonify({"intent": intent, "confidence": round(confidence, 2), "source": source, "response": reply})

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    
    cleaned = preprocessor.clean_text(incoming_msg)
    intent, confidence = classifier.predict_with_confidence(cleaned)

    if intent != "general_fallback" and intent in KNOWLEDGE_BASE:
        reply = KNOWLEDGE_BASE[intent]
    else:
        reply = gemini_fallback.get_fallback_response(incoming_msg)

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)