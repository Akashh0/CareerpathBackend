from flask import Flask, request, jsonify
from flask_cors import CORS
from Model import generate_recommendation_from_input  # Your existing logic
import traceback

app = Flask(__name__)
CORS(app)  # Allows requests from Express/React

@app.route('/api/generate-roadmap', methods=['POST'])
def generate_roadmap():
    try:
        data = request.json
        interest = data.get('interest')
        qualification = data.get('qualification')

        if not interest or not qualification:
            return jsonify({"error": "Missing 'interest' or 'qualification' in request"}), 400

        result = generate_recommendation_from_input(interest, qualification)
        return jsonify(result), 200

    except Exception as e:
        print("❌ API Error:", e)
        traceback.print_exc()
        return jsonify({"error": "Something went wrong. Try again later."}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
