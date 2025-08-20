import json
import pandas as pd
from pathlib import Path
from azure.ai.inference.models import SystemMessage, UserMessage

from brain import client

def process_data (data: dict) -> dict :
    with open ("clientDatas.json", "w", encoding="utf-8") as file:
        json.dump (data, file, indent=4, ensure_ascii=False)
    return {"status": "saved"}

def gen_data_json () :
    with open ("clientDatas.json", "r", encoding="utf-8") as file:
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

        [dd, mm, yy] = data.split ('/')
        date_ISO_8601 = f"{yy}-{mm}-{dd}"

        return [
            email,
            empresa,
            numero,
            conteudo,
            date_ISO_8601,
            hora,
        ]
    
def gen_quote_ia(reqs):
    file_excel_path = Path("base/base.xlsx")

    # Lê todas as abas de uma vez
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

    # Construção da mensagem
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

    # Retorna resposta da IA (com fallback)
    if response.choices and response.choices[0].message:
        resposta = response.choices[0].message.content
    else:
        resposta = "Nenhuma resposta gerada pela IA."
        
    return resposta

