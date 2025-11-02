# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-11-02

### Added
- `get_sjc_gold_price` tool for fetching SJC gold prices (current or historical from 2016-01-02)
- `get_btmc_gold_price` tool for fetching BTMC (Bảo Tín Minh Châu) gold prices (current only)
- `get_vcb_exchange_rate` tool for fetching VCB (Vietcombank) exchange rates for specific dates
- SJC data source integration for gold prices (9 products with buy/sell prices)
- BTMC data source integration for gold prices (49 products with karat, gold_content, world_price)
- VCB data source integration for bank exchange rates (20 major currencies)
- Commodity and exchange rate usage examples in documentation

### Changed
- Total tools count from 9 to 12 (4 price + 4 financial + 1 dividend + 3 commodity/exchange)
- Updated data sources section to include SJC, BTMC, and VCB
- Enhanced documentation with commodity and exchange rate tool details

### Documentation
- Updated README.md with commodity & exchange rate tools and usage examples
- Updated CLAUDE.md with new tool implementation details and data sources
- Updated llms.txt with complete commodity & exchange rate tool documentation
- Added vnstock commodity prices guide and source code reference links

## [0.3.0] - 2025-11-02

### Added
- `get_dividend_history` tool for fetching complete dividend history for Vietnamese stocks
- TCBS data source integration for dividend data
- Dividend usage examples in documentation
- vnstock dividends guide reference link
- Note about pandas DataFrame to JSON string conversion for JSON-RPC communication

### Changed
- Total tools count from 8 to 9 (4 price history + 4 financial statements + 1 dividend)
- Updated data sources section to include TCBS
- Enhanced documentation with dividend tool details

### Documentation
- Updated README.md with dividend tool and usage examples
- Updated CLAUDE.md with dividend tool implementation details
- Updated llms.txt with complete dividend tool documentation

## [0.2.0] - 2025-11-02

### Added
- Four financial statement tools for Vietnamese stocks:
  - `get_income_statement` - Annual income statement (profit & loss)
  - `get_balance_sheet` - Annual balance sheet
  - `get_cash_flow` - Annual cash flow statement
  - `get_financial_ratios` - Annual financial ratios (P/B, ROE, etc.)
- Support for Vietnamese and English language output for financial statements
- MultiIndex DataFrame flattening for financial ratios
- Comprehensive financial statement documentation
- Research report on MCP, vnstock, and project architecture

### Changed
- Total tools count from 4 to 8 (4 price history + 4 financial statements)
- Enhanced CLAUDE.md with financial statement implementation details
- Clarified that index data is only for Vietnamese market (VNINDEX, HNXINDEX, UPCOMINDEX)
- Updated all documentation to reflect annual-only financial data (quarterly support planned)

### Documentation
- Added vnstock financial statements guide references
- Added vnstock financial statements data types documentation
- Updated README.md with financial statement tools and usage examples
- Refined CLAUDE.md with precise tooling details and clearer setup guidance
- Added note about quarterly financial data in future roadmap

## [0.1.0] - 2025-11-01

### Added
- Initial release of VNStock MCP Server
- Four price history tools:
  - `get_stock_history` - Vietnamese stock OHLCV data via VCI
  - `get_forex_history` - Forex exchange rates via MSN
  - `get_crypto_history` - Cryptocurrency prices via MSN
  - `get_index_history` - Vietnamese market indices via VCI
- Docker containerization with python:3.11-slim base
- FastMCP framework integration (MCP SDK 1.2.0+)
- vnstock3 3.2.0+ library integration
- Dual data source routing (VCI for stocks/indices, MSN for forex/crypto)
- Complete MCP Gateway setup and configuration
- Comprehensive documentation (README.md, CLAUDE.md, llms.txt)

### Documentation
- Project setup instructions for macOS with Docker
- NetworkChuck Docker MCP tutorial references
- Configuration files for MCP Gateway
- Testing and debugging procedures
- vnstock3 documentation links
- Render deployment button

### Infrastructure
- Dockerfile with system dependencies for vnstock3
- MCP Gateway catalog configuration (vnstock-catalog.yaml)
- Requirements.txt with core dependencies
- .gitignore for project cleanliness

[Unreleased]: https://github.com/gahoccode/vnprices-mcp/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/gahoccode/vnprices-mcp/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/gahoccode/vnprices-mcp/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/gahoccode/vnprices-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/gahoccode/vnprices-mcp/releases/tag/v0.1.0
