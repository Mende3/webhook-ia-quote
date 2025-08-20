import os
from dotenv import load_dotenv

# Carrega variáveis do .env (em ambiente local)
load_dotenv()

# Importa client da Azure AI Inference
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-5-nano"
token = os.environ["GITHUB_TOKEN"]

# Inicializa cliente
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)