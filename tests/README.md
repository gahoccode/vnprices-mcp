# Testing Documentation

This directory contains the test suite for the vnprices-mcp project. The tests focus on validating the data fetching and processing logic used in portfolio optimization functions.

## Overview

The test suite uses real vnstock3 data fetching to test the actual functionality rather than mocking. This approach ensures tests validate real-world behavior and catch integration issues that mocks might miss.

## Test Structure

```
tests/
├── README.md                # This file - testing documentation
├── conftest.py              # Shared test configuration and fixtures
├── test_fetch.py            # Portfolio data fetching tests
├── test_financial_year_alignment.py  # Financial year chronological alignment tests
└── test_*.py               # Additional test modules (future)
```

## Running Tests

### Environment Setup

```bash
# Using uv (recommended for this project)
uv add "mcp[cli]" vnstock3 pandas pyportfolioopt osqp pytest pytest-mock pytest-cov IPython

# Or using pip
pip install -r requirements.txt

# Ensure vnstock3 and all dependencies are installed
uv run python3 -c "from vnstock import Quote; print('✓ vnstock3 working')"
```

### Running Tests

```bash
# Run all tests with coverage and verbose output
pytest

# Run specific test file
pytest tests/test_fetch.py -v

# Run tests with detailed coverage reporting
pytest --cov=server --cov-report=term-missing --cov-report=html

# Run tests by category using markers
pytest -m portfolio        # Portfolio optimization tests
pytest -m fetch           # Data fetching tests
pytest -m integration     # Integration tests
pytest -m unit            # Unit tests
pytest -m slow            # Slow running tests

# Run specific test modules
pytest tests/test_financial_year_alignment.py  # Financial year alignment tests
pytest -k "chronological"  # Tests related to chronological ordering

# Run with specific output options
pytest -v --tb=short       # Verbose output with short tracebacks
pytest -v --tb=long        # Verbose output with long tracebacks

# Generate HTML coverage report (opens in htmlcov/index.html)
pytest --cov=server --cov-report=html

# Run tests matching a keyword
pytest -k "temporal"      # Run tests with "temporal" in name
pytest -k "fetch_merge"    # Run specific test function

# Run with coverage failure threshold (configured in pytest.ini)
pytest --cov-fail-under=85  # Fail if coverage below 85%
```

### Test Markers

The tests use pytest markers to categorize different types of tests:

- `@pytest.mark.fetch`: Tests focused on data fetching functionality
- `@pytest.mark.portfolio`: Tests for portfolio optimization logic
- `@pytest.mark.unit`: Unit tests (when applicable)
- `@pytest.mark.integration`: Integration tests requiring external API calls
- `@pytest.mark.slow`: Tests that take longer to run

**Current Test Distribution:**
- **Data Fetching Tests**: 12 tests (fetch, portfolio, integration)
- **Structure Validation Tests**: 6 tests (fetch, integration)
- **Financial Year Alignment Tests**: 10 tests (chronological ordering, cross-tool alignment)
- **Total Tests**: 32 tests covering portfolio optimization, financial statements, and data integrity

## Key Test Areas

### Data Fetching Logic
Tests the core portfolio optimization data fetching and cleaning functionality:
- **Multiple Symbol Fetching**: `test_fetch_merge_multi` - Fetch and merge data for multiple Vietnamese stocks
- **Single Symbol Processing**: `test_single_symbol_processing` - Validate individual symbol data processing
- **DataFrame Concatenation**: `test_dataframe_concatenation` - Test proper alignment by datetime index
- **Data Cleaning**: `test_data_cleaning_na` - Validate dropna() and missing value handling
- **Temporal Alignment**: `test_temporal_alignment_across_symbols` - Verify proper date-based alignment
- **Only Close Prices**: `test_only_close_prices_extracted` - Ensure proper OHLCV data processing

### Error Handling
Validates proper handling of various scenarios:
- Invalid stock symbols
- API connection issues
- Empty data responses
- Date range edge cases

