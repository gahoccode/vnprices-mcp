"""
Vietnamese Stock Market Data MCP Server
Provides tools to fetch stock, forex, crypto, and index historical data from vnstock
"""

from mcp.server.fastmcp import FastMCP
from vnstock import Vnstock, Quote

# Initialize the MCP server
mcp = FastMCP("vnprices")


@mcp.tool()
def get_stock_history(
    symbol: str, start_date: str, end_date: str, interval: str = "1D"
) -> str:
    """
    Get historical stock price data for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        start_date: Start date in YYYY-MM-DD format (e.g., '2024-01-01')
        end_date: End date in YYYY-MM-DD format (e.g., '2024-12-31')
        interval: Data interval - '1D' (daily), '1W' (weekly), '1M' (monthly)

    Returns:
        JSON string with historical price data including time, open, high, low, close, volume
    """
    try:
        # Initialize Quote object with VCI source
        quote = Quote(symbol=symbol, source="VCI")

        # Fetch historical data
        df = quote.history(start=start_date, end=end_date, interval=interval)

        if df is None or df.empty:
            return f"No data found for {symbol} between {start_date} and {end_date}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching stock data: {str(e)}"


@mcp.tool()
def get_forex_history(
    symbol: str, start_date: str, end_date: str, interval: str = "1D"
) -> str:
    """
    Get historical forex exchange rate data.

    Args:
        symbol: Forex pair symbol (e.g., 'USDVND', 'JPYVND', 'EURVND')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval - '1D' (daily), '1W' (weekly), '1M' (monthly)

    Returns:
        JSON string with historical forex rate data (time, open, high, low, close)
    """
    try:
        # Initialize Forex using Vnstock wrapper with MSN source
        fx = Vnstock().fx(symbol=symbol, source="MSN")

        # Fetch historical data
        df = fx.quote.history(start=start_date, end=end_date, interval=interval)

        if df is None or df.empty:
            return (
                f"No forex data found for {symbol} between {start_date} and {end_date}"
            )

        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching forex data: {str(e)}"


@mcp.tool()
def get_crypto_history(
    symbol: str, start_date: str, end_date: str, interval: str = "1D"
) -> str:
    """
    Get historical cryptocurrency price data.

    Args:
        symbol: Crypto symbol (e.g., 'BTC', 'ETH')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval - '1D' (daily), '1W' (weekly), '1M' (monthly)

    Returns:
        JSON string with historical crypto price data (time, open, high, low, close, volume)
    """
    try:
        # Initialize Crypto using Vnstock wrapper with MSN source
        crypto = Vnstock().crypto(symbol=symbol, source="MSN")

        # Fetch historical data
        df = crypto.quote.history(start=start_date, end=end_date, interval=interval)

        if df is None or df.empty:
            return (
                f"No crypto data found for {symbol} between {start_date} and {end_date}"
            )

        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching crypto data: {str(e)}"


@mcp.tool()
def get_index_history(
    symbol: str, start_date: str, end_date: str, interval: str = "1D"
) -> str:
    """
    Get historical market index data (Vietnamese and international indices).

    Args:
        symbol: Index symbol
               Vietnamese: 'VNINDEX', 'HNXINDEX', 'UPCOMINDEX'
               International: 'DJI' (Dow Jones), 'SP500', etc.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval - '1D' (daily), '1W' (weekly), '1M' (monthly)

    Returns:
        JSON string with historical index data (time, open, high, low, close, volume)
    """
    try:
        # Check if it's a Vietnamese index
        vietnam_indices = ["VNINDEX", "HNXINDEX", "UPCOMINDEX"]

        if symbol.upper() in vietnam_indices:
            # Use Quote with VCI source for Vietnamese indices
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval=interval)
        else:
            # Use MSN source for international indices
            index = Vnstock().world_index(symbol=symbol, source="MSN")
            df = index.quote.history(start=start_date, end=end_date, interval=interval)

        if df is None or df.empty:
            return (
                f"No index data found for {symbol} between {start_date} and {end_date}"
            )

        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching index data: {str(e)}"


if __name__ == "__main__":
    # Run server with stdio transport (default)
    mcp.run()
