from flask import Blueprint, request, jsonify
from utils import process_data, gen_data_json, gen_quote_ia, send_email
from pathlib import Path
import requests
import traceback
from datetime import datetime

webhook_bp = Blueprint("webhook", __name__)

def log_webhook(level, message, data=None):
    """Função de log para webhook"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {level}: {message}"
    if data:
        log_msg += f"\n      Dados: {data}"
    print(log_msg)

@webhook_bp.route("/webhookcallback/", methods=["POST", "OPTIONS"])
def webhook_callback():
    try:        
        if request.method == "OPTIONS":
            log_webhook("INFO", "Requisição OPTIONS (preflight) recebida")
            return jsonify({"status": "preflight ok"}), 200
        
        log_webhook("INFO", "Requisição POST recebida")
        log_webhook("DEBUG", "Headers", dict(request.headers))
        
        data = request.json
        if not data:
            log_webhook("WARNING", "Dados JSON vazios ou None")
            return jsonify({"error": "Empty JSON data"}), 400
        
        process_data(data=data)
        log_webhook("INFO", "Dados processados com sucesso")
        
        lista_dados = gen_data_json()
        log_webhook("INFO", "Dados JSON gerados", {
            "email": lista_dados[0],
            "empresa": lista_dados[1],
            "numero": lista_dados[2],
            "conteudo_tamanho": len(lista_dados[3])
        })
        
        file_path = Path("clientDatas.json")
        if file_path.exists():
            file_path.unlink()
            log_webhook("INFO", "Arquivo clientDatas.json removido")
        else:
            log_webhook("INFO", "Arquivo clientDatas.json não existia")
        
        resposta_cotacao = gen_quote_ia(
            email=lista_dados[0],
            company=lista_dados[1],
            number=lista_dados[2],
            reqs=lista_dados[3],
            date=lista_dados[4],
            time=lista_dados[5]
        )
        lista_dados.append(resposta_cotacao)
        log_webhook("INFO", "Cotação IA adicionada aos dados")
        
        payload = {
            "email": lista_dados[0],
            "pedidos": [
                {
                    "empresa": lista_dados[1],
                    "numero": lista_dados[2],
                    "requisicao": lista_dados[3],
                    "resposta": lista_dados[6],
                    "data": lista_dados[4],
                    "hora": lista_dados[5],
                    "status": "pendente"
                }
            ]
        }
        
        log_webhook("INFO", "Payload preparado para Django")
        log_webhook("DEBUG", "Payload completo", payload)
        
        djangoUrl = 'https://rcs-hackthon-django.onrender.com/app_req_logs/criar_pedidos_de_quote/'
        send = requests.post(djangoUrl, json=payload)
        log_webhook("INFO", f"Resposta do Django: {send.status_code}")
        
        if send.status_code == 201 :
            log_webhook("INFO", "=== WEBHOOK CONCLUÍDO COM SUCESSO ===")
            send_email (
                "sucesso na requisição",
                lista_dados[0],
                lista_dados[1],
                lista_dados[3],
                lista_dados[4],
                lista_dados[5]
                )
            return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        log_webhook("ERROR", f"ERRO NO WEBHOOK: {str(e)}")
        log_webhook("DEBUG", "Traceback completo", traceback.format_exc())
        send_email_error ("ERRO NO WEBHOOK", date=None, time=None, tipo=0)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
