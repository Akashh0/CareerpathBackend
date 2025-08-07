# model_api.py
from flask import Flask, request, jsonify
from Model import generate_recommendation_from_input
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # So Express frontend can call it

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    interest = data.get("interest", "")
    qualification = data.get("qualification", "")
    
    try:
        result = generate_recommendation_from_input(interest, qualification)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)