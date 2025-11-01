# VNStock MCP Server

A Model Context Protocol (MCP) server that provides Vietnamese financial market data through Claude Desktop. Fetch historical prices for stocks, forex, cryptocurrencies, and international indices using the vnstock3 library.

## Features

- **Vietnamese Stocks**: Historical OHLCV data for Vietnamese stock market
- **Forex Rates**: Exchange rate data for currency pairs
- **Cryptocurrencies**: Historical crypto price data
- **International Indices**: Global market index data
- **Containerized**: Runs as an isolated Docker container via MCP Gateway
- **Seamless Integration**: Works directly with Claude Desktop

## Available Tools

### 1. `get_stock_history`
Fetch historical stock price data for Vietnamese stocks.

**Parameters:**
- `symbol` (string): Stock ticker (e.g., 'VCI', 'VNM', 'HPG')
- `start` (string): Start date (YYYY-MM-DD)
- `end` (string): End date (YYYY-MM-DD)
- `source` (string, optional): Data source (default: 'VCI')

**Returns:** OHLCV data (Open, High, Low, Close, Volume)

### 2. `get_forex_history`
Fetch historical forex exchange rate data.

**Parameters:**
- `symbol` (string): Forex pair (e.g., 'USDVND', 'EURVND')
- `start` (string): Start date (YYYY-MM-DD)
- `end` (string): End date (YYYY-MM-DD)

**Returns:** OHLC data (Open, High, Low, Close)

### 3. `get_crypto_history`
Fetch historical cryptocurrency price data.

**Parameters:**
- `symbol` (string): Crypto symbol (e.g., 'BTC', 'ETH')
- `start` (string): Start date (YYYY-MM-DD)
- `end` (string): End date (YYYY-MM-DD)

**Returns:** OHLCV data

### 4. `get_index_history`
Fetch historical international index data.

**Parameters:**
- `symbol` (string): Index symbol (e.g., 'DJI', 'IXIC', 'SPX')
- `start` (string): Start date (YYYY-MM-DD)
- `end` (string): End date (YYYY-MM-DD)

**Returns:** OHLCV data

## Prerequisites

- **Docker Desktop** (or Docker Engine)
- **Claude Desktop** application
- **macOS, Windows, or Linux**

## Project Structure
```
vnprices-mcp/
├── server.py           # MCP server implementation
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation

### Step 1: Clone or Create Project Directory
```bash
mkdir vnprices-mcp
cd vnprices-mcp
```

### Step 2: Create Files

Create the following files in your project directory:

#### `requirements.txt`
```txt
# MCP SDK with CLI support
"mcp[cli]>=1.2.0"

# VNStock library for Vietnamese financial data
vnstock3>=3.2.0

# Data processing
pandas>=2.0.0
```

#### `Dockerfile`
```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for wordcloud and vnstock3
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Make executable
RUN chmod +x server.py

# Metadata
LABEL org.opencontainers.image.title="VNStock MCP Server"
LABEL org.opencontainers.image.description="MCP server for Vietnamese financial data via vnstock3"
LABEL org.opencontainers.image.version="1.0.0"

# Run server
ENTRYPOINT ["python3", "server.py"]
```

#### `server.py`
See the complete implementation in the corrected server.py file above (or in repository).

### Step 3: Build Docker Image
```bash
# Build the Docker image
docker build -t vnprices-mcp:latest .

# Verify the build
docker images | grep vnprices-mcp
```

**Expected output:**
```
vnprices-mcp    latest    <image-id>    X minutes ago    1.21GB
```

### Step 4: Configure MCP Gateway

#### Create MCP Directory Structure
```bash
mkdir -p ~/.docker/mcp/catalogs
```

#### Create Custom Catalog

Create `~/.docker/mcp/catalogs/custom.yaml`:
```yaml
version: 2
name: custom
displayName: Custom MCP Servers

registry:
  vnprices:
    description: "Fetch historical prices for Vietnamese stocks, forex, crypto, and international indices"
    title: "VNStock Price Data"
    type: server
    dateAdded: "2025-01-24T00:00:00Z"
    image: vnprices-mcp:latest
    ref: ""
    readme: "https://vnstock.site"
    toolsUrl: ""
    source: "https://github.com/thinh-vu/vnstock"
    upstream: ""
    icon: ""
    tools:
      - name: get_stock_history
      - name: get_forex_history
      - name: get_crypto_history
      - name: get_index_history
    metadata:
      category: finance
      tags:
        - vietnam
        - stocks
        - forex
        - crypto
        - finance
      license: MIT
      owner: local
