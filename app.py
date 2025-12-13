from flask import Flask, request, jsonify,render_template
from utils.agent import ai_agent
from flask_cors import CORS
import os ,io

app = Flask(__name__, template_folder='templates')

CORS(app)  

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    user_query = data.get("query")

    result = ai_agent(user_query)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
