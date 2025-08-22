from flask import Blueprint, request, jsonify
from utils import process_data, gen_data_json, gen_quote_ia
from pathlib import Path
import requests

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
    resposta_cotaçao = gen_quote_ia (reqs=lista_dados[3])
    lista_dados.append(resposta_cotaçao)

    payload = {
        "email": lista_dados[0],
        "pedidos": [
            {
                "empresa": lista_dados[1],
                "numero": lista_dados[2],
                "requisicao": lista_dados[3],
                "resposta": lista_dados[6],
                "status": "pendente"
            }
        ]
    }

    djangoUrl = 'https://b33d112f4479.ngrok-free.app/app_req_logs/criar_pedidos_de_quote/'
    send = requests.post (djangoUrl, json=payload)
    print("Resposta do Django:", send.status_code, send.json())
    return jsonify({"status": "ok"}), 200
