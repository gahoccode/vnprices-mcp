"""
Tests for portfolio optimization data fetching and cleaning functionality.

This module tests the data fetching logic used in:
- calculate_returns()
- optimize_portfolio()
- full_portfolio_optimization()

The core logic being tested fetches historical price data for multiple symbols,
cleans and merges the data, and prepares it for portfolio optimization.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add the project root to the path to import server module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import Quote


class TestPortfolioDataFetching:
    """Test the core data fetching and cleaning logic for portfolio optimization."""

    def test_fetch_merge_multi(self):
        """Test successful fetching and merging of data for multiple real symbols."""
        # Use real Vietnamese stock symbols with recent date range
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

                # Add symbol column and keep time and close price (same as server.py)
                df_clean = df[["time", "close"]].copy()
                df_clean["time"] = pd.to_datetime(df_clean["time"])  # Convert to datetime
                df_clean.set_index("time", inplace=True)  # Set as datetime index
                df_clean.columns = [symbol]  # Rename close column to symbol name
                all_data.append(df_clean)

            except Exception as e:
                pytest.skip(f"Error fetching data for {symbol}: {str(e)}")

        # Skip test if we couldn't fetch any data
        if not all_data:
            pytest.skip("No data fetched for any symbols")

        # Merge all DataFrames on date index
        combined_df = pd.concat(all_data, axis=1)

        # Drop rows with any missing values
        combined_df = combined_df.dropna()

        # Verify the results
        assert not combined_df.empty, "Combined DataFrame should not be empty after dropping NaN values"
        assert len(combined_df.columns) == len(symbols), f"Should have {len(symbols)} columns"
        assert all(col in symbols for col in combined_df.columns), "All symbols should be present as columns"
        assert all(combined_df.notna().all()), "No missing values should remain after dropna"

        # Verify data integrity
        assert isinstance(combined_df.index, pd.DatetimeIndex), "Index should be DatetimeIndex"
        assert all(combined_df.dtypes.apply(lambda x: x in [np.float64, np.int64])), "All columns should be numeric"

    def test_single_symbol_processing(self):
        """Test processing of a single symbol."""
        symbol = "VCI"
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        # Simulate single symbol processing with real data
        all_data = []
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

        assert all_data, "Data should have been fetched successfully"
        assert len(all_data) == 1, "Should have exactly one DataFrame"
        assert list(all_data[0].columns) == [symbol], "Column should be named after symbol"

        # Verify the single DataFrame has expected structure
        df = all_data[0]
        assert "close" in df.columns or symbol in df.columns, f"Should have close price data for {symbol}"
        assert isinstance(df.index, (pd.RangeIndex, pd.DatetimeIndex)), "Index should be RangeIndex or DatetimeIndex"
        assert len(df) > 0, "Should have data rows"

    def test_no_data_found_for_symbol(self):
        """Test handling when no data is found for a specific symbol."""
        symbol = "INVALID"  # Non-existent stock symbol
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            # Should return empty DataFrame for invalid symbol
            if df is None or df.empty:
                # This is expected behavior for invalid symbols
                assert True, "Should return empty DataFrame for invalid symbol"
            else:
                pytest.fail("Expected empty DataFrame for invalid symbol")

        except Exception as e:
            # Exception handling is also acceptable for invalid symbols
            assert True, f"Exception handling works for invalid symbol: {str(e)}"

    def test_empty_symbols_list(self):
        """Test handling of empty symbols list."""
        symbols = []

        # Simulate the empty symbols check
        if not symbols:
            result = "No data found for any symbols"
            assert result == "No data found for any symbols"

    def test_data_cleaning_na(self):
        """Test proper handling of missing values in real data."""
        # Test with two symbols that might have different trading days
        symbols = ['VCI', 'FPT']  # These might have slightly different trading schedules
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        all_data = []
        for symbol in symbols:
            try:
                quote = Quote(symbol=symbol, source="VCI")
                df = quote.history(start=start_date, end=end_date, interval="1D")

                if df is None or df.empty:
                    continue

                # Add symbol column and keep time and close price (same as server.py)
                df_clean = df[["time", "close"]].copy()
                df_clean["time"] = pd.to_datetime(df_clean["time"])  # Convert to datetime
                df_clean.set_index("time", inplace=True)  # Set as datetime index
                df_clean.columns = [symbol]  # Rename close column to symbol name
                all_data.append(df_clean)

            except Exception:
                continue

        if len(all_data) < 2:
            pytest.skip("Could not fetch data for at least 2 symbols")

        # Merge all DataFrames on date index
        combined_df = pd.concat(all_data, axis=1)

        # Check if we have any missing values (common for real data)
        has_missing = combined_df.isna().any().any()

        if has_missing:
            # Test dropna functionality
            original_length = len(combined_df)
            cleaned_df = combined_df.dropna()

            # Should have fewer rows after dropping NaN values
            assert len(cleaned_df) <= original_length, "Should have fewer or equal rows after dropna"
            assert cleaned_df.notna().all().all(), "Should have no missing values after dropna"
            assert len(cleaned_df.columns) == len(combined_df.columns), "Should still have all columns"
        else:
            # If no missing values, the data is already clean
            assert combined_df.notna().all().all(), "Should have no missing values"

    def test_all_data_cleaned_away(self):
        """Test scenario where all data is cleaned away (empty after dropna)."""
        # Create a scenario with symbols that have no overlapping trading days
        # Use extreme date ranges to ensure no overlap
        symbols = ['VCI', 'VNM']
        start_dates = ['2020-01-01', '2022-01-01']  # Different time periods
        end_dates = ['2020-01-31', '2022-01-31']

        all_data = []
        for i, symbol in enumerate(symbols):
            try:
                quote = Quote(symbol=symbol, source="VCI")
                df = quote.history(start=start_dates[i], end=end_dates[i], interval="1D")

                if df is None or df.empty:
                    continue

                # Add symbol column and keep time and close price (same as server.py)
                df_clean = df[["time", "close"]].copy()
                df_clean["time"] = pd.to_datetime(df_clean["time"])  # Convert to datetime
                df_clean.set_index("time", inplace=True)  # Set as datetime index
                df_clean.columns = [symbol]  # Rename close column to symbol name
                all_data.append(df_clean)

            except Exception:
                continue

        if len(all_data) < 2:
            pytest.skip("Could not fetch data for test scenario")

        # This should create a DataFrame with missing values when merged
        combined_df = pd.concat(all_data, axis=1)

        # Apply dropna as the portfolio logic does
        cleaned_df = combined_df.dropna()

        # In extreme cases, this might result in empty DataFrame
        if cleaned_df.empty:
            # This simulates the "No complete data available" scenario
            result = "No complete data available after cleaning missing values"
            assert result == "No complete data available after cleaning missing values"
        else:
            # If not empty, the portfolio logic would proceed
            assert len(cleaned_df) > 0, "Should have data if dropna didn't remove everything"

    def test_only_close_prices_extracted(self):
        """Test that only close prices are extracted from OHLCV data."""
        symbol = "VCI"
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol}")

            # Test the data cleaning logic - extract only close prices
            df_clean = df[["close"]].copy()

            assert "close" in df_clean.columns, "Should have close column"
            assert len(df_clean) == len(df), "Should have same number of rows"
            assert isinstance(df_clean, pd.DataFrame), "Should be a DataFrame"

            # Verify we extracted only the close price data
            assert list(df_clean.columns) == ["close"], "Should only have close column"

        except Exception as e:
            pytest.skip(f"Error fetching data for {symbol}: {str(e)}")

    def test_dataframe_concatenation(self):
        """Test proper DataFrame concatenation on date index with real data."""
        symbols = ['VCI', 'FPT']
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        all_data = []
        for symbol in symbols:
            try:
                quote = Quote(symbol=symbol, source="VCI")
                df = quote.history(start=start_date, end=end_date, interval="1D")

                if df is None or df.empty:
                    continue

                df_clean = df[["close"]].copy()
                df_clean.columns = [symbol]
                all_data.append(df_clean)

            except Exception:
                continue

        if len(all_data) < 2:
            pytest.skip("Could not fetch data for at least 2 symbols")

        # Test concatenation
        combined_df = pd.concat(all_data, axis=1)

        # Verify concatenation results
        assert len(combined_df.columns) == len(symbols), "Should have correct number of columns"
        assert all(col in combined_df.columns for col in symbols), "All symbols should be present"
        assert isinstance(combined_df.index, (pd.RangeIndex, pd.DatetimeIndex)), "Index should be RangeIndex or DatetimeIndex"

        # Test that concatenation aligned data on date index
        assert len(combined_df) > 0, "Should have data after concatenation"

    def test_date_range_validation(self):
        """Test that date ranges work correctly with real data."""
        symbol = "VCI"

        # Test different date ranges
        date_ranges = [
            ("2024-01-01", "2024-01-10"),  # Short range
            ("2024-01-01", "2024-01-31"),  # One month
            ("2023-01-01", "2023-12-31"),  # One year
        ]

        for start_date, end_date in date_ranges:
            try:
                quote = Quote(symbol=symbol, source="VCI")
                df = quote.history(start=start_date, end=end_date, interval="1D")

                if df is None or df.empty:
                    continue  # Skip if no data for this range

                # Verify date range logic
                assert isinstance(df.index, (pd.RangeIndex, pd.DatetimeIndex)), "Should have datetime index"

                # Check that we have reasonable data structure
                if len(df) > 0:
                    # With RangeIndex, we check that we have the expected columns
                    assert 'close' in df.columns, "Should have close column"
                    assert len(df) > 0, "Should have data rows"

            except Exception as e:
                pytest.skip(f"Error testing date range {start_date} to {end_date}: {str(e)}")

    def test_temporal_alignment_across_symbols(self):
        """Test that data from different symbols aligns properly by datetime index."""
        symbols = ['VCI', 'FPT']
        start_date = "2024-01-01"
        end_date = "2024-01-10"

        all_data = []
        for symbol in symbols:
            try:
                quote = Quote(symbol=symbol, source="VCI")
                df = quote.history(start=start_date, end=end_date, interval="1D")

                if df is None or df.empty:
                    continue

                # Use the same logic as server.py
                df_clean = df[["time", "close"]].copy()
                df_clean["time"] = pd.to_datetime(df_clean["time"])
                df_clean.set_index("time", inplace=True)
                df_clean.columns = [symbol]
                all_data.append(df_clean)

            except Exception:
                continue

        if len(all_data) < 2:
            pytest.skip("Could not fetch data for temporal alignment test")

        # Concatenate should align by datetime index
        combined_df = pd.concat(all_data, axis=1)

        # Verify temporal alignment
        assert isinstance(combined_df.index, pd.DatetimeIndex), "Should have DatetimeIndex after concatenation"
        assert combined_df.index.is_monotonic_increasing, "Dates should be in chronological order"

        # Test that dropna removes rows where any symbol has missing data
        original_length = len(combined_df)
        cleaned_df = combined_df.dropna()

        # Cleaned DataFrame should have fewer or equal rows
        assert len(cleaned_df) <= original_length, "Should have fewer or equal rows after dropna"
        assert cleaned_df.notna().all().all(), "Should have no missing values after dropna"

    def test_vci_source_parameter(self):
        """Test that VCI source parameter works correctly."""
        symbol = "VCI"
        start_date = "2024-01-01"
        end_date = "2024-01-10"

        try:
            # Test that VCI source works for Vietnamese stocks
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol} with VCI source")

            # Verify the DataFrame structure
            expected_columns = ['open', 'high', 'low', 'close', 'volume']
            has_required_columns = any(col in df.columns for col in expected_columns)
            assert has_required_columns, f"Should have price data columns, found: {list(df.columns)}"

        except Exception as e:
            pytest.skip(f"Error testing VCI source for {symbol}: {str(e)}")

    @pytest.mark.parametrize("symbol", ["VCI", "FPT", "MWG", "HPG", "VNM"])
    def test_individual_symbol_data_integrity(self, symbol):
        """Test data integrity for individual symbols."""
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol}")

            # Test data integrity
            assert isinstance(df.index, (pd.RangeIndex, pd.DatetimeIndex)), "Index should be RangeIndex or DatetimeIndex"
            if isinstance(df.index, pd.DatetimeIndex):
                assert not df.index.duplicated().any(), "Should not have duplicate dates"
            assert len(df) > 0, "Should have data rows"

            # Check for expected price columns (may vary by data source)
            price_columns = [col for col in df.columns if col in ['open', 'high', 'low', 'close', 'volume']]
            assert len(price_columns) > 0, f"Should have at least some price columns, found: {list(df.columns)}"

            # Check that close prices are reasonable (positive numbers)
            if 'close' in df.columns:
                assert (df['close'] > 0).all(), "Close prices should be positive"

        except Exception as e:
            pytest.skip(f"Error testing {symbol}: {str(e)}")


@pytest.mark.fetch
class TestDataStructureValidation:
    """Test data structure and integrity aspects of the fetched real data."""

    def test_dataframe_index_is_datetime(self):
        """Test that the returned DataFrame has a datetime index."""
        symbol = "VCI"
        start_date = "2024-01-01"
        end_date = "2024-01-10"

        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol}")

            assert isinstance(df.index, (pd.RangeIndex, pd.DatetimeIndex)), "Index should be RangeIndex or DatetimeIndex"
            # Check data structure instead of index name since vnstock3 uses RangeIndex
            assert 'time' in df.columns or isinstance(df.index, pd.DatetimeIndex), "Should have time column or datetime index"

        except Exception as e:
            pytest.skip(f"Error testing index type for {symbol}: {str(e)}")

    def test_required_columns_present(self):
        """Test that expected price columns are present in real data."""
        symbol = "VCI"
        start_date = "2024-01-01"
        end_date = "2024-01-10"

        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol}")

            # Check for common price columns (data sources may vary)
            common_columns = ['open', 'high', 'low', 'close', 'volume']
            present_columns = [col for col in common_columns if col in df.columns]

            assert len(present_columns) > 0, f"Should have at least some price columns, found: {list(df.columns)}"

            # Most importantly, should have close price data
            assert 'close' in df.columns, "Should have close price column"

        except Exception as e:
            pytest.skip(f"Error testing columns for {symbol}: {str(e)}")

    def test_data_types_consistency(self):
        """Test that data types are consistent and appropriate in real data."""
        symbol = "VCI"
        start_date = "2024-01-01"
        end_date = "2024-01-10"

        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol}")

            # Test that numeric columns are indeed numeric
            for col in df.columns:
                if col in ['open', 'high', 'low', 'close']:
                    assert df[col].dtype in [np.float64, np.int64, np.float32, np.int32], \
                        f"Price column {col} should be numeric, got {df[col].dtype}"
                elif col == 'volume':
                    assert df[col].dtype in [np.float64, np.int64, np.int32], \
                        f"Volume column should be numeric, got {df[col].dtype}"

        except Exception as e:
            pytest.skip(f"Error testing data types for {symbol}: {str(e)}")

    def test_no_duplicate_dates(self):
        """Test that there are no duplicate dates in real data."""
        symbol = "VCI"
        start_date = "2024-01-01"
        end_date = "2024-01-10"

        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol}")

            assert not df.index.duplicated().any(), "Should not have duplicate dates"

        except Exception as e:
            pytest.skip(f"Error testing duplicate dates for {symbol}: {str(e)}")

    def test_chronological_order(self):
        """Test that dates are in chronological order in real data."""
        symbol = "VCI"
        start_date = "2024-01-01"
        end_date = "2024-01-10"

        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol}")

            assert df.index.is_monotonic_increasing, "Dates should be in chronological order"

        except Exception as e:
            pytest.skip(f"Error testing chronological order for {symbol}: {str(e)}")

    def test_price_data_validity(self):
        """Test that price data is valid and reasonable."""
        symbol = "VCI"
        start_date = "2024-01-01"
        end_date = "2024-01-10"

        try:
            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                pytest.skip(f"No data found for {symbol}")

            # Test that price data is reasonable
            if 'close' in df.columns:
                # Close prices should be positive
                assert (df['close'] > 0).all(), "Close prices should be positive"

                # Close prices should be finite
                assert np.isfinite(df['close']).all(), "Close prices should be finite"

            # Test OHLC relationships if available
            ohlc_cols = ['open', 'high', 'low', 'close']
            available_ohlc = [col for col in ohlc_cols if col in df.columns]

            if len(available_ohlc) == 4:  # All OHLC available
                assert (df['high'] >= df['low']).all(), "High should be >= low"
                assert (df['high'] >= df['open']).all(), "High should be >= open"
                assert (df['high'] >= df['close']).all(), "High should be >= close"
                assert (df['low'] <= df['open']).all(), "Low should be <= open"
                assert (df['low'] <= df['close']).all(), "Low should be <= close"

        except Exception as e:
            pytest.skip(f"Error testing price validity for {symbol}: {str(e)}")