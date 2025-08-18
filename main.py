import os
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/webhookcallback", methods=["POST"])
def hook():
    print(request.data)  # Isso vai para os logs do Render
    return "Hello world", 200

@app.route("/")  # Rota básica para testar se está vivo
def home():
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render define a porta
    app.run(host="0.0.0.0", port=port)

