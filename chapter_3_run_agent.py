import os
import json
import time
from azure.ai.agents.models import (
    FunctionTool,
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
    ToolOutput,
    MessageRole,
)
from agent.client import get_client
from tools.stock_tools import USER_FUNCTIONS

_functions = FunctionTool(functions=USER_FUNCTIONS)
POLL_INTERVAL = 1


def run_agent(agent_id: str, user_query: str) -> str:
    """
    Run an existing agent on a user query and return the assistant's answer.
    """
    with get_client() as client:
        # Step 1: Open a fresh conversation thread
        thread = client.threads.create()
        print(f"💬 Thread created: {thread.id}")

        # Step 2: Post the user's message
        client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_query,
        )

        # Step 3: Kick off the run
        run = client.runs.create(
            thread_id=thread.id,
            agent_id=agent_id,
        )
        print(f"🚀 Run started:  {run.id}  (status: {run.status})")

        # Step 4: Poll and handle tool calls
        while run.status in ("queued", "in_progress", "requires_action"):
            time.sleep(POLL_INTERVAL)
            run = client.runs.get(thread_id=thread.id, run_id=run.id)

            if run.status == "requires_action" and isinstance(
                run.required_action, SubmitToolOutputsAction
            ):
                tool_outputs = _handle_tool_calls(
                    run.required_action.submit_tool_outputs.tool_calls
                )
                client.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )

        print(f"✅ Run finished:  status={run.status}")

        # Step 5: Handle failure
        if run.status == "failed":
            return f"❌ Run failed: {run.last_error}"

        # Step 6: Extract and return the assistant's final message
        messages = client.messages.list(thread_id=thread.id)
        answer = next(
            (
                msg.content[0].text.value
                for msg in list(messages)
                if msg.role == MessageRole.AGENT and msg.content
            ),
            "No response generated.",
        )
        return answer


# helper fucntion to execute the tool calls
def _handle_tool_calls(tool_calls) -> list[ToolOutput]:
    """
    Execute each requested function tool call and collect the outputs.

    The model can request multiple tool calls in a single round-trip, so we
    iterate over them all before submitting results back.
    """
    outputs: list[ToolOutput] = []

    for call in tool_calls:
        if not isinstance(call, RequiredFunctionToolCall):
            continue

        fn_name = call.function.name
        fn_args = json.loads(call.function.arguments)
        print(f"  ⚙️  Tool call → {fn_name}({fn_args})")

        try:
            result = _functions.execute(call)
        except Exception as exc:
            result = f"Error in {fn_name}: {exc}"

        outputs.append(ToolOutput(tool_call_id=call.id, output=str(result)))

    return outputs

if __name__ == "__main__":
    agent_id = os.environ.get("AGENT_ID")

    if not agent_id:
        raise EnvironmentError(
            "AGENT_ID is not set.\n"
            "Run chapter_1_create_agent.py first, then add AGENT_ID to your .env file."
        )

    query = "Should I buy NVDA right now? Check fundamentals and recent news."

    print(f"\n{'='*60}")
    print(f"❓ {query}")
    print("=" * 60)
    print(run_agent(agent_id, query))
