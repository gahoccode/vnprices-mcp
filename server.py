"""
Vietnamese Stock Market Data MCP Server
Provides tools to fetch stock, forex, crypto, and index historical data from vnstock
"""

from mcp.server.fastmcp import FastMCP
from vnstock import Vnstock, Quote
from vnstock.core.utils.transform import flatten_hierarchical_index
from vnstock.explorer.misc.gold_price import sjc_gold_price, btmc_goldprice
from vnstock.explorer.misc.exchange_rate import vcb_exchange_rate
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt.exceptions import OptimizationError

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


@mcp.tool()
def get_income_statement(symbol: str, lang: str = "en") -> str:
    """
    Get annual income statement (profit & loss) for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        lang: Language - 'en' (English) or 'vi' (Vietnamese)

    Returns:
        JSON string with annual income statement data including revenue, expenses,
        profit metrics, and earnings per share (EPS) for multiple years
    """
    try:
        # Initialize stock with VCI source
        stock = Vnstock().stock(symbol=symbol.upper(), source="VCI")
        finance = stock.finance

        # Fetch annual income statement
        df = finance.income_statement(period="year", lang=lang)

        if df is None or df.empty:
            return f"No income statement data found for {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching income statement for {symbol}: {str(e)}"


@mcp.tool()
def get_balance_sheet(symbol: str, lang: str = "en") -> str:
    """
    Get annual balance sheet for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        lang: Language - 'en' (English) or 'vi' (Vietnamese)

    Returns:
        JSON string with annual balance sheet data including assets, liabilities,
        equity, and detailed financial position metrics for multiple years
    """
    try:
        # Initialize stock with VCI source
        stock = Vnstock().stock(symbol=symbol.upper(), source="VCI")
        finance = stock.finance

        # Fetch annual balance sheet
        df = finance.balance_sheet(period="year", lang=lang)

        if df is None or df.empty:
            return f"No balance sheet data found for {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching balance sheet for {symbol}: {str(e)}"


@mcp.tool()
def get_cash_flow(symbol: str, lang: str = "en") -> str:
    """
    Get annual cash flow statement for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        lang: Language - 'en' (English) or 'vi' (Vietnamese)

    Returns:
        JSON string with annual cash flow data including operating, investing,
        and financing activities for multiple years
    """
    try:
        # Initialize stock with VCI source
        stock = Vnstock().stock(symbol=symbol.upper(), source="VCI")
        finance = stock.finance

        # Fetch annual cash flow statement
        df = finance.cash_flow(period="year", lang=lang)

        if df is None or df.empty:
            return f"No cash flow data found for {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching cash flow for {symbol}: {str(e)}"


@mcp.tool()
def get_financial_ratios(symbol: str, lang: str = "en") -> str:
    """
    Get annual financial ratios and metrics for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        lang: Language - 'en' (English) or 'vi' (Vietnamese)

    Returns:
        JSON string with annual financial ratios including P/B (Price-to-Book),
        ROE (Return on Equity), and other key financial health indicators
    """
    try:
        # Initialize stock with VCI source
        stock = Vnstock().stock(symbol=symbol.upper(), source="VCI")
        finance = stock.finance

        # Fetch annual financial ratios
        df = finance.ratio(period="year", lang=lang)

        if df is None or df.empty:
            return f"No financial ratio data found for {symbol}"

        # Flatten MultiIndex DataFrame before converting to JSON
        flattened_df = flatten_hierarchical_index(
            df, separator="_", handle_duplicates=True, drop_levels=0
        )

        # Convert to JSON
        return flattened_df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching financial ratios for {symbol}: {str(e)}"


@mcp.tool()
def get_dividend_history(symbol: str) -> str:
    """
    Get complete dividend history for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'ACB', 'HPG')

    Returns:
        JSON string with complete dividend history including exercise date,
        cash year, dividend percentage, and issue method for all historical records
    """
    try:
        # Initialize stock with TCBS source (dividends only available from TCBS)
        stock = Vnstock().stock(symbol=symbol.upper(), source="TCBS")
        company = stock.company

        # Fetch dividend history
        df = company.dividends()

        if df is None or df.empty:
            return f"No dividend data found for {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching dividend history for {symbol}: {str(e)}"


