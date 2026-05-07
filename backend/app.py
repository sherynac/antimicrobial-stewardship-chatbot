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
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

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
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    # session_entities: list of {EntityType: [names]} dicts, one per turn
    if "session_entities" not in session:
        session["session_entities"] = []

    # ── NER ────────────────────────────────────────────────────────────────
    words = get_splitted_question(question)
    raw_entities = entities_service.look_up_entity(words, question)

    # Build {EntityType: [Name, ...]} for this turn
    current_entities: dict = {}
    for word, entity_type in raw_entities.items():
        current_entities.setdefault(entity_type, []).append(word.capitalize())

    # ── Follow-up context merging ──────────────────────────────────────────
    # Rule 1: Current question has entities → it's a NEW topic.
    #         Use only what the user just said. Never pull from history.
    #
    # Rule 2: Current question has NO entities → it's a follow-up
    #         (e.g. "What about its side effects?", "Tell me more").
    #         Reuse the full resolved context from the previous turn.
    if current_entities:
        # New topic — use only current turn's entities
        question_entities = dict(current_entities)
    elif session["session_entities"]:
        # Pure follow-up — clone last turn's resolved entities
        question_entities = dict(session["session_entities"][-1])
    else:
        # No entities and no history — nothing to work with
        question_entities = {}

    # Persist this turn's RESOLVED entities to history (keep last 10 turns).
    # We store question_entities (not current_entities) so that follow-up
    # chains always have a non-empty context to inherit from.
    session["session_entities"] = (session["session_entities"][-9:] + [question_entities])
    session.modified = True  # required: Flask won't auto-detect mutations in nested lists

    # ── Intent + response ──────────────────────────────────────────────────
    try:
        intent = intent_service.identify_intent(question)
        query_type = intent_service.identify_entities_present(question_entities.keys())

        result = intent_service.handle_intent(intent, query_type, question_entities)

        if result is None:
            reply = "Sorry, I couldn't understand your question. Could you please rephrase it?"
        elif isinstance(result, (dict, list)):
            reply = result
        else:
            reply = str(result)

    except (ValueError, AssertionError) as e:
        reply = str(e)
    except Exception as e:
        app.logger.exception("Unexpected error in /chat")
        reply = "I didn't quite get that. Can you please try rephrasing your question?"

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