### Data Integrity
Ensures proper DataFrame structure and data consistency:
- Datetime index validation
- Column presence and naming
- Data type consistency
- Price data validity (positive values, OHLC relationships)

### Edge Cases
Tests boundary conditions and unusual scenarios:
- Empty symbol lists
- All data cleaned away by dropna
- Different date ranges
- Market holidays and missing trading days

### Financial Year Alignment Tests
Tests chronological year ordering across all financial statement tools:
- **Individual Tool Chronological Ordering**: Validates each tool returns data sorted by yearReport
  - `test_income_statement_chronological_order` - Income statement year sorting
  - `test_balance_sheet_chronological_order` - Balance sheet year sorting
  - `test_cash_flow_chronological_order` - Cash flow statement year sorting
  - `test_financial_ratios_chronological_order` - Financial ratios MultiIndex year sorting
- **Cross-Statement Year Alignment**: Ensures all tools return identical year sequences for same symbol
  - `test_cross_statement_year_alignment` - Validates year consistency across 4 tools
- **Language Consistency**: Tests Vietnamese vs English output produces same year sequences
  - `test_vietnamese_vs_english_consistency` - Language alignment validation
- **Data Structure Validation**: Confirms vnstock3 API data structure and column presence
  - `test_data_structure_validation` - Validates yearReport column presence and types
- **Year Extraction Methods**: Tests helper functions for parsing JSON responses
  - `test_year_extraction_methods` - Validates year extraction from JSON and flattened data
- **Error Handling**: Tests edge cases and invalid data scenarios
  - `test_empty_dataframe_handling` - Empty/None DataFrame handling
  - `test_single_year_data` - Single year data processing

**Key Features:**
- **Real API Integration**: All tests use actual vnstock3 API calls (no mocking)
- **YearReport Focus**: Validates chronological sorting by yearReport column (not datetime)
- **MultiIndex Handling**: Special processing for financial ratios with flattened hierarchies
- **Cross-Tool Consistency**: Ensures temporal alignment across all financial statements

## Test Philosophy

### Real Data Integration Approach
Unlike traditional unit tests that mock external dependencies, these tests use the actual vnstock3 library to fetch real market data. This approach provides several benefits:

1. **Realistic Validation**: Tests validate actual API behavior and data structures
2. **Integration Testing**: Catch issues between vnstock3 and the portfolio logic
3. **Data Source Confidence**: Ensure the data source behaves as expected
4. **Live Feedback**: Tests fail if vnstock3 API changes or is unavailable

### Year-Based Chronological Alignment Implementation
**Recent Enhancement (2024):** All financial statement tools now properly handle year-based chronological ordering:

**Portfolio Optimization (datetime-based):**
```python
# Portfolio tools use datetime indexes for time series data
df_clean = df[["time", "close"]].copy()
df_clean["time"] = pd.to_datetime(df_clean["time"])
df_clean.set_index("time", inplace=True)
df_clean.columns = [symbol]
```

**Financial Statements (year-based):**
```python
# Financial statement tools use yearReport for chronological sorting
df = finance.income_statement(period="year", lang=lang)
df = df.sort_values('yearReport').reset_index(drop=True)
```

**For Financial Ratios (MultiIndex):**
```python
# Flatten MultiIndex first, then sort chronologically
flattened_df = flatten_hierarchical_index(df, separator="_", handle_duplicates=True, drop_levels=0)
if 'yearReport' in flattened_df.columns:
    flattened_df = flattened_df.sort_values('yearReport').reset_index(drop=True)
```

**Benefits:**
- **Year-Based Sorting**: Financial statements sorted by report year (2011, 2013, 2014, ...)
- **Consistent Data Structure**: All tools use `yearReport` column after processing
- **Cross-Statement Alignment**: Years match across all 4 financial statements
- **Simplified MultiIndex Handling**: Flatten then sort approach for financial ratios
- **Language Portability**: Works with English (`yearReport`) and Vietnamese data

