import json

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
    
def gen_quote_ia(resp) :
    pass