```

#### Create Registry File

Create `~/.docker/mcp/registry.yaml`:
```yaml
registry:
  vnprices:
    ref: ""
```

#### Create Config File

Create `~/.docker/mcp/config.yaml`:
```yaml
servers:
  vnprices:
    enabled: true
```

#### Create Docker MCP Catalog (if needed)
```bash
# Check if it exists
ls ~/.docker/mcp/catalogs/docker-mcp.yaml

# If not, create minimal one
cat > ~/.docker/mcp/catalogs/docker-mcp.yaml << 'EOF'
version: 2
name: docker-mcp
displayName: Docker MCP Catalog
registry: {}
EOF
```

### Step 5: Configure Claude Desktop

#### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-gateway": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "/Users/YOUR_USERNAME/.docker/mcp:/mcp",
        "docker/mcp-gateway",
        "--catalog=/mcp/catalogs/docker-mcp.yaml",
        "--catalog=/mcp/catalogs/custom.yaml",
        "--config=/mcp/config.yaml",
        "--registry=/mcp/registry.yaml",
        "--transport=stdio"
      ]
    }
  }
}
```

**Replace `/Users/YOUR_USERNAME` with your actual home directory path.**

#### Windows
Edit `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-gateway": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "C:\\Users\\YOUR_USERNAME\\.docker\\mcp:/mcp",
        "docker/mcp-gateway",
        "--catalog=/mcp/catalogs/docker-mcp.yaml",
        "--catalog=/mcp/catalogs/custom.yaml",
        "--config=/mcp/config.yaml",
        "--registry=/mcp/registry.yaml",
        "--transport=stdio"
      ]
    }
  }
}
```

**Replace `C:\\Users\\YOUR_USERNAME` with your actual path (use double backslashes).**

#### Linux
Edit `~/.config/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-gateway": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "/home/YOUR_USERNAME/.docker/mcp:/mcp",
        "docker/mcp-gateway",
        "--catalog=/mcp/catalogs/docker-mcp.yaml",
        "--catalog=/mcp/catalogs/custom.yaml",
        "--config=/mcp/config.yaml",
        "--registry=/mcp/registry.yaml",
        "--transport=stdio"
      ]
    }
  }
}
```

### Step 6: Start Using

1. **Quit Claude Desktop completely** (Cmd+Q on macOS)
2. **Start Claude Desktop**
3. Wait for it to fully load

## Usage Examples

Open Claude Desktop and try these commands:

### Check Available Tools
```
What tools do you have available?
```

### Fetch Stock Data
```
Get VCI stock prices from January 1, 2024 to December 31, 2024
```

### Fetch Forex Data
```
Show me USDVND exchange rates for the last 6 months
```

### Fetch Crypto Data
```
Get Bitcoin price history from 2024-01-01 to 2024-12-31
```

### Fetch Index Data
```
Retrieve S&P 500 index data for 2024
```

## Rebuild & Test

### After Code Changes

If you modify `server.py` or other files:
```bash
# 1. Navigate to project directory
cd vnprices-mcp

# 2. Rebuild Docker image
docker build --no-cache -t vnprices-mcp:latest .

# 3. Verify new image
docker images | grep vnprices-mcp

# 4. Check image ID changed
docker images vnprices-mcp

# 5. Restart Claude Desktop completely
# Quit (Cmd+Q) and restart
```

### Testing Gateway Manually

Test if the gateway can start and recognize your server:
```bash
# Run gateway manually (test mode)
docker run -i --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.docker/mcp:/mcp \
  docker/mcp-gateway \
  --catalog=/mcp/catalogs/docker-mcp.yaml \
  --catalog=/mcp/catalogs/custom.yaml \
  --config=/mcp/config.yaml \
  --registry=/mcp/registry.yaml \
  --transport=stdio \
  --verbose

# Press Ctrl+C to stop
```

**Expected output:**
```
- Reading configuration...
- Enabled servers: vnprices
- Listing MCP tools...
> 4 tools listed
```

### View Live Logs

While Claude Desktop is running:
```bash
# Find the gateway container
docker ps | grep mcp-gateway

# View logs (replace <container-id> with actual ID)
docker logs -f <container-id>

# Or in one command
docker logs -f $(docker ps -q -f ancestor=docker/mcp-gateway)
```

