import json
import pandas as pd
from pathlib import Path
from azure.ai.inference.models import SystemMessage, UserMessage
from brain import client
import logging
from datetime import datetime

# Configurar logging
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
        log_utils("INFO", "Salvando dados do cliente em clientDatas.json")
        with open("clientDatas.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        log_utils("INFO", "Dados salvos com sucesso")
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
        log_utils("INFO", "Iniciando geração de cotação IA")
        log_utils("DEBUG", "Requisição recebida", reqs[:100] + "..." if len(reqs) > 100 else reqs)
        
        file_excel_path = Path("base/base.xlsx")
        log_utils("INFO", f"Lendo arquivo Excel: {file_excel_path}")

        # Lê todas as abas de uma vez
        dfs = pd.read_excel(file_excel_path, sheet_name=None)
        log_utils("INFO", f"Abas encontradas: {list(dfs.keys())}")

        produtos = dfs.get("produtos e serviços", pd.DataFrame())
        fornecedores = dfs.get("fornecedores", pd.DataFrame())
        
        log_utils("INFO", f"Produtos: {len(produtos)} registros")
        log_utils("INFO", f"Fornecedores: {len(fornecedores)} registros")

        # Converte DataFrames em JSON legível
        produtos_json = produtos.to_dict(orient="records")
        fornecedores_json = fornecedores.to_dict(orient="records")

        with open("prompt.txt", "r", encoding="utf-8") as prompt_file:
            prompt_base = prompt_file.read()
        
        log_utils("INFO", "Prompt base lido com sucesso")

        prompt_final = prompt_base.format(
            produtos=json.dumps(produtos_json, ensure_ascii=False, indent=2),
            fornecedores=json.dumps(fornecedores_json, ensure_ascii=False, indent=2)
        )

        log_utils("DEBUG", "Prompt final preparado")

        # Construção da mensagem
        messages = [
            SystemMessage(content=prompt_final),
            UserMessage(content=reqs)
        ]

        log_utils("INFO", "Enviando requisição para IA...")
        
        # Envia requisição de chat
        response = client.complete(
            messages=messages,
            temperature=0.8,
            max_tokens=2048
        )

        log_utils("INFO", "Resposta da IA recebida")

        # Retorna resposta da IA (com fallback)
        if response.choices and response.choices[0].message:
            resposta = response.choices[0].message.content
            log_utils("INFO", f"Resposta IA gerada ({len(resposta)} caracteres)")
            log_utils("DEBUG", "Resposta IA (início)", resposta[:200] + "..." if len(resposta) > 200 else resposta)
        else:
            resposta = "Nenhuma resposta gerada pela IA."
            log_utils("WARNING", "Nenhuma resposta gerada pela IA")
        
        return resposta
        
    except Exception as e:
        log_utils("ERROR", f"Erro na geração de cotação IA: {str(e)}")
        raise