from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ENDPOINT      = os.environ["PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT_NAME = os.environ["MODEL_DEPLOYMENT_NAME"]

agents_client = AgentsClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

with agents_client:
    agent = agents_client.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name="simple-agent",
        instructions="You are a concise financial educator.",
    )

    thread = agents_client.threads.create()

    agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content="What should I know before investing in semiconductor stocks?",
    )

    # create_and_process handles polling automatically — no manual loop needed
    run = agents_client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )
    print(f"Run status: {run.status}")

    # Print conversation in chronological order
    messages = agents_client.messages.list(thread_id=thread.id)
    for msg in reversed(list(messages)):
        role = msg.role.upper()
        text = msg.content[0].text.value if msg.content else ""
        print(f"\n[{role}]\n{text}")

    agents_client.delete_agent(agent.id)