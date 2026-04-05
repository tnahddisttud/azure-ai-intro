import json
import logging
import os
import azure.functions as func
from langchain_community.utilities import SerpAPIWrapper

app = func.FunctionApp()

_serp = SerpAPIWrapper(
    serpapi_api_key=os.environ["SERPAPI_API_KEY"],
    params={
        "tbm": "nws",    # Google News tab
        "tbs": "qdr:d",  # Last 24 hours
    },
)


@app.function_name("search_news")
@app.queue_trigger(
    arg_name="msg",
    queue_name="search-news-input",
    connection="AzureWebJobsStorage",
)
@app.queue_output(
    arg_name="outputQueue",
    queue_name="search-news-output",
    connection="AzureWebJobsStorage",
)
def search_news(msg: func.QueueMessage, outputQueue: func.Out[str]) -> None:
    """
    Queue-triggered Azure Function.

    The Azure AI Agent drops a JSON payload into the input queue when it needs
    news results. This function runs the SerpAPI search and writes the result
    to the output queue, which the agent picks up automatically.

    Input payload schema (set by the agent runtime):
        {
            "tool_call_id": "<id>",
            "arguments": { "query": "NVIDIA earnings Q2 2025" }
        }
    """
    payload = json.loads(msg.get_body().decode("utf-8"))
    tool_call_id: str = payload["tool_call_id"]

    query: str = payload["arguments"]["query"]
    logging.info("search_news called for query=%r", query)

    result = _serp.run(query)

    # Write result back to the output queue — the agent reads from here
    outputQueue.set(json.dumps({
        "tool_call_id": tool_call_id,
        "output": result,
    }))
