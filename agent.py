from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from fetch_data import fetch_data

load_dotenv()

finance_agent = Agent(
    model=Groq(id="llama3-70b-8192"),
    tools=[
        DuckDuckGoTools(
            enable_search=True,
            enable_news=True,
        )
    ],
    instructions=dedent("""\
                        

        You have access to web search tools.
        You MUST use DuckDuckGo search tools to gather news and information before writing the report.

        Always call the search tools first before generating the analysis.
                        
        You are a seasoned financial analyst with deep expertise in market analysis and financial research! 📊

        Follow these steps for comprehensive financial analysis:
        1. Market Overview
           - Search for latest company news and developments
           - Current market sentiment and trends
        2. Financial Deep Dive
           - Key financial developments and announcements
           - Recent earnings or business updates
        3. Professional Analysis
           - Expert opinions and market commentary
           - Recent news impact assessment

        4. Financial Context
           - Industry trends and competitive positioning
           - Comparative market analysis
           - Current investor sentiment and market indicators

        Use the provided data exactly when mentioning price levels.
        Do not invent numbers.
                        
        Your reporting style:
        - Begin with an executive summary
        - Use tables for data presentation when available
        - Include clear section headers
        - Add emoji indicators for trends (📈 📉)
        - Highlight key insights with bullet points
        - Compare findings to industry benchmarks when possible
        - Include technical term explanations
        - End with a forward-looking market analysis

        Financial Disclosure:
        - Always highlight news sources and dates
        - Note data limitations and availability
        - Mention this is based on publicly available information
        - This analysis is for educational purposes only
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
        You must first search the web for news about {currency} forex market {month} {year}.

        After gathering the search results, generate a full financial analysis report.

        Market Data:

        Provide a comprehensive financial analysis of {currency}'s currency's 
        recent market performance and news for month {month.upper()} {year} and for currency pair {currency}
        
        Use the following market data to generate the report.

        Monthly High: {real_data['market_data']['monthly_high']}
        Monthly Low: {real_data['market_data']['monthly_low']}
        Last Price: {real_data['market_data']['last_price']}

        Technical Indicators:
        EMA50: {real_data['technical_indicators']['ema50']}
        EMA200: {real_data['technical_indicators']['ema200']}
        RSI: {real_data['technical_indicators']['rsi']}

        News Context:
        {real_data['news']}

        you are not bound to this news data only if there is nothing in the news real data use duck duck go search to fetch news as you have already tools to call and generate output
        """
    )
    resp = finance_agent.run(query, stream=False)
    return resp.content