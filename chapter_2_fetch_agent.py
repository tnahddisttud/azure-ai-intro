import os
from azure.ai.agents.models import Agent
from agent.client import get_client


def fetch_agent(agent_id: str) -> Agent:
    """
    Fetch an existing agent from Azure AI Foundry by its ID.
    """
    with get_client() as client:
        agent = client.get_agent(agent_id)

        print("🔍 Agent fetched from Foundry:")
        print(f"   Name        : {agent.name}")
        print(f"   ID          : {agent.id}")
        print(f"   Model       : {agent.model}")
        print(f"   Tools       : {[t.get('function', {}).get('name') for t in (agent.tools or [])]}")

        return agent


if __name__ == "__main__":
    agent_id = os.environ.get("AGENT_ID")

    if not agent_id:
        raise EnvironmentError(
            "AGENT_ID is not set.\n"
            "Run chapter_1_create_agent.py first, then add AGENT_ID to your .env file."
        )

    fetch_agent(agent_id)
