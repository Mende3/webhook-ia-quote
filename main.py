import os
from flask import Flask, request


app = Flask(__name__)

@app.route("/webhookcallback", methods=["POST"])
def hook():
    print (request.data)
    return "Hello world", 200

@app.route("/")
def home():
    return "API em flask rodando"

if __name__ == "__main__":
    port = int(os.envioron.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