@mcp.tool()
def get_sjc_gold_price(date: str = None) -> str:
    """
    Get SJC gold prices (current or historical).

    Args:
        date: Date in YYYY-MM-DD format (e.g., '2024-01-15').
              If None, returns current prices. Historical data available from 2016-01-02.

    Returns:
        JSON string with gold price data including name, branch, buy_price, sell_price, date
    """
    try:
        # Fetch SJC gold prices
        df = sjc_gold_price(date=date)

        if df is None or df.empty:
            date_str = date if date else "current date"
            return f"No SJC gold price data found for {date_str}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching SJC gold prices: {str(e)}"


@mcp.tool()
def get_btmc_gold_price() -> str:
    """
    Get current BTMC (Bảo Tín Minh Châu) gold prices.

    Returns:
        JSON string with gold price data including name, karat, gold_content,
        buy_price, sell_price, world_price, time
    """
    try:
        # Fetch BTMC gold prices
        df = btmc_goldprice()

        if df is None or df.empty:
            return "No BTMC gold price data found"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching BTMC gold prices: {str(e)}"


@mcp.tool()
def get_vcb_exchange_rate(date: str) -> str:
    """
    Get VCB (Vietcombank) exchange rates for a specific date.

    Args:
        date: Date in YYYY-MM-DD format (e.g., '2024-01-15')

    Returns:
        JSON string with exchange rate data including currency_code, currency_name,
        buy_cash, buy_transfer, sell, date for 20 major currencies
    """
    try:
        # Fetch VCB exchange rates
        df = vcb_exchange_rate(date=date)

        if df is None or df.empty:
            return f"No VCB exchange rate data found for {date}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching VCB exchange rates: {str(e)}"


@mcp.tool()
def get_company_info(symbol: str, info_type: str = "overview", lang: str = "en") -> str:
    """
    Get company information for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'ACB', 'HPG')
        info_type: Type of company information to fetch:
                  'overview' - Company overview and basic information
                  'shareholders' - Major shareholders information
                  'officers' - Company officers and management (filter: 'working', 'resigned', 'all')
                  'subsidiaries' - Subsidiaries and associated companies (filter: 'all', 'subsidiary')
                  'events' - Corporate events and announcements
                  'news' - Company news and updates
                  'reports' - Analysis reports
                  'ratio_summary' - Financial ratios summary
                  'trading_stats' - Trading statistics and market data
        lang: Language - 'en' (English) or 'vi' (Vietnamese)

    Returns:
        JSON string with company information based on the requested type
    """
    try:
        # Initialize stock with VCI source for company information
        stock = Vnstock().stock(symbol=symbol.upper(), source="VCI")
        company = stock.company

        # Fetch the requested company information
        if info_type == "overview":
            df = company.overview()
        elif info_type == "shareholders":
            df = company.shareholders()
        elif info_type == "officers":
            # Default to working officers, can be extended to accept filter parameter
            df = company.officers(filter_by="working")
        elif info_type == "subsidiaries":
            # Default to all subsidiaries and associated companies
            df = company.subsidiaries(filter_by="all")
        elif info_type == "events":
            df = company.events()
        elif info_type == "news":
            df = company.news()
        elif info_type == "reports":
            df = company.reports()
        elif info_type == "ratio_summary":
            df = company.ratio_summary()
        elif info_type == "trading_stats":
            df = company.trading_stats()
        else:
            return f"Invalid info_type '{info_type}'. Valid types: overview, shareholders, officers, subsidiaries, events, news, reports, ratio_summary, trading_stats"

        if df is None or df.empty:
            return f"No {info_type} data found for {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching {info_type} for {symbol}: {str(e)}"


