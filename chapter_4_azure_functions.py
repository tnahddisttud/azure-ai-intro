import os
from azure.ai.agents.models import (
    AzureFunctionTool,
    AzureFunctionDefinition,
    AzureFunctionBinding,
    AzureFunctionStorageQueue,
    MessageRole,
)
from agent.client import get_client, MODEL_DEPLOYMENT_NAME
from dotenv import load_dotenv

_ = load_dotenv()

STORAGE_QUEUE_ENDPOINT = os.environ["STORAGE_QUEUE_ENDPOINT"]

AGENT_NAME = "stock-research-agent-az"

AGENT_INSTRUCTIONS = """
You are a quantitative equity analyst.
Always call get_stock_fundamentals AND search_news before forming a view.
Structure your final answer as:
  📊 Fundamentals summary
  📰 Key news (last 24 h)
  🔍 Analysis
  ✅ Recommendation: BUY / HOLD / SELL with one-line rationale
"""


def _make_queue_binding(queue_name: str) -> AzureFunctionBinding:
    return AzureFunctionBinding(
        storage_queue=AzureFunctionStorageQueue(
            queue_service_endpoint=STORAGE_QUEUE_ENDPOINT,
            queue_name=queue_name,
        )
    )


def _build_az_function_tool() -> AzureFunctionTool:
    """
    Build an AzureFunctionTool that points to cloud-hosted Azure Functions
    instead of local Python callables.

    Each tool definition wires:
      - function schema  → tells the model what the tool does and its parameters
      - input_binding    → the queue the agent drops requests into
      - output_binding   → the queue the Azure Function writes results to
    """
    return AzureFunctionTool(
        definitions=[
            AzureFunctionDefinition(
                function={
                    "name": "get_stock_fundamentals",
                    "description": (
                        "Get current stock price, P/E ratio, market cap, "
                        "and revenue growth for a ticker symbol."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "Stock ticker symbol, e.g. 'NVDA' or 'AAPL'.",
                            }
                        },
                        "required": ["ticker"],
                    },
                },
                input_binding=_make_queue_binding("get-stock-fundamentals-input"),
                output_binding=_make_queue_binding("get-stock-fundamentals-output"),
            ),
            AzureFunctionDefinition(
                function={
                    "name": "search_news",
                    "description": "Search the last 24 hours of Google News for a given query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query, e.g. 'NVIDIA earnings Q2 2025'.",
                            }
                        },
                        "required": ["query"],
                    },
                },
                input_binding=_make_queue_binding("search-news-input"),
                output_binding=_make_queue_binding("search-news-output"),
            ),
        ]
    )


def create_agent_with_azure_functions() -> str:
    """
    Create an agent backed by Azure Functions instead of local callables.
    Returns the agent_id.
    """
    az_fn_tool = _build_az_function_tool()

    with get_client() as client:
        agent = client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
            tools=az_fn_tool.definitions,
        )

        print("✅ Agent (Azure Functions) created!")
        print(f"   Name : {agent.name}")
        print(f"   ID   : {agent.id}")
        print()
        print("👉 Add to your .env file:")
        print(f"   AGENT_ID_AZ={agent.id}")

        return agent.id


def run_agent_with_azure_functions(agent_id: str, user_query: str) -> str:
    """
    Run the agent. No manual tool-call loop needed — the agent runtime
    communicates with Azure Functions via storage queues automatically.
    create_and_process handles all polling internally.
    """
    with get_client() as client:
        # Step 1: Open a fresh thread
        thread = client.threads.create()
        print(f"💬 Thread created: {thread.id}")

        # Step 2: Post the user message
        client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_query,
        )

        # Step 3: Run — polling + queue I/O handled by the SDK
        run = client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent_id,
        )
        print(f"✅ Run finished:  status={run.status}")

        if run.status == "failed":
            return f"❌ Run failed: {run.last_error}"

        # Step 4: Extract the assistant's final message
        messages = client.messages.list(thread_id=thread.id)
        return next(
            (
                msg.content[0].text.value
                for msg in list(messages)
                if msg.role == MessageRole.AGENT and msg.content
            ),
            "No response generated.",
        )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    agent_id = os.environ.get("AGENT_ID_AZ")

    if not agent_id:
        print("No AGENT_ID_AZ found — creating agent...")
        agent_id = create_agent_with_azure_functions()
        print()

    query = "Should I buy NVDA right now? Check fundamentals and recent news."

    print(f"\n{'='*60}")
    print(f"❓ {query}")
    print("=" * 60)
    print(run_agent_with_azure_functions(agent_id, query))
