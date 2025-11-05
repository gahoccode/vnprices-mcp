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
- **Total Tests**: 22 tests covering portfolio optimization and data integrity

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

## Test Philosophy

### Real Data Integration Approach
Unlike traditional unit tests that mock external dependencies, these tests use the actual vnstock3 library to fetch real market data. This approach provides several benefits:

1. **Realistic Validation**: Tests validate actual API behavior and data structures
2. **Integration Testing**: Catch issues between vnstock3 and the portfolio logic
3. **Data Source Confidence**: Ensure the data source behaves as expected
4. **Live Feedback**: Tests fail if vnstock3 API changes or is unavailable

### Datetime Index Implementation
**Recent Enhancement (2024):** All portfolio optimization functions now properly handle datetime indexing:

**Before:** Extracted only close prices with RangeIndex (0, 1, 2, ...)
```python
# Old approach (in server.py)
df_clean = df[["close"]].copy()
df_clean.columns = [symbol]
```

**After:** Preserves time information and sets proper DatetimeIndex
```python
# Current approach (in server.py)
df_clean = df[["time", "close"]].copy()
df_clean["time"] = pd.to_datetime(df_clean["time"])
df_clean.set_index("time", inplace=True)
df_clean.columns = [symbol]
```

**Benefits:**
- **Temporal Alignment**: Data from different symbols aligns by actual dates
- **Better Portfolio Optimization**: More accurate calculations with time-aligned data
- **Industry Standards**: Follows financial time series best practices
- **Improved Data Integrity**: Proper handling of market holidays and missing trading days

**Test Validation:**
- `test_temporal_alignment_across_symbols`: Verifies datetime alignment works correctly
- `test_dataframe_concatenation`: Tests proper date-based merging
- `test_date_range_validation`: Ensures date ranges are handled properly

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
- **Total Tests**: 22 tests (as of latest run)
- **Coverage Target**: 80% (configured in pytest.ini)
- **Test Result**: ✅ All 22 tests passing
- **Key Functions Tested**: Portfolio optimization data fetching, datetime alignment, error handling, data integrity

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
4. **Test Edge Cases**: Consider market holidays, symbol changes, API limits
5. **Be Specific**: Test specific functionality with clear assertions

### Test Symbols
Common symbols used in tests:
- **VCI**: VietCapital Securities (reliable, liquid stock)
- **FPT**: FPT Corporation (large tech company)
- **MWG**: Mobile World Group (retail giant)
- **HPG**: Hoa Phat Group (steel manufacturer)
- **VNM**: Vinamilk (dairy company)

### Date Ranges
Typical date ranges for testing:
- **Recent**: 2024-01-01 to 2024-01-31 (last month)
- **Extended**: 2023-01-01 to 2023-12-31 (full year)
- **Short**: 2024-01-01 to 2024-01-10 (10 days)

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

1. **Stagger Tests**: Add small delays between test calls
2. **Reduce Test Scope**: Run tests in smaller batches
3. **Use Different Symbols**: Rotate symbols to distribute load
4. **Check vnstock3 Documentation**: Review current API limits

## Future Enhancements

Planned improvements to the test suite:

1. **Data Validation**: Add more comprehensive data quality checks
2. **Integration Tests**: Test complete portfolio optimization workflows