@mcp.tool()
def calculate_returns(
    symbols: list,
    start_date: str,
    end_date: str,
    method: str = "mean_historical",
    log_returns: bool = False,
) -> str:
    """
    Calculate expected returns for a portfolio of Vietnamese stocks.

    Args:
        symbols: List of stock symbols (e.g., ['VCI', 'VNM', 'HPG'])
        start_date: Start date in YYYY-MM-DD format (e.g., '2024-01-01')
        end_date: End date in YYYY-MM-DD format (e.g., '2024-12-31')
        method: Returns calculation method - 'mean_historical', 'ema_historical'
        log_returns: Whether to use log returns (True) or arithmetic returns (False)

    Returns:
        JSON string with expected returns data, methodology, and statistics
    """
    try:
        import pandas as pd
        import json

        # Fetch and clean price data for multiple symbols
        all_data = []
        for symbol in symbols:
            try:
                # Initialize Quote object with VCI source
                quote = Quote(symbol=symbol, source="VCI")
                df = quote.history(start=start_date, end=end_date, interval="1D")

                if df is None or df.empty:
                    return f"No data found for {symbol} between {start_date} and {end_date}"

                # Add symbol column and keep only close price
                df_clean = df[["close"]].copy()
                df_clean.columns = [symbol]
                all_data.append(df_clean)

            except Exception as e:
                return f"Error fetching data for {symbol}: {str(e)}"

        if not all_data:
            return "No data found for any symbols"

        # Merge all DataFrames on date index
        combined_df = pd.concat(all_data, axis=1)

        # Drop rows with any missing values
        combined_df = combined_df.dropna()

        if combined_df.empty:
            return "No complete data available after cleaning missing values"

        # Calculate expected returns using mean historical method
        mu = expected_returns.mean_historical_return(
            combined_df,
            returns_data=False,
            compounding=False,
            frequency=252,
            log_returns=log_returns,
        )

        # Prepare output
        output = {
            "symbols": symbols,
            "start_date": start_date,
            "end_date": end_date,
            "method": method,
            "log_returns": log_returns,
            "expected_returns": mu.to_dict(),
            "frequency": 252,
            "compounding": False,
        }

        return json.dumps(output, indent=2)

    except Exception as e:
        return f"Error calculating returns: {str(e)}"


@mcp.tool()
def optimize_portfolio(
    symbols: list,
    start_date: str,
    end_date: str,
    risk_free_rate: float = 0.02,
    covariance_method: str = "sample_cov",
    log_returns: bool = False,
) -> str:
    """
    Perform Mean-Variance Optimization to find the maximum Sharpe ratio portfolio.

    Args:
        symbols: List of stock symbols (e.g., ['VCI', 'VNM', 'HPG'])
        start_date: Start date in YYYY-MM-DD format (e.g., '2024-01-01')
        end_date: End date in YYYY-MM-DD format (e.g., '2024-12-31')
        risk_free_rate: Risk-free rate for Sharpe ratio calculation (default: 0.02)
        covariance_method: Covariance matrix method - 'sample_cov', 'ledoit_wolf', 'exp_cov', 'semicovariance'
        log_returns: Whether to use log returns (True) or arithmetic returns (False)

    Returns:
        JSON string with optimal weights and portfolio performance metrics
    """
    try:
        import pandas as pd
        import json

        # Fetch and clean price data for multiple symbols
        all_data = []
        for symbol in symbols:
            try:
                # Initialize Quote object with VCI source
                quote = Quote(symbol=symbol, source="VCI")
                df = quote.history(start=start_date, end=end_date, interval="1D")

                if df is None or df.empty:
                    return f"No data found for {symbol} between {start_date} and {end_date}"

                # Add symbol column and keep only close price
                df_clean = df[["close"]].copy()
                df_clean.columns = [symbol]
                all_data.append(df_clean)

            except Exception as e:
                return f"Error fetching data for {symbol}: {str(e)}"

        if not all_data:
            return "No data found for any symbols"

        # Merge all DataFrames on date index
        combined_df = pd.concat(all_data, axis=1)

        # Drop rows with any missing values
        combined_df = combined_df.dropna()

        if combined_df.empty:
            return "No complete data available after cleaning missing values"

        # Calculate expected returns using mean historical method
        mu = expected_returns.mean_historical_return(
            combined_df,
            returns_data=False,
            compounding=False,
            frequency=252,
            log_returns=log_returns,
        )

        # Calculate covariance matrix based on selected method
        if covariance_method == "sample_cov":
            S = risk_models.sample_cov(combined_df)
        elif covariance_method == "ledoit_wolf":
            S = risk_models.ledoit_wolf_shrinkage(combined_df)
        elif covariance_method == "exp_cov":
            S = risk_models.exp_cov(combined_df)
        elif covariance_method == "semicovariance":
            S = risk_models.semicovariance(combined_df)
        else:
            S = risk_models.sample_cov(combined_df)  # fallback to default

        # Create Efficient Frontier object and run optimization
        ef = EfficientFrontier(mu, S)
        ef.max_sharpe(risk_free_rate=risk_free_rate)

        # Get performance metrics
        performance = ef.portfolio_performance(
            verbose=False, risk_free_rate=risk_free_rate
        )

        # Clean weights and round to 4 decimal places
        clean_weights = ef.clean_weights()
        rounded_weights = {k: round(v, 4) for k, v in clean_weights.items()}

        # Prepare comprehensive output
        output = {
            "symbols": symbols,
            "start_date": start_date,
            "end_date": end_date,
            "optimization_type": "max_sharpe",
            "risk_free_rate": risk_free_rate,
            "covariance_method": covariance_method,
            "log_returns": log_returns,
            "optimal_weights": rounded_weights,
            "performance_metrics": {
                "expected_annual_return": round(performance[0], 6),
                "annual_volatility": round(performance[1], 6),
                "sharpe_ratio": round(performance[2], 6),
            },
        }

        return json.dumps(output, indent=2)

    except OptimizationError as e:
        return f"Optimization failed: {str(e)}"
    except Exception as e:
        return f"Error optimizing portfolio: {str(e)}"


