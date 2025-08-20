import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from routes import webhook_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(webhook_bp)

@app.route("/") 
def home():
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

