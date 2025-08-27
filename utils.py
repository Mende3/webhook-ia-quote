import json
import pandas as pd
from pathlib import Path
from azure.ai.inference.models import SystemMessage, UserMessage
from brain import client
import logging
from datetime import datetime
from flask import Flask
from flask_mail import Mail, Message

# Configuração do Flask e Mail
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'adc56b8b0123b5'
app.config['MAIL_PASSWORD'] = '088b7abaab1c20'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

DEV_EMAIL = "devsmalldev@gmail.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(subject, message_body, level="INFO"):
    """Envia email usando Mailtrap"""
    try:
        with app.app_context():
            msg = Message(
                subject=f"[{level}] {subject}",
                sender="sistema@exemplo.com",
                recipients=[DEV_EMAIL]
            )
            msg.body = message_body
            mail.send(msg)
            logger.info(f"Email enviado para {DEV_EMAIL}")
            return True
    except Exception as e:
        logger.error(f"Erro ao enviar email: {str(e)}")
        return False

def log_utils(level, message, data=None):
    """Função de log para utils.py com notificação por email"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {level}: {message}"
    
    if data:
        log_msg += f"\n      Dados: {data}"
    
    print(log_msg)
    
    # Enviar email para erros
    if level == "ERROR":
        email_subject = f"ERRO no sistema: {message[:50]}..."
        email_body = f"""
        ALERTA DE ERRO
        
        Hora: {timestamp}
        Nível: {level}
        Mensagem: {message}
        
        Dados relacionados:
        {json.dumps(data, indent=2, ensure_ascii=False) if data else 'Nenhum dado adicional'}
        
        ---
        Sistema de Notificações Automáticas
        """
        send_email(email_subject, email_body, "ERROR")
    
    # Enviar email para sucessos importantes
    elif level == "INFO" and any(keyword in message.lower() for keyword in 
                               ["sucesso", "completado", "finalizado", "concluído", "salvo", "extraído"]):
        email_subject = f"✅ SUCESSO: {message[:50]}..."
        email_body = f"""
        ✅ OPERAÇÃO BEM-SUCEDIDA
        
        Hora: {timestamp}
        Mensagem: {message}
        
        Dados relacionados:
        {json.dumps(data, indent=2, ensure_ascii=False) if data else 'Nenhum dado adicional'}
        
        ---
        Sistema de Notificações Automáticas
        """
        send_email(email_subject, email_body, "SUCCESS")

def process_data(data: dict) -> dict:
    try:
        with open("clientDatas.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        log_utils("INFO", "Dados processados e salvos com sucesso no clientDatas.json")
        return {"status": "saved"}
    except Exception as e:
        log_utils("ERROR", f"Erro ao salvar dados no clientDatas.json: {str(e)}", {"error_details": str(e)})
        raise

def gen_data_json():
    try:
        log_utils("INFO", "Iniciando leitura e processamento do clientDatas.json")
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
            
            log_utils("INFO", "Dados extraídos com sucesso do clientDatas.json", {
                "email": email,
                "empresa": empresa,
                "numero": numero,
                "conteudo_tamanho": len(conteudo) if conteudo else 0,
                "data_extraida": date_ISO_8601,
                "hora_extraida": hora
            })
            
            return result
            
    except Exception as e:
        log_utils("ERROR", f"Erro ao gerar dados JSON do clientDatas.json: {str(e)}", {"error_details": str(e)})
        raise

def gen_quote_ia(reqs):
    try:
        log_utils("INFO", "Iniciando geração de cotação IA")
        log_utils("DEBUG", "Requisição recebida para cotação", {"request_preview": reqs[:100] + "..." if len(reqs) > 100 else reqs})
        
        file_excel_path = Path("base/base.xlsx")
        log_utils("INFO", f"Lendo arquivo Excel: {file_excel_path}")

        # Lê todas as abas de uma vez
        dfs = pd.read_excel(file_excel_path, sheet_name=None)
        log_utils("INFO", f"Abas encontradas no Excel: {list(dfs.keys())}")

        produtos = dfs.get("produtos e serviços", pd.DataFrame())
        fornecedores = dfs.get("fornecedores", pd.DataFrame())
        
        log_utils("INFO", f"Produtos carregados: {len(produtos)} registros")
        log_utils("INFO", f"Fornecedores carregados: {len(fornecedores)} registros")

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

        log_utils("DEBUG", "Prompt final preparado para IA")

        # Construção da mensagem
        messages = [
            SystemMessage(content=prompt_final),
            UserMessage(content=reqs)
        ]

        log_utils("INFO", "Enviando requisição para API de IA...")
        
        # Envia requisição de chat
        response = client.complete(
            messages=messages,
            temperature=0.8,
            max_tokens=2048
        )

        log_utils("INFO", "Resposta da IA recebida com sucesso")

        # Retorna resposta da IA (com fallback)
        if response.choices and response.choices[0].message:
            resposta = response.choices[0].message.content
            log_utils("INFO", f"Cotação IA gerada com sucesso - Tamanho: {len(resposta)} caracteres")
            log_utils("DEBUG", "Preview da resposta IA", {"preview": resposta[:200] + "..." if len(resposta) > 200 else resposta})
            
            # Email de sucesso para geração de cotação
            email_subject = "✅ Cotação IA gerada com sucesso"
            email_body = f"""
            COTAÇÃO IA FINALIZADA
            
            Hora da geração: {datetime.now().strftime("%H:%M:%S")}
            Tamanho da resposta: {len(resposta)} caracteres
            Requisição inicial: {reqs[:100]}...
            
            Preview da cotação:
            {resposta[:500]}...
            
            ---
            Sistema de Cotações Automáticas
            """
            send_email(email_subject, email_body, "SUCCESS")
            
        else:
            resposta = "Nenhuma resposta gerada pela IA."
            log_utils("WARNING", "Nenhuma resposta gerada pela IA para a cotação")
        
        return resposta
        
    except Exception as e:
        error_details = {
            "error_message": str(e),
            "request_preview": reqs[:100] + "..." if len(reqs) > 100 else reqs if reqs else "Nenhuma requisição"
        }
        log_utils("ERROR", f"Erro crítico na geração de cotação IA: {str(e)}", error_details)
        raise