### Check Server Container

When Claude calls a tool, your server container should spin up:
```bash
# List all containers (including stopped ones)
docker ps -a | grep vnprices

# View server logs
docker logs <vnprices-container-id>
```

### Clean Up Old Containers
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Full cleanup (careful!)
docker system prune -a
```

### Force Rebuild Everything

If things aren't working:
```bash
# 1. Stop Claude Desktop

# 2. Remove old containers
docker rm -f $(docker ps -aq -f ancestor=vnprices-mcp:latest)
docker rm -f $(docker ps -aq -f ancestor=docker/mcp-gateway)

# 3. Remove old image
docker rmi vnprices-mcp:latest

# 4. Rebuild from scratch
docker build --no-cache -t vnprices-mcp:latest .

# 5. Verify files exist
ls -la ~/.docker/mcp/
cat ~/.docker/mcp/config.yaml
cat ~/.docker/mcp/catalogs/custom.yaml

# 6. Test gateway manually (see above)

# 7. Restart Claude Desktop
```

## Troubleshooting

### Tools Not Appearing in Claude

**Check 1: Verify config.yaml**
```bash
cat ~/.docker/mcp/config.yaml
```
Should show:
```yaml
servers:
  vnprices:
    enabled: true
```

**Check 2: View gateway logs**
```bash
docker ps | grep mcp-gateway
docker logs -f <container-id>
```

Look for:
- `Enabled servers: vnprices`
- `4 tools listed`

**Check 3: Verify image exists**
```bash
docker images | grep vnprices-mcp
```

**Check 4: Test manual gateway run**
```bash
docker run -i --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.docker/mcp:/mcp \
  docker/mcp-gateway \
  --catalog=/mcp/catalogs/custom.yaml \
  --registry=/mcp/registry.yaml \
  --config=/mcp/config.yaml \
  --verbose
```

### Gateway Not Starting

**Check Claude config syntax:**
```bash
# Validate JSON
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python3 -m json.tool
```

**Check file permissions:**
```bash
ls -la ~/.docker/mcp/
chmod 644 ~/.docker/mcp/config.yaml
chmod 644 ~/.docker/mcp/catalogs/custom.yaml
```

### Server Returns Errors

**Check vnstock3 is working:**
```bash
# Test inside container
docker run -it vnprices-mcp:latest python3 -c "from vnstock import Quote; print('OK')"
```

**View detailed server logs:**
```bash
docker logs <vnprices-container-id> --tail 100
```

### Build Fails on Wordcloud

If you get wordcloud build errors:
```bash
# Check system dependencies are installed
docker build --no-cache --progress=plain -t vnprices-mcp:latest . 2>&1 | grep -A 10 "wordcloud"
```

The Dockerfile should already have all necessary dependencies.

## Development

### Project Structure
```
vnprices-mcp/
├── server.py              # MCP server implementation
│   ├── handle_list_tools()    # Register available tools
│   └── handle_call_tool()     # Execute tool calls
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
└── README.md             # Documentation
```

### Adding New Tools

1. **Add tool definition** in `handle_list_tools()`:
```python
types.Tool(
    name="your_new_tool",
    description="What it does",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    }
)
```

2. **Add handler logic** in `handle_call_tool()`:
```python
elif name == "your_new_tool":
    # Your implementation
    result = {"data": "response"}
    return [types.TextContent(type="text", text=json.dumps(result))]
```

3. **Rebuild:**
```bash
docker build -t vnprices-mcp:latest .
```

4. **Update catalog** in `~/.docker/mcp/catalogs/custom.yaml`:
```yaml
tools:
  - name: your_new_tool
```

## Technical Details

- **MCP Protocol Version**: 2025-06-18
- **Python Version**: 3.11
- **MCP SDK**: 1.2.0+
- **VNStock**: 3.2.0+
- **Transport**: stdio (Standard Input/Output)
- **Container Size**: ~1.2GB

## References

- [vnstock3 Documentation](https://vnstock.site)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Docker MCP Gateway](https://github.com/docker/mcp-gateway)

## License

MIT License - Feel free to use and modify.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## Support

For issues or questions:
- VNStock: [vnstock GitHub](https://github.com/thinh-vu/vnstock)
- MCP: [Model Context Protocol Docs](https://modelcontextprotocol.io)
- Docker: [Docker MCP Gateway](https://github.com/docker/mcp-gateway)

---

**Built with ❤️ for the Vietnamese developer community**