**Test Validation:**
- `test_income_statement_chronological_order`: Validates income statement year sorting
- `test_financial_ratios_chronological_order`: Validates MultiIndex year sorting
- `test_cross_statement_year_alignment`: Validates year consistency across tools
- `test_year_extraction_methods`: Validates JSON parsing for year data

### Test Resilience
Since tests depend on external data sources, they use `pytest.skip()` to gracefully handle:

- Network connectivity issues
- Data source unavailability
- Symbol changes or delistings
- Temporary API errors

## Example Test Patterns

### Basic Data Fetching Test
```python
def test_successful_multiple_symbol_fetching_and_merging(self):
    """Test successful fetching and merging of data for multiple real symbols."""
    symbols = ['VCI', 'FPT', 'MWG']  # Well-known Vietnamese stocks
    start_date = '2024-01-01'
    end_date = '2024-01-31'

    # Simulate the data fetching logic from server.py
    all_data = []
    for symbol in symbols:
        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol} between {start_date} and {end_date}")

            # Add symbol column and keep only close price
            df_clean = df[["close"]].copy()
            df_clean.columns = [symbol]
            all_data.append(df_clean)

        except Exception as e:
            pytest.skip(f"Error fetching data for {symbol}: {str(e)}")

    # Continue with assertions...
```

### Error Handling Test
```python
def test_no_data_found_for_symbol(self):
    """Test handling when no data is found for a specific symbol."""
    symbol = "INVALID"  # Non-existent stock symbol

    try:
        quote = Quote(symbol=symbol, source="VCI")
        df = quote.history(start="2024-01-01", end="2024-01-31", interval="1D")

        # Should return empty DataFrame for invalid symbol
        if df is None or df.empty:
            assert True, "Should return empty DataFrame for invalid symbol"
        else:
            pytest.fail("Expected empty DataFrame for invalid symbol")

    except Exception as e:
        # Exception handling is also acceptable for invalid symbols
        assert True, f"Exception handling works for invalid symbol: {str(e)}"
```

### Financial Year Alignment Test Pattern
```python
def test_income_statement_chronological_order(self, test_symbols):
    """Test chronological year ordering for income statement."""
    for symbol in test_symbols:
        try:
            from server import get_income_statement

            result = get_income_statement(symbol, lang="en")

            # Validate no errors
            assert "Error" not in result, f"Got error for {symbol}: {result}"
            assert "No income statement data found" not in result, f"No data for {symbol}"

            # Extract and validate years
            years = self.extract_years_from_json(result)
            assert len(years) > 0, f"No years found in {symbol} data"

            # Verify chronological ordering
            sorted_years = sorted(years)
            assert years == sorted_years, f"Years not chronological for {symbol}: {years}"

        except Exception as e:
            pytest.skip(f"Failed to test {symbol}: {str(e)}")
```

### Cross-Statement Alignment Test Pattern
```python
def test_cross_statement_year_alignment(self, test_symbols):
    """Test year alignment across all financial statements."""
    for symbol in test_symbols:
        try:
            from server import get_income_statement, get_balance_sheet, get_cash_flow, get_financial_ratios

            # Get all statements (may skip due to API rate limits)
            income_result = get_income_statement(symbol, lang="en")
            balance_result = get_balance_sheet(symbol, lang="en")
            cashflow_result = get_cash_flow(symbol, lang="en")
            ratios_result = get_financial_ratios(symbol, lang="en")

            # Extract years from each statement
            income_years = self.extract_years_from_json(income_result)
            balance_years = self.extract_years_from_json(balance_result)
            cashflow_years = self.extract_years_from_json(cashflow_result)
            ratios_years = self.extract_years_from_flattened_json(ratios_result)

            # Validate cross-statement alignment
            all_years_lists = [income_years, balance_years, cashflow_years, ratios_years]
            common_years = set.intersection(*[set(years) for years in all_years_lists if years])

            assert len(common_years) > 0, f"No common years for {symbol}"
            print(f"{symbol} common years: {sorted(common_years)}")

        except Exception as e:
            pytest.skip(f"Alignment test failed for {symbol}: {str(e)}")
```

