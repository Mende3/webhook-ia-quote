import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/webhookcallback/", methods=["POST", "OPTIONS"])
def hook():
    if request.method == "OPTIONS":
        return jsonify({"status": "preflight ok"}), 200
    
    data = request.json
    print("recebi:", data)
    return jsonify({"status": "ok"}), 200

@app.route("/") 
def home():
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

