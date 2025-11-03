# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-11-03

### 🎉 First Major Release

This release marks the first stable version with comprehensive Vietnamese financial data coverage and advanced portfolio optimization capabilities.

### Breaking Changes

⚠️ **Container Size Increase**: Docker image size increased from ~1.2GB to ~1.7GB (~500MB / 41% increase) due to portfolio optimization dependencies (scipy, numpy, cvxpy, osqp). This impacts:
- Disk space requirements
- Initial pull/build time (significantly longer)
- CI/CD pipeline duration
- Bandwidth for container distribution
- Memory requirements during optimization calculations

⚠️ **New Dependencies**: Added heavy numerical computing libraries (pyportfolioopt, osqp) with transitive dependencies (scipy, numpy, cvxpy). May conflict with existing numerical library versions in custom deployments.

⚠️ **Build Requirements**: Requires system build tools (gcc, g++, build-essential) already included in Dockerfile. Custom builds need these dependencies.

### Added
- `calculate_returns` tool for calculating expected returns for Vietnamese stock portfolios
- `optimize_portfolio` tool for Mean-Variance Optimization to maximize Sharpe ratio
- `full_portfolio_optimization` tool for comprehensive portfolio optimization with multiple strategies (max Sharpe, min volatility, max utility)
- PyPortfolioOpt library integration for portfolio optimization (version 1.5.6+)
- OSQP solver integration for quadratic programming (version 0.6.0+)
- Support for multiple expected returns calculation methods (mean historical, exponential moving average)
- Support for multiple covariance matrix methods (sample_cov, ledoit_wolf, exp_cov, semicovariance)
- Configurable risk-free rate and risk aversion parameters
- Portfolio performance metrics (expected annual return, annual volatility, Sharpe ratio)
- Portfolio optimization usage examples in examples/questions.md

### Changed
- Total tools count from 13 to 16 (4 price + 3 portfolio + 4 financial + 1 dividend + 1 company + 3 commodity/exchange)
- Container size from ~1.2GB to ~1.7GB due to optimization libraries
- Refactored portfolio optimization tools to use inline implementation pattern (removed helper functions)
- Reorganized documentation structure - moved usage examples to dedicated examples/questions.md file
- Simplified README.md Usage Examples section with reference to examples directory
- Updated vnstock-catalog.yaml with all 16 tools
- Enhanced .gitignore to exclude prds/ directory

### Documentation
- Created examples/ directory for better organization
- Created examples/questions.md with comprehensive usage examples for all tools
- Updated README.md with portfolio optimization tools section
- Added portfolio optimization examples for calculate returns, optimize portfolio, and full portfolio analysis
- Updated technical details to reflect 16 total tools and new container size
- Documented breaking changes in requirements.txt

### Technical
- All portfolio optimization tools use self-contained inline implementation (stateless container design)
- Proper error handling with OptimizationError exceptions
- JSON-RPC compatible output format for all optimization results
- Platform support: macOS ARM64 and Linux x86_64 with binary wheels

## [0.5.0] - 2025-11-02

### Added
- `get_company_info` tool for comprehensive company information access (9 types of data)
- Company overview, shareholders, officers, subsidiaries, events, news, reports, ratio_summary, trading_stats
- Enhanced Vietnamese stock market analysis capabilities with fundamental data
- Company information usage examples for all 9 data types
- Logging guidelines for MCP servers in CLAUDE.md
- FastMCP dependency clarification in documentation

### Changed
- Total tools count from 12 to 13 (4 price + 4 financial + 1 dividend + 1 company + 3 commodity/exchange)
- Updated README.md with new Company Information Tools section
- Enhanced tool categorization and documentation structure
- Rebuilt Docker image with new company information functionality (image ID: cd1542af2688)

### Documentation
- Added comprehensive company information tool examples
- Updated available tools section with get_company_info
- Enhanced usage examples with company analysis scenarios
- Updated technical details to reflect 13 total tools
- Added MCP server logging best practices

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

[Unreleased]: https://github.com/gahoccode/vnprices-mcp/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/gahoccode/vnprices-mcp/compare/v0.5.0...v1.0.0
[0.5.0]: https://github.com/gahoccode/vnprices-mcp/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/gahoccode/vnprices-mcp/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/gahoccode/vnprices-mcp/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/gahoccode/vnprices-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/gahoccode/vnprices-mcp/releases/tag/v0.1.0
