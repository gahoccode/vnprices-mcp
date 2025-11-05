"""
Shared test configuration and fixtures for vnprices-mcp tests.
"""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_symbols():
    """Sample list of Vietnamese stock symbols for testing."""
    return ['VCI', 'FPT', 'MWG', 'HPG', 'VNM']


@pytest.fixture
def sample_dates():
    """Sample date ranges for testing."""
    return {
        'short_range': ('2024-01-01', '2024-01-10'),
        'monthly': ('2024-01-01', '2024-01-31'),
        'yearly': ('2023-01-01', '2023-12-31')
    }


@pytest.fixture
def trading_symbols():
    """Well-known Vietnamese stocks with good liquidity for testing."""
    return {
        'large_cap': ['VCI', 'FPT', 'MWG', 'HPG', 'VNM'],
        'tech': ['FPT', 'CMG', 'ELC', 'EIP'],
        'retail': ['MWG', 'DGW', 'FRT'],
        'banking': ['TCB', 'VCB', 'CTG', 'ACB'],
        'manufacturing': ['HPG', 'HSG', 'NKG']
    }


@pytest.fixture
def date_ranges():
    """Common date ranges for testing different time periods."""
    return {
        'recent_week': ('2024-01-01', '2024-01-07'),
        'recent_month': ('2024-01-01', '2024-01-31'),
        'quarterly': ('2023-10-01', '2023-12-31'),
        'year_2023': ('2023-01-01', '2023-12-31'),
        'year_2024': ('2024-01-01', '2024-12-31')
    }


@pytest.fixture
def invalid_symbols():
    """Invalid or unlikely stock symbols for testing error handling."""
    return ['INVALID', 'NOTREAL', 'FAKE123', 'XYZ999']


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "portfolio: Tests for portfolio optimization functionality"
    )
    config.addinivalue_line(
        "markers", "fetch: Tests for data fetching functionality"
    )
    config.addinivalue_line(
        "markers", "integration: Tests requiring external API calls"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )