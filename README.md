# AI Agents on Azure AI Foundry — Workshop

A hands-on Python workshop for SWEs covering how to build, deploy, and run AI agents using **Azure AI Foundry** and the `azure-ai-agents` SDK.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.11+ | Managed via `.python-version` / `uv` |
| Azure subscription | With an AI Foundry project |
| `az login` done | `DefaultAzureCredential` reads from the CLI session |
| SerpAPI key | For the live news search tool |

### Install dependencies

```bash
uv sync          # or: pip install -e .
```

### Configure environment

Copy the values into `.env`:

```env
PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
SERPAPI_API_KEY=<your-serpapi-key>

# Filled in after running Chapter 1:
# AGENT_ID=
```

---

## Workshop Chapters

### Chapter 1 — Create an Agent with Tools

```bash
python chapter_1_create_agent.py
```

- Registers a **persistent** agent in Foundry with two function tools:
  - `get_stock_fundamentals` — live price, P/E, market cap via `yfinance`
  - `search_news` — Google News (last 24 h) via SerpAPI
- Prints the `agent_id` — **copy it into your `.env` file** as `AGENT_ID=...`

> **Key concept:** Create the agent *once*. Reuse it forever.

---

### Chapter 2 — Fetch the Agent from Foundry

```bash
python chapter_2_fetch_agent.py
```

- Calls `client.get_agent(agent_id)` to retrieve the existing agent.
- No quota consumed, no new resource created.
- Prints name, model, and registered tools for inspection.

> **Key concept:** `get_agent` vs `create_agent` — prefer fetch in production.

---

### Chapter 3 — Run the Agent

```bash
python chapter_3_run_agent.py
```

- Opens a **fresh thread** (conversation session) for each query.
- Posts the user message, starts a run, polls for completion.
- Handles **tool calls** mid-run (function calling loop).
- Returns and prints the assistant's structured analysis.

> **Key concept:** Agent (persistent brain) ≠ Thread (ephemeral conversation).

---

### Full end-to-end demo

```bash
python main.py
```

Runs all three chapters in sequence.  If `AGENT_ID` is already in `.env`, it skips Chapter 1.

---

## Project Structure

```
azure-ai-intro/
├── agent/
│   ├── __init__.py
│   └── client.py               # Shared AgentsClient factory
├── tools/
│   └── stock_tools.py          # get_stock_fundamentals + search_news
├── chapter_1_create_agent.py   # Workshop: Chapter 1
├── chapter_2_fetch_agent.py    # Workshop: Chapter 2
├── chapter_3_run_agent.py      # Workshop: Chapter 3
├── main.py                     # End-to-end orchestrator
├── minimal_agent.py            # Simplest possible agent (no tools)
└── .env                        # Environment variables
```
