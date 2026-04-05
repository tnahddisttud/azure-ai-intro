import os
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

_ = load_dotenv()

PROJECT_ENDPOINT: str = os.environ["PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT_NAME: str = os.environ["MODEL_DEPLOYMENT_NAME"]


def get_client() -> AgentsClient:
    """Return a configured AgentsClient using DefaultAzureCredential."""
    return AgentsClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
