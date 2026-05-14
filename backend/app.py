import os
import uuid
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from collections import defaultdict

import services.intent_service as intent_service
from services.ner_service import ner_service
from services.ontology_service import ontology_service
from services.response_service import response_service
from services.warning_classifier_service import warning_classifier
from utils.helpers import to_camel_case

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost",
    "http://frontend",
])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()

    if not question:
        return jsonify({"error": "No message provided."}), 400

    # ── Session bootstrap ──────────────────────────────────────────────────
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    if "session_entities" not in session:
        session["session_entities"] = []

    # ── NER ────────────────────────────────────────────────────────────────
    raw_entities = ner_service.extract_entities(question)

    # Build {EntityType: [Name, ...]} for this turn — same as terminal
    current_entities = defaultdict(list)
    for entity_dict in raw_entities:
        entity_type = entity_dict['entity_type']

        if entity_dict.get('source') in ('ontology', 'custom'):
            word = entity_dict['entity']
        else:
            word = to_camel_case(entity_dict['entity'])

        current_entities[entity_type].append(word)

    # ── Follow-up context merging ──────────────────────────────────────────
    if current_entities:
        question_entities = dict(current_entities)
    elif session["session_entities"]:
        question_entities = dict(session["session_entities"][-1])
    else:
        question_entities = {}

    session["session_entities"] = (session["session_entities"][-9:] + [question_entities])
    session.modified = True

    # ── Intent + classify + response ───────────────────────────────────────
    try:
        intent = intent_service.identify_intent(question)

        classified = ner_service.classify_entities(question_entities)

        if intent == "get_warning_precautions":
            warning_result = warning_classifier.predict(question)
            if warning_result['predicted_warning_type']:
                classified['WarningType'] = [warning_result['predicted_warning_type']]
                print("WARNING CLASSIFIER RESULT", warning_result)

        entity_types = list(classified.keys())
        query_type = ner_service.identify_query_type(entity_types)

        result = intent_service.handle_intent(intent, query_type, classified)

        if result is None:
            reply = response_service.build_text_response(
                "Sorry, I couldn't understand your question. Could you please rephrase it?"
            )
        else:
            reply = result

    except (ValueError, AssertionError) as e:
        reply = response_service.build_text_response(str(e))
    except Exception as e:
        app.logger.exception("Unexpected error in /chat")
        reply = response_service.build_text_response(
            "I didn't quite get that. Can you please try rephrasing your question?"
        )

    return jsonify({
        "reply": reply,
        "session_id": session["session_id"],
        "resolved_entities": question_entities,
    })


# ---------------------------------------------------------------------------
# Clear session
# ---------------------------------------------------------------------------
@app.route("/session/clear", methods=["POST"])
def clear_session():
    session.clear()
    return jsonify({"status": "session cleared"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)