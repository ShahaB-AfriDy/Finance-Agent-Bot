import requests
import os
from datetime import datetime
from langchain_core.tools import tool

@tool
def get_stock_price(ticker: str) -> str:
    """
    📈 Get the current stock price for a given ticker symbol using the API-Ninjas Stock Price API.

    Args:
        ticker (str): The stock or index ticker symbol (e.g., 'AAPL', 'GOOGL', '^DJI').

    Returns:
        str: A formatted string showing the stock's name, symbol, exchange, current price, currency,
            and last updated time. Returns an error message if something goes wrong.

    Example:
        >>> get_stock_price("AAPL")
        '📈 Apple Inc. (AAPL) [NASDAQ]\n💵 Price: $192.42 USD\n🕒 Updated: 2024-01-26 18:20:01'
    """
    api_key = os.getenv("NINJAS_API_KEY")
    url = f"https://api.api-ninjas.com/v1/stockprice?ticker={ticker.upper()}"

    try:
        response = requests.get(url, headers={'X-Api-Key': api_key})
        if response.status_code != 200:
            return f"❌ Error {response.status_code}: {response.text}"

        data = response.json()
        if not data or "price" not in data:
            return f"⚠️ No data found for ticker: {ticker.upper()}"

        updated_time = datetime.fromtimestamp(data['updated']).strftime('%Y-%m-%d %H:%M:%S')

        return (
            f"📈 {data['name']} ({data['ticker']}) [{data['exchange']}]\n"
            f"💵 Price: ${data['price']} {data['currency']}\n"
            f"🕒 Updated: {updated_time}"
        )

    except Exception as e:
        return f"❌ Exception occurred: {str(e)}"


if __name__ == "__main__":
    print(get_stock_price.invoke("GOOGL"))
