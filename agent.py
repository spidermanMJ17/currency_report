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
            fixed_max_results=5
        )
    ],
    instructions = dedent("""
        You are a professional financial analyst.

        You have access to these tools and you must use it:
        If you answer without calling a tool first, the response will be rejected.
        You must call either web_search or search_news before generating the report.
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
)


def run_analysis(month: str, year: int, currency: str) -> str:

    #first gettting real value via real data
    real_data = fetch_data(currency, month, year)

    """
    Run financial analysis for the given month and year.
    Returns the LLM response as a string.
    """
    query = dedent(f"""

        Find the latest macroeconomic news affecting the {currency} forex market
        for {month} {year} using the available tools.

        You must call web_search or search_news to retrieve this information
        before generating the report.

        Market Data for your additional information
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