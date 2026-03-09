import requests
import pandas as pd
from datetime import datetime
import json
from dotenv import load_dotenv
import os
load_dotenv()
import calendar

def get_month_range(month, year):
    last_day = calendar.monthrange(year, month)[1]

    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day}"

    return start_date, end_date

TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_fx_prices(pair, month, year):
    """
    Fetch daily FX prices
    """
    pair = pair[:3] + "/" + pair[3:]

    start_date, end_date = get_month_range(month, year)

    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=1day&outputsize=5000&start_date={start_date}&end_date={end_date}&apikey={TWELVEDATA_API_KEY}"

    r = requests.get(url).json()

    prices = []
    dates = []

    for i in r["values"]:
        prices.append(float(i["close"]))
        dates.append(i["datetime"])

    df = pd.DataFrame({
        "date": pd.to_datetime(dates),
        "close": prices
    })

    df = df.sort_values("date")

    return df


def filter_month(df, month, year):
    """
    Filter dataframe for selected month
    """

    df_month = df[
        (df["date"].dt.month == month) &
        (df["date"].dt.year == year)
    ]

    return df_month


def compute_indicators(df):

    df["EMA50"] = df["close"].ewm(span=50).mean()
    df["EMA200"] = df["close"].ewm(span=200).mean()

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return {
        "ema50": round(df["EMA50"].iloc[-1], 3),
        "ema200": round(df["EMA200"].iloc[-1], 3),
        "rsi": round(rsi.iloc[-1], 2)
    }


def get_news(pair, month, year):

    query = pair

    # url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    start_date, end_date = get_month_range(month, year)
    url = (
    f"https://newsapi.org/v2/everything?"
    f"q={pair}&"
    f"from={start_date}&"
    f"to={end_date}&"
    f"language=en&"
    f"sortBy=publishedAt&"
    f"apiKey={NEWS_API_KEY}"
)

    r = requests.get(url).json()

    headlines = []

    for article in r.get("articles", [])[:5]:
        title = article["title"]
        source = article["source"]["name"]
        date = article["publishedAt"][:10]

        headlines.append(f"{title} ({source}, {date})")

    return " | ".join(headlines)


def fetch_data(pair, month, year):

    if isinstance(month, str):
        month = list(calendar.month_name).index(month)

    df = get_fx_prices(pair, month, year)

    df_month = filter_month(df, month, year)

    monthly_high = round(df_month["close"].max(), 4)
    monthly_low = round(df_month["close"].min(), 4)
    last_price = round(df_month["close"].iloc[-1], 4)

    indicators = compute_indicators(df)

    news = get_news(pair, month, year)

    result = {
        "currency_pair": pair,
        "month": month,
        "year": year,
        "market_data": {
            "monthly_high": monthly_high,
            "monthly_low": monthly_low,
            "last_price": last_price
        },
        "technical_indicators": indicators,
        "news": news
    }

    return result


# if __name__ == "__main__":

#     pair = "USDINR"
#     month = 1
#     year = 2026

#     data = fetch_data(pair, month, year)

#     print(json.dumps(data, indent=4))