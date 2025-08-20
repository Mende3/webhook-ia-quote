import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

load_dotenv()

endpoint = os.getenv('ENDPOINT')
model = os.getenv('MODEL_IA')
token = os.getenv('TOKEN_AI_API')

# Inicializa o cliente
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
    model=model
)