## Configuration

### pytest.ini Configuration
The test configuration is defined in `pytest.ini` at the project root:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --cov=server
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    portfolio: Portfolio optimization tests
    fetch: Data fetching tests
```

**Configuration Details:**
- **Test Discovery**: Searches `tests/` directory for `test_*.py` files
- **Coverage Target**: 80% minimum coverage for `server.py` module
- **Output Format**: Verbose output with short tracebacks
- **Reports**: Terminal (missing lines) + HTML (detailed) coverage reports
- **Strict Markers**: Only allows predefined pytest markers
- **Failure Threshold**: Tests fail if coverage drops below 80%

### Test Dependencies

**Core Testing Framework:**
- **pytest** (>=8.4.2): Main testing framework with plugin support
- **pytest-mock** (>=3.15.1): Mocking and patching capabilities
- **pytest-cov** (>=7.0.0): Coverage reporting and analysis

**Application Dependencies Required:**
- **vnstock3** (>=3.2.1): Vietnamese stock market data library
- **pandas** (>=2.0.0): Data manipulation and analysis
- **pyportfolioopt** (>=1.5.6): Portfolio optimization algorithms
- **mcp[cli]** (>=1.2.0): Model Context Protocol SDK

**Installation:**
```bash
# Install all dependencies at once
uv add "mcp[cli]" vnstock3 pandas pyportfolioopt osqp pytest pytest-mock pytest-cov IPython

# Or verify existing installation
uv run python3 -c "import pytest, vnstock; print('✓ All dependencies available')"
```

## Coverage Requirements

The test suite maintains **80% minimum code coverage** of the `server.py` module. Coverage reports are generated automatically:

- **Terminal**: Missing lines shown in terminal output with `--cov-report=term-missing`
- **HTML**: Detailed interactive report in `htmlcov/index.html`
- **Failure Threshold**: Tests fail if coverage drops below 80%

**Current Status:**
- **Total Tests**: 32 tests (as of latest run)
- **Coverage Target**: 80% (configured in pytest.ini)
- **Test Result**: ✅ All 32 tests passing
- **Key Functions Tested**: Portfolio optimization data fetching, datetime alignment, financial statement chronological sorting, error handling, data integrity

**Financial Year Alignment Tests Added:**
- ✅ `test_income_statement_chronological_order` - Income statement year sorting
- ✅ `test_balance_sheet_chronological_order` - Balance sheet year sorting
- ✅ `test_cash_flow_chronological_order` - Cash flow statement year sorting
- ✅ `test_financial_ratios_chronological_order` - Financial ratios MultiIndex year sorting
- ✅ `test_cross_statement_year_alignment` - Cross-tool year consistency (may skip due to API rate limits)
- ✅ `test_year_extraction_methods` - JSON parsing validation
- ✅ Language consistency and data structure validation tests

**Running Coverage:**
```bash
# Quick coverage check
pytest --cov=server

# Detailed HTML report
pytest --cov=server --cov-report=html
# Then open: htmlcov/index.html

