import json
import pandas as pd
from pathlib import Path
from azure.ai.inference.models import SystemMessage, UserMessage
from brain import client
import logging
from datetime import datetime

from mailersend import MailerSendClient, EmailBuilder

import os
from dotenv import load_dotenv

load_dotenv ()

api_key_mailersend = os.getenv('API_KEY_MAILERSEND')
ms = MailerSendClient (api_key_mailersend)
domain = 'MS_fLx9MZ@test-r6ke4n1m809gon12.mlsender.net'
meu_email = 'tquote265@gmail.com'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_utils(level, message, data=None):
    """Função de log para utils.py"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {level}: {message}"
    if data:
        log_msg += f"\n      Dados: {data}"
    print(log_msg)

def process_data(data: dict) -> dict:
    try:
        with open("clientDatas.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return {"status": "saved"}
    except Exception as e:
        log_utils("ERROR", f"Erro ao salvar dados: {str(e)}")
        raise

def gen_data_json():
    try:
        log_utils("INFO", "Lendo e processando clientDatas.json")
        with open("clientDatas.json", "r", encoding="utf-8") as file:
            datas = json.load(file)
            client_datas = datas.get("clientData", {})

            email = client_datas.get("email", "email não existe")
            empresa = client_datas.get("company", "company não existe")
            numero = client_datas.get("number", "number não existe")
            
            conteudo = datas.get("content", "content não existe")
            dateTime = datas.get("timestamp", "timestamp não existe")

            partes = dateTime.split(",")  
            data = partes[0].strip() if len(partes) > 0 else "sem data"
            hora = partes[1].strip() if len(partes) > 1 else "sem hora"

            [dd, mm, yy] = data.split('/')
            date_ISO_8601 = f"{yy}-{mm}-{dd}"

            result = [email, empresa, numero, conteudo, date_ISO_8601, hora]
            log_utils("INFO", "Dados extraídos com sucesso", {
                "email": email,
                "empresa": empresa,
                "numero": numero,
                "conteudo_tamanho": len(conteudo) if conteudo else 0
            })
            
            return result
            
    except Exception as e:
        log_utils("ERROR", f"Erro ao gerar dados JSON: {str(e)}")
        raise

def gen_quote_ia(reqs):
    try:        
        file_excel_path = Path("base/base.xlsx")
        log_utils("INFO", f"Lendo arquivo Excel: {file_excel_path}")

        dfs = pd.read_excel(file_excel_path, sheet_name=None)

        produtos = dfs.get("produtos e serviços", pd.DataFrame())
        fornecedores = dfs.get("fornecedores", pd.DataFrame())
        
        # Converte DataFrames em JSON legível
        produtos_json = produtos.to_dict(orient="records")
        fornecedores_json = fornecedores.to_dict(orient="records")

        with open("prompt.txt", "r", encoding="utf-8") as prompt_file:
            prompt_base = prompt_file.read()
        

        prompt_final = prompt_base.format(
            produtos=json.dumps(produtos_json, ensure_ascii=False, indent=2),
            fornecedores=json.dumps(fornecedores_json, ensure_ascii=False, indent=2)
        )

        messages = [
            SystemMessage(content=prompt_final),
            UserMessage(content=reqs)
        ]

        # Envia requisição de chat
        response = client.complete(
            messages=messages,
            temperature=0.8,
            max_tokens=2048
        )

        log_utils("INFO", "Resposta da IA recebida")

        if response.choices and response.choices[0].message:
            resposta = response.choices[0].message.content
        else:
            log_utils("WARNING", "Nenhuma resposta gerada pela IA")
            return ()
        
        return resposta
        
    except Exception as e:
        log_utils("ERROR", f"Erro na geração de cotação IA: {str(e)}")
        raise
    

def send_email(sms, to, company, req, date, time):

    # corpo HTML mais apresentável
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.5;">
            <h2>{sms}</h2>
            <p><strong>Cliente:</strong> {company} ({to})</p>
            <p><strong>Pedido de cotação:</strong><br>{req}</p>
            <p><strong>Data/Hora:</strong> {date} {time}</p>
            <hr>
            <p style="color: gray; font-size: 0.9em;">
                Este é um envio automático de cotações pelo sistema RCS.
            </p>
        </body>
    </html>
    """
    
    text_content = f"""
    {sms}

    Cliente: {company} ({to})
    Pedido de cotação:
    {req}

    Data/Hora: {date} {time}

    Geração automática de cotações - RCS
    """

    # construir e enviar email
    email = (EmailBuilder()
             .from_email(domain, "RCS Emails")
             .to_many([{"email": meu_email, "name": "Cliente"}])
             .subject(sms)
             .html(html_content)
             .text(text_content)
             .build()
             )
    
    ms.emails.send(email)