@mcp.tool()
def full_portfolio_optimization(
    symbols: list,
    start_date: str,
    end_date: str,
    risk_free_rate: float = 0.02,
    risk_aversion: float = 1.0,
    covariance_method: str = "sample_cov",
    log_returns: bool = False,
) -> str:
    """
    Perform comprehensive portfolio optimization with multiple strategies.

    Args:
        symbols: List of stock symbols (e.g., ['VCI', 'VNM', 'HPG'])
        start_date: Start date in YYYY-MM-DD format (e.g., '2024-01-01')
        end_date: End date in YYYY-MM-DD format (e.g., '2024-12-31')
        risk_free_rate: Risk-free rate for Sharpe ratio calculation (default: 0.02)
        risk_aversion: Risk aversion coefficient for utility optimization (default: 1.0)
        covariance_method: Covariance matrix method - 'sample_cov', 'ledoit_wolf', 'exp_cov', 'semicovariance'
        log_returns: Whether to use log returns (True) or arithmetic returns (False)

    Returns:
        JSON string with all three optimized portfolios and performance comparison
    """
    try:
        import pandas as pd
        import json

        # Fetch and clean price data for multiple symbols
        all_data = []
        for symbol in symbols:
            try:
                # Initialize Quote object with VCI source
                quote = Quote(symbol=symbol, source="VCI")
                df = quote.history(start=start_date, end=end_date, interval="1D")

                if df is None or df.empty:
                    return f"No data found for {symbol} between {start_date} and {end_date}"

                # Add symbol column and keep only close price
                df_clean = df[["close"]].copy()
                df_clean.columns = [symbol]
                all_data.append(df_clean)

            except Exception as e:
                return f"Error fetching data for {symbol}: {str(e)}"

        if not all_data:
            return "No data found for any symbols"

        # Merge all DataFrames on date index
        combined_df = pd.concat(all_data, axis=1)

        # Drop rows with any missing values
        combined_df = combined_df.dropna()

        if combined_df.empty:
            return "No complete data available after cleaning missing values"

        # Calculate expected returns using mean historical method
        mu = expected_returns.mean_historical_return(
            combined_df,
            returns_data=False,
            compounding=False,
            frequency=252,
            log_returns=log_returns,
        )

        # Calculate covariance matrix based on selected method
        if covariance_method == "sample_cov":
            S = risk_models.sample_cov(combined_df)
        elif covariance_method == "ledoit_wolf":
            S = risk_models.ledoit_wolf_shrinkage(combined_df)
        elif covariance_method == "exp_cov":
            S = risk_models.exp_cov(combined_df)
        elif covariance_method == "semicovariance":
            S = risk_models.semicovariance(combined_df)
        else:
            S = risk_models.sample_cov(combined_df)  # fallback to default

        # Run all three optimization types
        optimizations = {}

        # Max Sharpe optimization
        try:
            ef_sharpe = EfficientFrontier(mu, S)
            ef_sharpe.max_sharpe(risk_free_rate=risk_free_rate)
            performance_sharpe = ef_sharpe.portfolio_performance(
                verbose=False, risk_free_rate=risk_free_rate
            )
            clean_weights_sharpe = ef_sharpe.clean_weights()

            optimizations["max_sharpe"] = {
                "success": True,
                "weights": {k: round(v, 4) for k, v in clean_weights_sharpe.items()},
                "expected_annual_return": round(performance_sharpe[0], 6),
                "annual_volatility": round(performance_sharpe[1], 6),
                "sharpe_ratio": round(performance_sharpe[2], 6),
                "optimization_type": "max_sharpe",
            }
        except OptimizationError as e:
            optimizations["max_sharpe"] = {
                "success": False,
                "error": f"Max Sharpe optimization failed: {str(e)}",
            }

        # Minimum volatility optimization
        try:
            ef_minvol = EfficientFrontier(mu, S)
            ef_minvol.min_volatility()
            performance_minvol = ef_minvol.portfolio_performance(
                verbose=False, risk_free_rate=risk_free_rate
            )
            clean_weights_minvol = ef_minvol.clean_weights()

            optimizations["min_volatility"] = {
                "success": True,
                "weights": {k: round(v, 4) for k, v in clean_weights_minvol.items()},
                "expected_annual_return": round(performance_minvol[0], 6),
                "annual_volatility": round(performance_minvol[1], 6),
                "sharpe_ratio": round(performance_minvol[2], 6),
                "optimization_type": "min_volatility",
            }
        except OptimizationError as e:
            optimizations["min_volatility"] = {
                "success": False,
                "error": f"Min volatility optimization failed: {str(e)}",
            }

        # Maximum utility optimization
        try:
            ef_utility = EfficientFrontier(mu, S)
            ef_utility.max_quadratic_utility(risk_aversion=risk_aversion)
            performance_utility = ef_utility.portfolio_performance(
                verbose=False, risk_free_rate=risk_free_rate
            )
            clean_weights_utility = ef_utility.clean_weights()

            optimizations["max_utility"] = {
                "success": True,
                "weights": {k: round(v, 4) for k, v in clean_weights_utility.items()},
                "expected_annual_return": round(performance_utility[0], 6),
                "annual_volatility": round(performance_utility[1], 6),
                "sharpe_ratio": round(performance_utility[2], 6),
                "optimization_type": "max_utility",
            }
        except OptimizationError as e:
            optimizations["max_utility"] = {
                "success": False,
                "error": f"Max utility optimization failed: {str(e)}",
            }

        # Filter out failed optimizations for summary
        successful_opts = [
            k for k, v in optimizations.items() if v.get("success", False)
        ]

        # Prepare comprehensive output
        output = {
            "symbols": symbols,
            "start_date": start_date,
            "end_date": end_date,
            "risk_free_rate": risk_free_rate,
            "risk_aversion": risk_aversion,
            "covariance_method": covariance_method,
            "log_returns": log_returns,
            "optimized_portfolios": optimizations,
            "summary": {
                "total_portfolios": len(successful_opts),
                "successful_optimizations": successful_opts,
            },
        }

        return json.dumps(output, indent=2)

    except Exception as e:
        return f"Error in full portfolio optimization: {str(e)}"


if __name__ == "__main__":
    # Run server with stdio transport (default)
    mcp.run()
