from flask import Flask, request, jsonify
from flask_cors import CORS
from Model import generate_recommendation_from_input
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://career-path-recommender-orpin.vercel.app"}})

@app.route('/api/generate-roadmap', methods=['POST'])
def generate_roadmap():
    try:
        data = request.get_json()
        user_interest = data.get("interest")
        user_qualification = data.get("qualification")
        response = generate_recommendation_from_input(user_interest, user_qualification)
        return jsonify(response)
    except Exception as e:
        print("ERROR:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def health():
    return "Backend running!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
