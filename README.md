# VNStock MCP Server

A Model Context Protocol (MCP) server that provides Vietnamese financial market data through Claude Desktop. Fetch historical prices for stocks, forex, cryptocurrencies, and international indices using the vnstock3 library.

## Features

- **Vietnamese Stocks**: Historical OHLCV data for Vietnamese stock market
- **Forex Rates**: Exchange rate data for currency pairs
- **Cryptocurrencies**: Historical crypto price data
- **International Indices**: Global market index data
- **Containerized**: Runs as an isolated Docker container via MCP Gateway
- **Seamless Integration**: Works directly with Claude Desktop

## Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/gahoccode/vnprices-mcp)

## Available Tools

### 1. `get_stock_history`
Fetch historical stock price data for Vietnamese stocks (e.g., VCI, VNM, HPG).

### 2. `get_forex_history`
Fetch historical forex exchange rate data (e.g., USDVND, EURVND).

### 3. `get_crypto_history`
Fetch historical cryptocurrency price data (e.g., BTC, ETH).

### 4. `get_index_history`
Fetch historical index data for Vietnamese (VNINDEX, HNXINDEX)

## Prerequisites

- **Docker Desktop** (or Docker Engine) - [Download Docker Desktop](https://docs.docker.com/get-started/get-docker/)
- **Claude Desktop** application
- **macOS, Windows, or Linux**

**vnstock3 Documentation:**
- [vnstock3 Documentation](https://vnstocks.com/docs/vnstock/thong-ke-gia-lich-su)
- [vnstock Historical Prices Guide](https://github.com/gahoccode/docs/blob/main/vnstock/historical_prices.md)
- [vnstock VCI Quote Source](https://github.com/thinh-vu/vnstock/blob/main/vnstock/explorer/vci/quote.py)
- [vnstock MSN Quote Source](https://github.com/thinh-vu/vnstock/blob/main/vnstock/explorer/msn/quote.py)

## Tutorial

Besides the docs, I highly recommend watching this tutorial and following NetworkChuck's instructions. This guy is awesome!

- [Docker MCP Tutorial by NetworkChuck](https://www.youtube.com/watch?v=GuTcle5edjk&t=1349s)
- [NetworkChuck's Docker MCP Example](https://github.com/theNetworkChuck/docker-mcp-tutorial)

## Project Structure
```
vnprices-mcp/
├── server.py           # MCP server implementation
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Configuration

### Step 1: Copy Catalog File

First, copy the vnstock catalog to the MCP catalogs directory:

```bash
# Create the catalogs directory if it doesn't exist
mkdir -p ~/.docker/mcp/catalogs

# Copy the catalog file
cp vnstock-catalog.yaml ~/.docker/mcp/catalogs/custom.yaml
```

### Step 2: Claude Desktop Setup

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
        "--catalog=/mcp/catalogs/vnstock-catalog.yaml",
        "--config=/mcp/config.yaml",
        "--registry=/mcp/registry.yaml",
        "--transport=stdio"
      ]
    }
  }
}
```

**Important:** Replace `YOUR_USERNAME` with your actual macOS username.

After configuration:
1. Quit Claude Desktop completely (Cmd+Q on macOS)
2. Restart Claude Desktop
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
Retrieve VNINDEX data for 2024
```

## Rebuild & Test

### After Code Changes

If you modify `server.py` or other files:
```bash
# 1. Navigate to project directory
cd vnprices-mcp

# 2. Rebuild Docker image
docker build -t vnprices-mcp:latest .
docker build -t mcp-gateway .

# 2. Stop and remove old gateway container
docker stop mcp-gateway && docker rm mcp-gateway

# 3. Verify new image
docker images | grep vnprices-mcp

# 4. Check image ID changed
docker images vnprices-mcp

# 5. Run gateway
docker run -d \
  --name mcp-gateway \
  -v $(pwd)/catalogs:/mcp/catalogs \
  -v $(pwd)/registry.yaml:/mcp/registry.yaml \
  -v $(pwd)/config.yaml:/mcp/config.yaml \
  -p 3000:3000 \
  mcp-gateway

# 6. Restart Claude Desktop completely
# Quit (Cmd+Q) and restart
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

#Check Dockerfile 

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

- [vnstock3 Documentation](https://vnstocks.com/docs/vnstock/thong-ke-gia-lich-su)
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
