import ssl
import httpx
from langchain_openai.chat_models import AzureChatOpenAI
import os

from dotenv import load_dotenv

load_dotenv()

def create_openai_chat_client(model, config, model_version=None, api_version='2024-10-21', **kwargs):

    api_key = os.environ.get("OPENAI_API_KEY")
    WMT_CA_PATH = os.environ.get("WMT_CA_PATH")
    end_point = config.get("llm_url")


    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    # Build a custom client with Walmart CAs and Headers built into it
    context = ssl.create_default_context()
    context.load_verify_locations(WMT_CA_PATH)
    client = httpx.Client(verify=context, headers=headers)
    async_client = httpx.AsyncClient(verify=context, headers=headers)

    llm_chat = AzureChatOpenAI(openai_api_key="<ignored>",
                               model=model if model_version is None else f"{model}@{model_version}",
                               api_version=api_version,
                               azure_endpoint=end_point,
                               http_client=client,
                               http_async_client=async_client,
                               **kwargs)
    
    return llm_chat