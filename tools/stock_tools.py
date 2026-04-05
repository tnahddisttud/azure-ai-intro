# tools/stock_tools.py

import os
import yfinance as yf
from langchain_community.utilities import SerpAPIWrapper
from dotenv import load_dotenv

_ = load_dotenv()
# ── Tool 1: Stock Fundamentals ─────────────────────────────────────────────

def get_stock_fundamentals(ticker: str) -> dict:
    """
    Get current stock price, P/E ratio, market cap, and revenue growth for a ticker.

    Args:
        ticker: The stock ticker symbol (e.g., 'AAPL', 'NVDA').

    Returns:
        A dictionary with price, pe_ratio, market_cap, revenue_growth,
        52w_high, and 52w_low. Values may be None if unavailable.
    """
    stock = yf.Ticker(ticker)
    info  = stock.info
    return {
        "price":          info.get("currentPrice"),
        "pe_ratio":       info.get("trailingPE"),
        "market_cap":     info.get("marketCap"),
        "revenue_growth": info.get("revenueGrowth"),
        "52w_high":       info.get("fiftyTwoWeekHigh"),
        "52w_low":        info.get("fiftyTwoWeekLow"),
    }


# ── Tool 2: Recent News Search ─────────────────────────────────────────────

_serp = SerpAPIWrapper(
    serpapi_api_key=os.environ["SERPAPI_API_KEY"],
    params={
        "tbm": "nws",   # Google News tab
        "tbs": "qdr:d", # Last 24 hours
    },
)

def search_news(query: str) -> str:
    """
    Search the last 24 hours of Google News for a given query.

    Args:
        query: A natural-language search query (e.g., 'NVIDIA earnings Q2 2025').

    Returns:
        A formatted string of news headlines and URLs.
    """
    return _serp.run(query)


# ── Export as a callable set ───────────────────────────────────────────────
USER_FUNCTIONS: set = {get_stock_fundamentals, search_news}