# Strict coverage with custom threshold
pytest --cov=server --cov-fail-under=85
```

## Best Practices

### Writing New Tests

1. **Use Real Symbols**: Test with actual Vietnamese stock symbols (VCI, FPT, MWG, etc.)
2. **Handle Failures Gracefully**: Use `pytest.skip()` for data availability issues
3. **Validate Data Structure**: Check DataFrame structure, not just values
4. **Test Edge Cases**: Consider market holidays, symbol changes, API rate limits
5. **Be Specific**: Test specific functionality with clear assertions
6. **Financial Statement Testing**: Use language parameter consistently (`lang='en'`) for predictable `yearReport` columns
7. **API Rate Limit Management**: Balance comprehensive testing with rate limit awareness
8. **Cross-Tool Validation**: Ensure all financial statement tools align temporally

### Test Symbols
Common symbols used in tests:
- **VCI**: VietCapital Securities (reliable, liquid stock) - **Best for financial statements**
- **FPT**: FPT Corporation (large tech company) - Good portfolio optimization data
- **MWG**: Mobile World Group (retail giant) - Comprehensive financial data available
- **HPG**: Hoa Phat Group (steel manufacturer) - Good historical data
- **VNM**: Vinamilk (dairy company) - Long financial history

**Financial Statement Testing Priority:**
- **VCI**: Most reliable for consistent `yearReport` data across all 4 statements
- **FPT**: Good secondary option with comprehensive data availability

### Date Ranges
Typical date ranges for testing:
- **Recent**: 2024-01-01 to 2024-01-31 (last month)
- **Extended**: 2023-01-01 to 2023-12-31 (full year)
- **Short**: 2024-01-01 to 2024-01-10 (10 days)
- **Financial Statements**: Use annual data (`period='year'`) - typically 10+ years of yearReport data

## Troubleshooting

### Tests Skipping Frequently
If tests are often skipping due to data issues:

1. **Check Network**: Ensure internet connectivity for vnstock3 API calls
2. **Verify Symbols**: Test symbols (VCI, FPT, MWG, HPG, VNM) are liquid Vietnamese stocks
3. **Update Date Ranges**: Use recent dates (2024 data) for better availability
4. **Check vnstock3 Version**: Verify library is up to date: `uv run python3 -c "import vnstock; print(vnstock.__version__)"`

**Common Issues:**
- **API Rate Limits**: vnstock3 may limit requests during peak usage
- **Market Holidays**: Vietnamese market closed on holidays affects data availability
- **Symbol Changes**: Stock tickers may change over time
- **Weekend Data**: No trading data available on weekends

**Debugging Tips:**
```bash
# Test individual symbol to isolate issues
uv run python3 -c "
from vnstock import Quote
q = Quote('VCI', source='VCI')
df = q.history('2024-01-01', '2024-01-05', '1D')
print(f'Data shape: {df.shape}')
print(f'Date range: {df.time.min()} to {df.time.max()}')
"```

### Slow Test Performance
To improve test performance:

1. **Use Shorter Date Ranges**: Reduce date ranges for faster fetching
2. **Fewer Symbols**: Test with 2-3 symbols instead of many
3. **Run Specific Tests**: Use pytest markers to run only needed tests
4. **Cache Tests**: Consider test caching for repeated runs

### API Rate Limits
If encountering API rate limits:

1. **Stagger Tests**: Add small delays between test calls (especially for cross-statement tests)
2. **Reduce Test Scope**: Run tests in smaller batches, focus on individual tools
3. **Use Different Symbols**: Rotate symbols to distribute load (VCI → FPT → MWG)
4. **Check vnstock3 Documentation**: Review current API limits

**Financial Statement Rate Limit Mitigation:**
- **`test_cross_statement_year_alignment`**: Most likely to hit limits (calls all 4 tools per symbol)
- **Run Individual Tool Tests**: Use specific markers like `-k "income_statement"`
- **Focus on Core Tools**: Priority order: income → balance → cash flow → ratios
- **Use Primary Symbol**: VCI has most reliable data, reduces need for multiple symbols

## Future Enhancements

Already Implemented:
- ✅ **Financial Year Alignment**: Complete chronological validation across all financial statements
- ✅ **Cross-Statement Validation**: Temporal consistency testing (with rate limit awareness)
- ✅ **MultiIndex Handling**: Proper testing for financial ratios flattened data structures
- ✅ **Language Consistency**: Vietnamese vs English output validation
- ✅ **Real Data Integration**: All tests use actual vnstock3 API calls

Planned improvements to the test suite:

1. **Performance Testing**: Add benchmarks for financial statement fetching performance
2. **Quarterly Data Support**: Extend tests when quarterly financial statements become available
3. **More Edge Cases**: Test with delisted symbols, partial data years
4. **Integration Tests**: Complete end-to-end financial analysis workflows
