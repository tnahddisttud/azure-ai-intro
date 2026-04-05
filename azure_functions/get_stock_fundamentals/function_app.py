import json
import logging
import azure.functions as func
import yfinance as yf

app = func.FunctionApp()


@app.function_name("get_stock_fundamentals")
@app.queue_trigger(
    arg_name="msg",
    queue_name="get-stock-fundamentals-input",
    connection="AzureWebJobsStorage",
)
@app.queue_output(
    arg_name="outputQueue",
    queue_name="get-stock-fundamentals-output",
    connection="AzureWebJobsStorage",
)
def get_stock_fundamentals(msg: func.QueueMessage, outputQueue: func.Out[str]) -> None:
    """
    Queue-triggered Azure Function.

    The Azure AI Agent drops a JSON payload into the input queue when it needs
    stock fundamentals. This function processes the request and writes the
    result to the output queue, which the agent picks up automatically.

    Input payload schema (set by the agent runtime):
        {
            "tool_call_id": "<id>",
            "arguments": { "ticker": "NVDA" }
        }
    """
    payload = json.loads(msg.get_body().decode("utf-8"))
    tool_call_id: str = payload["tool_call_id"]

    ticker: str = payload["arguments"]["ticker"]
    logging.info("get_stock_fundamentals called for ticker=%s", ticker)

    stock = yf.Ticker(ticker)
    info = stock.info

    result = {
        "price":          info.get("currentPrice"),
        "pe_ratio":       info.get("trailingPE"),
        "market_cap":     info.get("marketCap"),
        "revenue_growth": info.get("revenueGrowth"),
        "52w_high":       info.get("fiftyTwoWeekHigh"),
        "52w_low":        info.get("fiftyTwoWeekLow"),
    }

    # Write result back to the output queue — the agent reads from here
    outputQueue.set(json.dumps({
        "tool_call_id": tool_call_id,
        "output": json.dumps(result),
    }))
