from flask import Blueprint, request, jsonify
from utils import process_data, gen_data_json, gen_quote_ia
from pathlib import Path

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhookcallback/", methods=["POST", "OPTIONS"])
def webhook_callback() :
    if request.method == "OPTIONS":
        return jsonify({"status": "preflight ok"}), 200
    
    data = request.json
    process_data (data=data)
    file_path = Path ("clientDatas.json")
    lista_dados = gen_data_json ()
    if file_path.exists():
        file_path.unlink()
    resposta_cotaçao = gen_quote_ia (resp=lista_dados[3])

    return jsonify({"status": "ok"}), 200