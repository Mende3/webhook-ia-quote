import os
from flask import Flask, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/webhookcallback", methods=["POST"])
def hook():
    print(request.data)
    return "Hello world", 200

@app.route("/") 
def home():
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

