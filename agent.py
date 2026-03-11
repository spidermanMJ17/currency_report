from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from fetch_data import fetch_data

load_dotenv()

finance_agent = Agent(
    model=Groq(id="openai/gpt-oss-120b"),
    tools=[
        DuckDuckGoTools(
            enable_search=True,
            enable_news=True,
        )
    ],
    instructions = dedent("""
        You are a professional financial analyst.

        You have access to these tools:

        1. web_search(query: str)
           → Search the internet for relevant financial or macroeconomic information.

        2. search_news(query: str)
           → Retrieve recent news articles.

        Rules for tool usage:
        - Always include a `query` parameter.
        - Example tool call:
          web_search(query="USDINR forex market news May 2025")
        - Never include parameters like id, cursor, link, or url.

        Workflow:
        1. First gather information using tools.
        2. Then analyze the provided market data.
        3. Generate a structured financial report.

        Report format:
        - Executive Summary
        - Market Overview
        - Technical Indicators Analysis
        - Key Insights
        - Forward-looking Market Outlook

        Important:
        - Use the provided price data exactly.
        - Do not invent numerical values.
        - Mention news sources when available.
        - This analysis is for educational purposes only.
        """),
    markdown=True,
    tool_choice="required",
)


def run_analysis(month: str, year: int, currency: str) -> str:

    #first gettting real value via real data
    real_data = fetch_data(currency, month, year)

    """
    Run financial analysis for the given month and year.
    Returns the LLM response as a string.
    """
    query = dedent(f"""
        First gather relevant news and macroeconomic information about
        {currency} forex market for {month} {year} using the web_search or search_news tools.

        Then generate a professional financial analysis report using the data below.

        Market Data
        Monthly High: {real_data['market_data']['monthly_high']}
        Monthly Low: {real_data['market_data']['monthly_low']}
        Last Price: {real_data['market_data']['last_price']}

        Technical Indicators
        EMA50: {real_data['technical_indicators']['ema50']}
        EMA200: {real_data['technical_indicators']['ema200']}
        RSI: {real_data['technical_indicators']['rsi']}

        News Context
        {real_data['news']}
        """)
    resp = finance_agent.run(query, stream=False)
    return resp.content