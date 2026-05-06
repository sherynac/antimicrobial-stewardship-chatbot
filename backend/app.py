import os
import uuid
from flask import Flask, request, jsonify, session
from flask_cors import CORS

import services.intent_service as intent_service
import services.entities_service as entities_service
from services.response_service import response_service
from utils.helpers import get_splitted_question

app = Flask(__name__)

# Secret key for signing session cookies — override via SECRET_KEY env var in production
app.secret_key = os.environ.get("SECRET_KEY", "ophiuchus-dev-secret-change-in-prod")

# Allow credentials (cookies) from the React dev server and the nginx-served frontend
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",   # Vite dev server
    "http://localhost:3000",   # alternative dev port
    "http://localhost",        # nginx in Docker
    "http://frontend",         # Docker service name
])

# Pre-load entity list once at startup (reads the OWL ontology — expensive)
_entities_cache = entities_service.fill_entities()


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
    # Flask's built-in session is cookie-based and signed with secret_key.
    # We keep a rolling history of entity dicts so follow-up questions can
    # reuse context when the current question supplies no entities.
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    # session_entities: list of {EntityType: [names]} dicts, one per turn
    if "session_entities" not in session:
        session["session_entities"] = []

    # ── NER ────────────────────────────────────────────────────────────────
    words = get_splitted_question(question)
    raw_entities = entities_service.look_up_entity(words)

    # Build {EntityType: [Name, ...]} for this turn
    current_entities: dict = {}
    for word, entity_type in raw_entities.items():
        current_entities.setdefault(entity_type, []).append(word.capitalize())

    # ── Follow-up context merging ──────────────────────────────────────────
    # If the current question has NO entities at all, reuse the entire last
    # turn's resolved entities (e.g. "What about its side effects?").
    # If there ARE some entities but a key type is missing, fill the gap
    # from the most-recent turn that had it (e.g. "What about amoxicillin?"
    # where the prior turn already established a Brand name).
    if not current_entities and session["session_entities"]:
        question_entities = dict(session["session_entities"][-1])
    else:
        question_entities = dict(current_entities)
        for past in reversed(session["session_entities"]):
            for etype, names in past.items():
                if etype not in question_entities:
                    question_entities[etype] = names

    # Persist this turn's entities to history (keep last 10 turns)
    session["session_entities"] = session["session_entities"][-9:] + [current_entities]
    session.modified = True  # tell Flask the mutable dict was changed

    # ── Intent + response ──────────────────────────────────────────────────
    try:
        intent = intent_service.identify_intent(question)
        query_type = intent_service.identify_entities_present(question_entities.keys())

        result = intent_service.handle_intent(intent, query_type, question_entities)

        if result is None:
            reply = "Sorry, I couldn't understand your question. Could you please rephrase it?"
        elif isinstance(result, dict):
            reply = result.get("text") or str(result)
        else:
            reply = str(result)

    except (ValueError, AssertionError) as e:
        reply = str(e)
    except Exception as e:
        app.logger.exception("Unexpected error in /chat")
        reply = "An unexpected error occurred. Please try again."

    return jsonify({
        "reply": reply,
        "session_id": session["session_id"],
        "resolved_entities": question_entities,
    })


# ---------------------------------------------------------------------------
# Clear session endpoint — called when user clicks "Clear Chat"
# ---------------------------------------------------------------------------
@app.route("/session/clear", methods=["POST"])
def clear_session():
    session.clear()
    return jsonify({"status": "session cleared"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)