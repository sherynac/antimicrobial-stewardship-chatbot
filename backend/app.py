import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from whitenoise import WhiteNoise

# Import the skeleton services
from backend.services.intent_service import analyze_query
from services.ontology_service import get_drug_data
from services.response_service import construct_response

# Point to where Docker will put the React files ('client')
app = Flask(__name__, static_folder='client')
CORS(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='client')

@app.route('/api/consult', methods=['POST'])
def consult():
    # 1. Get Input
    data = request.json
    user_text = data.get('drug', '')

    # 2. Call Skeleton Services
    analysis = analyze_query(user_text)
    drug_data = get_drug_data(user_text)
    final_reply = construct_response(analysis['intent'], drug_data, user_text)

    # 3. Return JSON
    return jsonify({"text": final_reply})

# Serve React Frontend (Catch-All)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(port=10000)