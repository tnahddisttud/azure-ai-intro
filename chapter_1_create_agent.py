from azure.ai.agents.models import FunctionTool
from agent.client import get_client, MODEL_DEPLOYMENT_NAME
from tools.stock_tools import USER_FUNCTIONS


AGENT_NAME = "stock-research-agent"

AGENT_INSTRUCTIONS = """
You are a quantitative equity analyst.
Always call get_stock_fundamentals AND search_news before forming a view.
Structure your final answer as:
  📊 Fundamentals summary
  📰 Key news (last 24 h)
  🔍 Analysis
  ✅ Recommendation: BUY / HOLD / SELL with one-line rationale
"""


def create_agent() -> str:
    """
    Create a new agent in Azure AI Foundry and return its agent_id.
    """
    functions = FunctionTool(functions=USER_FUNCTIONS)

    with get_client() as client:
        agent = client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
            tools=functions.definitions,
        )

        print("✅ Agent created successfully!")
        print(f"   Name  : {agent.name}")
        print(f"   ID    : {agent.id}")
        print()
        print("👉 Add the following line to your .env file:")
        print(f'   AGENT_ID={agent.id}')

        return agent.id


if __name__ == "__main__":
    create_agent()
