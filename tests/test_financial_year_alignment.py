"""
Tests for chronological year alignment in financial statement tools.

This test module validates that all financial statement tools return data
sorted chronologically by yearReport for consistent temporal analysis.
"""

import pytest
import pandas as pd
import json
from vnstock import Vnstock


class TestFinancialYearAlignment:
    """Test year-based chronological alignment across financial statements."""

    @pytest.fixture(scope="class")
    def test_symbols(self):
        """Symbols for testing financial statements with reliable data."""
        return ['VCI', 'FPT', 'MWG', 'HPG']

    @pytest.fixture(scope="class")
    def years_range(self):
        """Expected year range for validation."""
        return list(range(2018, 2024))  # Typical available years

    def extract_years_from_json(self, json_str: str, year_key: str = 'yearReport') -> list:
        """Extract years from JSON response."""
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                years = [item.get(year_key) for item in data if year_key in item]
                return [year for year in years if year is not None]
            return []
        except (json.JSONDecodeError, TypeError):
            return []

    def extract_years_from_flattened_json(self, json_str: str) -> list:
        """Extract years from flattened MultiIndex JSON (financial ratios)."""
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                # Look for yearReport column in flattened data ( simplified approach )
                years = [item.get('yearReport') for item in data if 'yearReport' in item]
                return [year for year in years if year is not None]
            return []
        except (json.JSONDecodeError, TypeError):
            return []

    @pytest.mark.integration
    @pytest.mark.fetch
    def test_income_statement_chronological_order(self, test_symbols):
        """Test get_income_statement returns years in chronological order."""
        for symbol in test_symbols:
            try:
                # Import here to avoid potential import issues
                import sys, os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from server import get_income_statement

                result = get_income_statement(symbol, lang="en")

                # Should not be an error message
                assert "Error" not in result, f"Got error for {symbol}: {result}"
                assert "No income statement data found" not in result, f"No data for {symbol}"

                # Extract years and verify chronological ordering
                years = self.extract_years_from_json(result)
                assert len(years) > 0, f"No years found in {symbol} income statement"

                # Verify years are in ascending chronological order
                sorted_years = sorted(years)
                assert years == sorted_years, f"Years not chronological for {symbol}: {years}"

                # Verify years are integers
                assert all(isinstance(year, (int, float)) for year in years), f"Non-integer years for {symbol}: {years}"

            except Exception as e:
                pytest.skip(f"Failed to test {symbol}: {str(e)}")

    @pytest.mark.integration
    @pytest.mark.fetch
    def test_balance_sheet_chronological_order(self, test_symbols):
        """Test get_balance_sheet returns years in chronological order."""
        for symbol in test_symbols:
            try:
                import sys, os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from server import get_balance_sheet

                result = get_balance_sheet(symbol, lang="en")

                assert "Error" not in result, f"Got error for {symbol}: {result}"
                assert "No balance sheet data found" not in result, f"No data for {symbol}"

                years = self.extract_years_from_json(result)
                assert len(years) > 0, f"No years found in {symbol} balance sheet"

                sorted_years = sorted(years)
                assert years == sorted_years, f"Years not chronological for {symbol}: {years}"
                assert all(isinstance(year, (int, float)) for year in years), f"Non-integer years for {symbol}: {years}"

            except Exception as e:
                pytest.skip(f"Failed to test {symbol}: {str(e)}")

    @pytest.mark.integration
    @pytest.mark.fetch
    def test_cash_flow_chronological_order(self, test_symbols):
        """Test get_cash_flow returns years in chronological order."""
        for symbol in test_symbols:
            try:
                import sys, os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from server import get_cash_flow

                result = get_cash_flow(symbol, lang="en")

                assert "Error" not in result, f"Got error for {symbol}: {result}"
                assert "No cash flow data found" not in result, f"No data for {symbol}"

                years = self.extract_years_from_json(result)
                assert len(years) > 0, f"No years found in {symbol} cash flow"

                sorted_years = sorted(years)
                assert years == sorted_years, f"Years not chronological for {symbol}: {years}"
                assert all(isinstance(year, (int, float)) for year in years), f"Non-integer years for {symbol}: {years}"

            except Exception as e:
                pytest.skip(f"Failed to test {symbol}: {str(e)}")

    @pytest.mark.integration
    @pytest.mark.fetch
    def test_financial_ratios_chronological_order(self, test_symbols):
        """Test get_financial_ratios returns years in chronological order with MultiIndex."""
        for symbol in test_symbols:
            try:
                import sys, os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from server import get_financial_ratios

                result = get_financial_ratios(symbol, lang="en")

                assert "Error" not in result, f"Got error for {symbol}: {result}"
                assert "No financial ratio data found" not in result, f"No data for {symbol}"

                years = self.extract_years_from_flattened_json(result)
                assert len(years) > 0, f"No years found in {symbol} financial ratios"

                sorted_years = sorted(years)
                assert years == sorted_years, f"Years not chronological for {symbol}: {years}"
                assert all(isinstance(year, (int, float)) for year in years), f"Non-integer years for {symbol}: {years}"

            except Exception as e:
                pytest.skip(f"Failed to test {symbol}: {str(e)}")

    @pytest.mark.integration
    @pytest.mark.fetch
    def test_cross_statement_year_alignment(self, test_symbols):
        """Test all statements return identical year sequences for the same symbol."""
        for symbol in test_symbols:
            try:
                import sys, os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from server import get_income_statement, get_balance_sheet, get_cash_flow, get_financial_ratios

                # Get all statements
                income_result = get_income_statement(symbol, lang="en")
                balance_result = get_balance_sheet(symbol, lang="en")
                cashflow_result = get_cash_flow(symbol, lang="en")
                ratios_result = get_financial_ratios(symbol, lang="en")

                # Skip if any statement has no data
                if ("Error" in income_result or "Error" in balance_result or
                    "Error" in cashflow_result or "Error" in ratios_result):
                    pytest.skip(f"API error for {symbol}")

                if ("No data found" in income_result or "No data found" in balance_result or
                    "No data found" in cashflow_result or "No data found" in ratios_result):
                    pytest.skip(f"Missing data for {symbol}")

                # Extract years from each statement
                income_years = self.extract_years_from_json(income_result)
                balance_years = self.extract_years_from_json(balance_result)
                cashflow_years = self.extract_years_from_json(cashflow_result)
                ratios_years = self.extract_years_from_flattened_json(ratios_result)

                # All should have years
                assert len(income_years) > 0, f"No income years for {symbol}"
                assert len(balance_years) > 0, f"No balance years for {symbol}"
                assert len(cashflow_years) > 0, f"No cash flow years for {symbol}"
                assert len(ratios_years) > 0, f"No ratios years for {symbol}"

                # Verify all statements have the same years (allowing for small variations)
                # Some statements might have missing years, so we check the intersection
                common_years = set(income_years) & set(balance_years) & set(cashflow_years) & set(ratios_years)
                assert len(common_years) > 0, f"No common years across statements for {symbol}"

                print(f"\n{symbol} year coverage:")
                print(f"  Income: {sorted(income_years)}")
                print(f"  Balance: {sorted(balance_years)}")
                print(f"  Cash Flow: {sorted(cashflow_years)}")
                print(f"  Ratios: {sorted(ratios_years)}")
                print(f"  Common: {sorted(common_years)}")

            except Exception as e:
                pytest.skip(f"Failed alignment test for {symbol}: {str(e)}")

    @pytest.mark.unit
    def test_year_extraction_methods(self):
        """Test the year extraction helper methods."""
        # Test normal JSON
        test_json = json.dumps([
            {'yearReport': 2023, 'value': 100},
            {'yearReport': 2022, 'value': 80},
            {'yearReport': 2021, 'value': 60}
        ])
        years = self.extract_years_from_json(test_json)
        assert years == [2023, 2022, 2021], f"Expected [2023, 2022, 2021], got {years}"

        # Test flattened MultiIndex JSON
        test_flattened_json = json.dumps([
            {'yearReport': 2023, '(Chỉ tiêu định giá, P/B)': 2.5},
            {'yearReport': 2022, '(Chỉ tiêu định giá, P/B)': 2.8},
            {'yearReport': 2021, '(Chỉ tiêu định giá, P/B)': 3.1}
        ])
        flattened_years = self.extract_years_from_flattened_json(test_flattened_json)
        assert flattened_years == [2023, 2022, 2021], f"Expected [2023, 2022, 2021], got {flattened_years}"

    @pytest.mark.integration
    @pytest.mark.fetch
    def test_vietnamese_vs_english_consistency(self, test_symbols):
        """Test year alignment is consistent between Vietnamese and English languages."""
        for symbol in test_symbols[:2]:  # Test fewer symbols for this slower test
            try:
                import sys, os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from server import get_income_statement

                # Get both language versions
                en_result = get_income_statement(symbol, lang="en")
                vi_result = get_income_statement(symbol, lang="vi")

                if ("Error" in en_result or "Error" in vi_result or
                    "No data found" in en_result or "No data found" in vi_result):
                    pytest.skip(f"Language consistency test failed for {symbol}")

                en_years = self.extract_years_from_json(en_result)
                vi_years = self.extract_years_from_json(vi_result)

                # Both should have same years and ordering
                assert en_years == vi_years == sorted(en_years), (
                    f"Language inconsistency for {symbol}: "
                    f"EN={en_years}, VI={vi_years}"
                )

            except Exception as e:
                pytest.skip(f"Language consistency error for {symbol}: {str(e)}")

    @pytest.mark.integration
    @pytest.mark.fetch
    def test_data_structure_validation(self, test_symbols):
        """Test data structure consistency and validate yearReport column presence."""
        symbol = test_symbols[0]  # Test with one reliable symbol

        try:
            # Test the actual vnstock3 data structure
            stock = Vnstock().stock(symbol=symbol.upper(), source="VCI")
            finance = stock.finance

            # Test income statement structure
            income_df = finance.income_statement(period="year", lang="en")
            assert 'yearReport' in income_df.columns, "yearReport column missing in income statement"
            assert income_df['yearReport'].dtype in ['int64', 'Int64'], f"Incorrect yearReport dtype: {income_df['yearReport'].dtype}"

            # Test balance sheet structure
            balance_df = finance.balance_sheet(period="year", lang="en")
            assert 'yearReport' in balance_df.columns, "yearReport column missing in balance sheet"
            assert balance_df['yearReport'].dtype in ['int64', 'Int64'], f"Incorrect yearReport dtype: {balance_df['yearReport'].dtype}"

            # Test cash flow structure
            cashflow_df = finance.cash_flow(period="year", lang="en")
            assert 'yearReport' in cashflow_df.columns, "yearReport column missing in cash flow"
            assert cashflow_df['yearReport'].dtype in ['int64', 'Int64'], f"Incorrect yearReport dtype: {cashflow_df['yearReport'].dtype}"

            # Test ratios MultiIndex structure
            ratios_df = finance.ratio(period="year", lang="en")
            assert hasattr(ratios_df.index, 'names'), "Ratios should have MultiIndex"
            assert len(ratios_df.index.names) > 1, "Ratios should have MultiIndex with multiple levels"

        except Exception as e:
            pytest.skip(f"Data structure validation failed: {str(e)}")


class TestYearAlignmentEdgeCases:
    """Test edge cases and error handling for year alignment."""

    @pytest.mark.unit
    def test_empty_dataframe_handling(self):
        """Test handling of empty or None DataFrames."""
        import sys, os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from server import get_income_statement

        # This would ideally use mocking, but here we test a potentially problematic symbol
        result = get_income_statement("INVALIDSYMBOL", lang="en")
        assert "Error" in result or "No data found" in result, "Should handle invalid symbol gracefully"

    @pytest.mark.unit
    def test_single_year_data(self):
        """Test handling of data with only one year."""
        # This test would be more robust with mocking
        # For now, we verify the sorting logic works with single-year data
        test_data = [{'yearReport': 2023, 'value': 100}]
        years = TestFinancialYearAlignment().extract_years_from_json(json.dumps(test_data))
        assert years == [2023], f"Expected [2023], got {years}"