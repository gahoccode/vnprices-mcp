# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VNStock MCP Server - A containerized Model Context Protocol (MCP) server that integrates Vietnamese financial market data with Claude Desktop through the vnstock3 library. Provides historical prices for Vietnamese stocks, forex, crypto, and international indices.

## Development Commands

### Build and Deploy Workflow
```bash
# After modifying server.py
docker build --no-cache -t vnprices-mcp:latest .

# Verify build
docker images | grep vnprices-mcp

# Restart Claude Desktop (Cmd+Q, then reopen)
```

### Testing
```bash
# Test vnstock3 installation in container
docker run -it vnprices-mcp:latest python3 -c "from vnstock import Quote; print('OK')"

# Test data fetching
docker run -it vnprices-mcp:latest python3 -c "from vnstock import Quote; q = Quote('VCI'); print(q.history('2024-01-01', '2024-12-31'))"

# Test gateway manually (debug mode)
docker run -i --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.docker/mcp:/mcp \
  docker/mcp-gateway \
  --catalog=/mcp/catalogs/custom.yaml \
  --config=/mcp/config.yaml \
  --registry=/mcp/registry.yaml \
  --verbose

# View gateway logs
docker logs -f $(docker ps -q -f ancestor=docker/mcp-gateway)

# View server logs when tools are called
docker ps -a | grep vnprices  # Find container ID
docker logs <vnprices-container-id> --tail 100
```

### Cleanup
```bash
# Remove stopped containers
docker container prune

# Force rebuild everything (when things break)
docker rm -f $(docker ps -aq -f ancestor=vnprices-mcp:latest)
docker rm -f $(docker ps -aq -f ancestor=docker/mcp-gateway)
docker rmi vnprices-mcp:latest
docker build --no-cache -t vnprices-mcp:latest .
```

## Architecture

### Technology Stack
- **Runtime**: Python 3.11 (Docker containerized)
- **Framework**: MCP SDK 1.2.0+ (FastMCP)
- **Data Source**: vnstock3 3.2.0+ library
- **Processing**: pandas 2.0.0+
- **Transport**: stdio over Docker MCP Gateway

### Core Design Patterns

**FastMCP Pattern**: All tools use decorator-based implementation
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("vnprices")

@mcp.tool()
def tool_name(param: str) -> str:
    """Tool description"""
    try:
        # Implementation
        return json.dumps(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

**Stateless Design**: Each tool invocation spins up a fresh container instance - no state maintained between calls.

**Dual Data Source Routing** (implemented in `get_index_history`):
- Vietnamese indices (VNINDEX, HNXINDEX, UPCOMINDEX): Use `Quote` class (VCI source)
- International indices (DJI, SPX, IXIC, etc.): Use `Vnstock().world_index` (MSN source)

### Key Files

**server.py (~159 lines)** - Core MCP server with 4 tools:
- `get_stock_history()` - Vietnamese stocks via VCI source
- `get_forex_history()` - Exchange rates via MSN source
- `get_crypto_history()` - Cryptocurrency via MSN source
- `get_index_history()` - Indices (hybrid VCI/MSN routing)

All functions accept:
- `start`/`end` dates (YYYY-MM-DD format)
- `interval` parameter (1D, 1W, 1M)
- Return JSON strings
- Include error handling with try-catch

**Dockerfile** - Multi-stage build with system dependencies for wordcloud/vnstock3:
- Base: `python:3.11-slim`
- System deps: gcc, build-essential, image libraries (libfreetype6-dev, libpng-dev, libjpeg-dev)
- Python deps: requirements.txt
- Entrypoint: `python3 server.py`

**requirements.txt** - Must stay synchronized with Dockerfile

## Configuration Files

**MCP Gateway Config (macOS):**
```
~/.docker/mcp/
├── config.yaml                      # Server enablement
├── registry.yaml                    # Registry entries
└── catalogs/
    ├── docker-mcp.yaml             # Docker MCP catalog
    └── custom.yaml                 # Server definitions
```

**Claude Desktop Config:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Important**: These config files are managed outside the repository. When modifying tools, remember to update `~/.docker/mcp/catalogs/custom.yaml` to reflect changes.

## Data Flow

1. Claude Desktop → MCP Gateway (via stdio transport)
2. MCP Gateway → Docker container (vnprices-mcp:latest)
3. Container initializes Quote/Vnstock objects
4. vnstock3 fetches from VCI/MSN sources
5. Data processed via pandas → JSON string
6. Return path: Container → Gateway → Claude Desktop

## Common Development Tasks

### Adding a New Tool

1. **Update server.py** with new `@mcp.tool()` decorator function
2. **Rebuild container**: `docker build --no-cache -t vnprices-mcp:latest .`
3. **Update catalog** at `~/.docker/mcp/catalogs/custom.yaml`:
   ```yaml
   tools:
     - name: your_new_tool
   ```
4. **Restart Claude Desktop** (Cmd+Q, then reopen)

### Debugging Tools Not Appearing

1. Check `~/.docker/mcp/config.yaml` has vnprices enabled
2. View gateway logs: `docker logs -f $(docker ps -q -f ancestor=docker/mcp-gateway)`
3. Look for: "Enabled servers: vnprices" and "X tools listed"
4. Verify image exists: `docker images | grep vnprices-mcp`

### Debugging Data Fetching Issues

Test vnstock3 directly in container:
```bash
docker run -it vnprices-mcp:latest python3 << 'EOF'
from vnstock import Quote, Vnstock

# Test Vietnamese stock
q = Quote('VCI')
print(q.history('2024-01-01', '2024-12-31'))

# Test forex
v = Vnstock()
print(v.fx('USDVND', '2024-01-01', '2024-12-31'))
EOF
```

### Build Failures

If wordcloud/vnstock3 dependencies fail:
```bash
docker build --no-cache --progress=plain -t vnprices-mcp:latest . 2>&1 | grep -i error
```

System dependencies in Dockerfile should handle all build requirements. If fails, check apt-get install section includes: gcc, g++, build-essential, python3-dev, libfreetype6-dev, libpng-dev, libjpeg-dev, pkg-config.

## Technical Constraints

- **Container Size**: ~1.2GB (Python 3.11 slim + dependencies)
- **No API Keys**: vnstock3 handles data fetching internally
- **No Network Config**: Uses stdio transport (no ports needed)
- **Stateless**: Cannot maintain state between tool calls
- **Date Format**: All dates must be YYYY-MM-DD
- **Default Interval**: 1D (daily) if not specified

## References

- vnstock3 Documentation: https://vnstocks.com/docs/vnstock/thong-ke-gia-lich-su
- Model Context Protocol: https://modelcontextprotocol.io
- FastMCP SDK: https://github.com/modelcontextprotocol/python-sdk
- Docker MCP Gateway: https://github.com/docker/mcp-gateway
