# Comprehensive Research Report: VNStock MCP Server Technical Foundation

**Date:** 2025-11-02
**Project:** vnprices-mcp
**Purpose:** Deep technical research on foundational technologies and patterns

---

## Table of Contents

1. [thinh-vu/vnstock GitHub Repository](#1-thinh-vuvnstock-github-repository)
2. [docker/mcp-gateway GitHub Repository](#2-dockermcp-gateway-github-repository)
3. [modelcontextprotocol/python-sdk GitHub Repository](#3-modelcontextprotocolpython-sdk-github-repository)
4. [Model Context Protocol Overview](#4-model-context-protocol-overview)
5. [MCP Protocol Specification (2025-06-18)](#5-mcp-protocol-specification-2025-06-18)
6. [Implementation Insights for vnprices-mcp](#6-implementation-insights-for-vnprices-mcp)

---

## 1. thinh-vu/vnstock GitHub Repository

### Overview
The vnstock library is a Python package for Vietnamese financial market data, providing a modular, service-oriented architecture focused on simplicity and ease of use.

### Core Architecture and Design

**Design Patterns:**
- **Facade Pattern**: Top-level functions (`stock_historical_data()`, `listing_companies()`) provide simple interfaces to complex underlying logic
- **Modular Design**: Organized by functionality (`chart`, `fundamental`, `trading`, `snippet`)
- **Implicit Strategy Pattern**: Runtime data source selection via `source` parameter (VCI, SSI, TCBS, MSN)

**Key Principles:**
- Prioritizes simplicity over deep class hierarchies
- Returns pandas DataFrames consistently across all functions
- Stateless functional approach minimizes complexity
- High-level facade functions for common tasks

### Quote Class and Data Sources

**Implementation Pattern:**
```python
class Quote:
    def __init__(self, symbol: str, source='VCI'):
        self.symbol = symbol
        self.source = source

    def get_price_board(self):
        if self.source == 'VCI':
            data = self._fetch_vci_price_board()
        elif self.source == 'MSN':
            data = self._fetch_msn_price_board()
        return self._format_data(data)
```

**Data Sources:**
- **VCI (Viet Capital Securities)**: Public API endpoint for Vietnamese stock price board data (JSON)
- **MSN**: Alternative source via scraping/undocumented API from financial portals
- Source selection dictates internal fetching method

### Historical Data Fetching Methods

**1. `history()` / `stock_historical_data()`**
- **Purpose**: OHLCV (Open, High, Low, Close, Volume) data
- **Parameters**: `symbol`, `start_date`, `end_date`, `resolution` (1D, 1H)
- **Process Flow**:
  1. Validate input parameters
  2. Select data source (TCBS, SSI, VCI)
  3. Construct API request URL with query parameters
  4. Make HTTP GET request
  5. Parse JSON response
  6. Normalize data (convert timestamps, rename columns)
  7. Return pandas DataFrame

**2. `fx()` / `foreign_exchange_rate()`**
- **Data Source**: Central bank APIs (State Bank of Vietnam) or financial institutions
- **Process**: Request data for specific date, parse XML/JSON, return DataFrame with currency pairs

**3. `world_index()` / `world_stock_index()`**
- **Data Source**: Scraping/API from Investing.com or Yahoo Finance
- **Process**: Fetch HTML/JSON, parse table of world indices, convert to DataFrame

### API Patterns and Best Practices

**Design Excellence:**
- **Functional API First**: Top-level functions without class instantiation
- **Consistent Return Type**: All functions return pandas DataFrames
- **Descriptive Names**: Clear function naming (`stock_fundamental_data`, `company_overview`)
- **Keyword Arguments**: Sensible defaults (e.g., `source='TCBS'`)
- **Minimal State**: Stateless operations reduce complexity

### Error Handling Patterns

**Network Errors:**
- `try...except` blocks for `requests.exceptions.RequestException`
- Raises custom exceptions or standard Python exceptions with informative messages
- Examples: `RuntimeError`, `ValueError` with context

**API/Data Errors:**
- Validates non-200 status codes
- Catches malformed JSON responses
- Indicates invalid symbols or API downtime

**Input Validation:**
- Immediate `ValueError` for unsupported sources
- Fails fast with clear error messages
- Prevents ambiguous `None` or empty DataFrame returns

### Data Processing with Pandas

**Core Responsibilities:**
- **Data Structuring**: Raw JSON → pandas DataFrame
- **Data Cleaning**:
  - Column renaming: `t` → `time`, `o` → `open`
  - Type conversion: Unix epochs → `datetime`, strings → `float`/`int`
  - Indexing: Date/timestamp columns set as index
- **No Heavy Computation**: Focuses on data delivery, not analysis/feature engineering

**Key Insight:** vnstock is a well-designed, practical library that understands user needs, prioritizing ease of use and consistent API while leveraging pandas as the primary data delivery mechanism.

---

## 2. docker/mcp-gateway GitHub Repository

### Gateway Architecture

**Core Concept:**
The mcp-gateway acts as an intelligent proxy and lightweight, session-based container orchestrator, managing on-demand provisioning of Docker containers for MCP tools.

**Architectural Components:**
- **Central Entry Point**: Single contact point for all clients
- **Service Discovery**: File-based YAML configuration system
- **On-Demand Provisioning**: Starts containers only when needed
- **Session-Based Lifecycle**: Containers tied to client sessions
- **Transport Abstraction**: Bridges client connections to container stdio streams

**Key Responsibilities:**
1. Translate client tool requests into running Docker containers
2. Manage container lifecycle (create, attach, proxy, teardown)
3. Provide resource isolation per client session
4. Abstract communication layer via stdio streaming

### Configuration Files Structure

**1. `config.yaml` (Main Gateway Configuration)**
```yaml
# Bootstrap configuration for gateway application
host: 0.0.0.0
port: 8080
logging:
  level: info
  output: /var/log/gateway.log
registry_path: /mcp/registry.yaml
docker:
  socket: /var/run/docker.sock
  timeout: 30
security:
  tls_enabled: false
```

**Purpose**: Gateway operational parameters, logging, paths to other configs, Docker settings, security

**2. `registry.yaml` (Catalog Registry)**
```yaml
# Points to tool definition files
catalogs:
  - "catalogs/development.yaml"
  - "catalogs/production/*.yaml"
```

**Purpose**: Decouples gateway core config from tool definitions, enables easy catalog addition/removal

**3. `catalogs/*.yaml` (Tool Definitions)**
```yaml
# Example tool definition
tools:
  - id: python-linter
    name: Python Code Linter
    image: python:3.11-slim
    cmd: ["python3", "linter.py"]
    env:
      - PYTHONUNBUFFERED=1
    resource_limits:
      cpu: "0.5"
      memory: "512M"
    workdir: /app
```

**Purpose**: Service discovery system defining container metadata for each tool

**Configuration Relationships:**
```
config.yaml → registry.yaml → catalogs/*.yaml
     ↓              ↓                ↓
  Gateway    Catalog Paths    Tool Definitions
```

### Container Orchestration

**Lifecycle Management:**
1. **Request**: Client connects and requests tool by ID
2. **Provision**: Gateway finds tool definition, issues `docker run` command
3. **Attach**: Gateway attaches to container's stdin/stdout/stderr streams
4. **Proxy**: Data proxied between client and container
5. **Teardown**: `docker stop` and `docker rm` on session end

**Isolation & Statelessness:**
- Each client session gets dedicated container
- Strong isolation prevents cross-session interference
- Ephemeral containers lose state on teardown
- Stateful operations require external databases or mounted volumes

### stdio Transport Mechanism

**How It Works:**
1. Gateway establishes stream-capable connection with client (WebSocket/gRPC)
2. Gateway runs container via Docker API, gets stdio stream handles
3. Client data → gateway → container stdin
4. Container stdout/stderr → gateway → client

**Advantages:**
- **Simplicity**: No networking code needed in container tools
- **Security**: No exposed container ports, reduced attack surface
- **Dynamic**: Avoids port collision problems
- **Efficient**: Direct stream proxying

### Tool Discovery and Registration

**Static, File-Based Process:**
1. Gateway starts, loads `config.yaml`
2. Reads `registry.yaml` for catalog paths
3. Parses all matching catalog YAML files
4. Validates tool definitions
5. Builds in-memory map keyed by tool ID

**Key Points:**
- Entirely static at gateway startup
- Changes require gateway restart
- No dynamic tool discovery at runtime

### Communication Flow (Client to Server)

**Step-by-Step Trace:**
1. **Client → Gateway**: Establish connection (e.g., `ws://gateway:8080`)
2. **Tool Request**: Client sends `{"tool_id": "python-linter"}`
3. **Gateway → Docker**: Create and start container command
4. **Gateway Attaches**: To container stdio streams
5. **Client → Gateway → Container**: Data payload written to stdin
6. **Container Processing**: Tool reads stdin, processes, writes to stdout
7. **Container → Gateway → Client**: Results forwarded over connection
8. **Session End**: Gateway stops and removes container

### Best Practices

**Configuration:**
- Version control all YAML configs
- Separate tools into multiple catalog files by category
- Use environment variables for secrets/environment-specific settings
- Always define CPU/memory limits to prevent resource starvation

**Debugging:**
- **Gateway Logs**: First stop for connection attempts, tool requests, container events
- **Docker Daemon Logs**: `journalctl -u docker.service` for detailed errors
- **Running Containers**: `docker ps -a` to see container states
- **Container Logs**: `docker logs <container_id>` for tool stdout/stderr
- **Interactive Testing**: `docker run -it --entrypoint /bin/bash <image>` to debug

---

## 3. modelcontextprotocol/python-sdk GitHub Repository

### FastMCP Framework Architecture

**Design Philosophy:**
- **Code as Source of Truth**: Type hints and docstrings auto-generate schemas
- **Asynchronous First**: Built on `asyncio` for high-concurrency I/O
- **Transport Agnostic**: Tools decoupled from communication layer
- **Dependency Injection**: Context passing for cleaner, testable code

**Core Components:**
1. **`MCP` Application**: Central object (like FastAPI/Flask)
2. **Decorators**: `@mcp.tool`, `@mcp.resource`, etc.
3. **Schema Generation**: Pydantic introspection for JSON Schema
4. **Transport Layer**: Pluggable stdio/WebSocket/SSE

### Tool Decorator Pattern (`@mcp.tool()`)

**Mechanism:**
```python
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    username: str = Field(..., description="Unique username")
    age: Optional[int] = Field(None, description="User's age")

@mcp.tool()
async def update_user_profile(profile: UserProfile):
    """Updates a user's profile in the database."""
    return {"status": "success", "username": profile.username}
```

**How It Works:**
1. **Registration**: Function added to MCP instance registry
2. **Introspection**:
   - Function name → `tool_name`
   - Docstring → `description`
   - Parameters & type hints → `parameters` JSON Schema
   - Return type → output schema

**Best Practices:**
- **Excellent Docstrings**: Primary communication with LLM
- **Specific Type Hints**: Use precise types instead of `Any`
- **Pydantic for Complexity**: Define `BaseModel` for >2-3 arguments
- **Field Descriptions**: Use `Field(..., description="...")` for clarity

### Server Implementation and Lifecycle

**Implementation Pattern:**
```python
from fastmcp import MCP
import asyncio

mcp = MCP(title="Example Server")

# Shared resources
db_connection = None

@mcp.on_event("startup")
async def startup_event():
    """Initializes resources on server start."""
    global db_connection
    print("Connecting to database...")
    await asyncio.sleep(1)  # Simulate async connection
    db_connection = {"connected": True}

@mcp.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown."""
    global db_connection
    print("Closing database connection...")
    db_connection = None

@mcp.tool()
async def check_db_status():
    """Checks database connection status."""
    return {"db_status": db_connection}
```

**Lifecycle Events:**
- **`startup`**: Initialize shared resources (DB pools, ML models, connections)
- **`shutdown`**: Graceful cleanup (close connections, save state, release handles)

### Transport Protocols

**1. stdio**
- **Mechanism**: Read JSON-RPC from stdin, write to stdout (newline-delimited)
- **Use Case**: Local development, testing, subprocess embedding
- **Advantages**: Simple, no network overhead

**2. SSE (Server-Sent Events)**
- **Mechanism**: HTTP-based server push after initial connection
- **Use Case**: Web frontends needing update streams
- **Characteristics**: Largely one-way (server → client)

**3. WebSocket**
- **Mechanism**: Full-duplex, persistent TCP connection
- **Use Case**: Interactive applications, remote servers, low-latency bidirectional
- **Advantages**: Most flexible and powerful

**Transport Switching Example:**
```python
if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    if transport == "stdio":
        mcp.run_stdio()
    elif transport == "websocket":
        import uvicorn
        uvicorn.run(mcp, host="0.0.0.0", port=8000)
```

### Tool Schema Definition

**Type Mapping:**
- `str` → `"type": "string"`
- `int` → `"type": "integer"`
- `float` → `"type": "number"`
- `bool` → `"type": "boolean"`

**Complex Types with Pydantic:**
```python
from typing import List

class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str

@mcp.tool()
async def web_search(
    query: str = Field(..., description="Search query")
) -> List[SearchResult]:
    """Performs web search and returns results."""
    return [
        SearchResult(
            url="https://example.com",
            title="Example",
            snippet="An example domain"
        )
    ]
```

### Error Handling Patterns

**Built-in Error Handling:**
- Framework catches unhandled exceptions
- Sends standardized error message to client
- Includes error code, message, optional stack trace

**Best Practices:**
1. **Let It Fail**: Don't catch generic `Exception`, let exceptions propagate
2. **Raise Specific Exceptions**:
   - `ValueError`: Invalid parameter values
   - `FileNotFoundError`: Missing required files
   - `PermissionError`: Authorization issues
3. **Custom Exceptions**:
```python
class InsufficientStockError(Exception):
    """Raised when item is out of stock."""
    pass

@mcp.tool()
async def order_product(product_id: str, quantity: int):
    """Orders a product."""
    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    stock = await get_stock_level(product_id)
    if stock < quantity:
        raise InsufficientStockError(
            f"Not enough stock for {product_id}. Available: {stock}"
        )

    return {"status": "order_placed", "product_id": product_id}
```

### Resource and Prompt Decorators

**`@mcp.resource()`**
- **Purpose**: Manage stateful objects with unique IDs
- **Use Case**: File handles, database sessions, browser automation
- **Pattern**: Create resource → get ID → pass ID to other tools

**`@mcp.prompt()`**
- **Purpose**: Serve prompt templates from server
- **Use Case**: Co-locate prompt engineering with tools
- **Pattern**: Agent requests prompt by name → receives template → structures interactions

### Complete Server Example

```python
from typing import List, Optional
from pydantic import BaseModel, Field
from fastmcp import MCP
import asyncio

mcp = MCP(
    title="Advanced File and Data Server",
    description="Server for managing files and data lookups"
)

# Shared state
mock_database = {
    "users": {
        "U01": {"name": "Alice", "email": "alice@example.com"},
        "U02": {"name": "Bob", "email": "bob@example.com"}
    }
}

@mcp.on_event("startup")
async def startup():
    """Server initialization."""
    print("Server initializing...")
    await asyncio.sleep(0.5)
    print("Server ready.")

@mcp.on_event("shutdown")
async def shutdown():
    """Server shutdown."""
    print("Server shutting down.")

class User(BaseModel):
    """User in the system."""
    id: str = Field(..., description="Unique user ID (e.g., 'U01')")
    name: str
    email: Optional[str] = None

@mcp.tool()
async def get_user_by_id(user_id: str) -> Optional[User]:
    """Retrieves user information by ID."""
    user_data = mock_database["users"].get(user_id)
    if not user_data:
        return None
    return User(id=user_id, **user_data)

@mcp.tool()
async def list_all_users() -> List[User]:
    """Returns all users in the system."""
    return [
        User(id=uid, **data)
        for uid, data in mock_database["users"].items()
    ]

@mcp.tool()
async def divide(a: float, b: float) -> float:
    """Divides two numbers. Demonstrates error handling."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    print("Starting server with STDIO transport...")
    mcp.run_stdio()
```

---

## 4. Model Context Protocol Overview

### What is MCP?

The Model Context Protocol (MCP) is a standardized, stateful communication protocol for interaction between AI applications (clients) and AI models/services (servers).

**Purpose:**
- Solve limitations of stateless REST APIs for AI interactions
- Eliminate need to resend conversation history on every turn
- Provide formal structure for tool use, multi-modal content, streaming
- Enable interoperability between different clients, servers, and tools

**Key Innovation:** Shifts paradigm from independent requests to continuous, managed sessions with models.

### Core Concepts and Architecture

**Components:**
1. **Server**: Hosts language models, manages conversation state (Resources)
2. **Client**: Application consuming model capabilities (chatbot, agent, script)
3. **Host**: Environment where server runs (infrastructure, inference engine)
4. **Transport**: Communication layer (WebSocket, stdio, gRPC)

**Decoupling:** Application logic (client) separated from model/state management (server).

### Communication Patterns and Message Flow

**Session-Based Flow:**
1. **Connection & Handshake**: Client establishes connection, sends `connect` message
2. **Create/Load Resource**: Initiate or resume conversation by URI
3. **Send Prompt**: Client sends prompt message within resource context
4. **Server Processing**: Server appends to history, processes with LLM, streams response
5. **Tool Calls** (if applicable):
   - Server sends `tool_call` request to client
   - **Client executes** tool logic (critical security design)
   - Client sends `tool_output` back to server
   - Server continues generation with tool context
6. **End Session**: Connection closed, resource persists for later reload

**Statefulness Advantage:** After initial prompt, only new messages sent, not entire history.

### Three Core Primitives

**1. Resource**
- **Definition**: Stateful conversation context with unique URI
- **Contains**: Complete ordered history (prompts, responses, tool calls, outputs)
- **Metadata**: Model configuration, sampling parameters, available tools
- **Example URI**: `mcp://my-server.com/resources/12345`

**2. Prompt**
- **Definition**: Structured message from client to server
- **Capabilities**: Multi-modal content (text, images, other data types)
- **Purpose**: Elicit model response with rich input

**3. Tool**
- **Definition**: Function the model can request client to execute
- **Flow**:
  1. Server declares available tools to model
  2. Model requests tool invocation (name + arguments)
  3. Protocol standardizes tool definitions (JSON Schema)
  4. Clear, secure contract for external system interaction

### Sampling/LLM Integration

**Model Agnosticism:**
- Server acts as abstraction layer over multiple LLMs
- Client specifies model during resource creation (`claude-3-opus`, `llama3-70b`)
- Server routes to correct backend

**Sampling Parameters:**
- Standard specification: `temperature`, `top_p`, `max_tokens`
- Set at resource creation, overridable per-prompt
- Fine-grained control with standardized interface

**Abstraction Benefit:** Client only speaks MCP, server handles LLM-specific API translation.

### Security Model

**Client-Side Tool Execution (Critical):**
- Server/model can only **request** tool calls, not execute
- Client has full authority to validate, sanitize, sandbox, or reject
- Prevents malicious model from executing arbitrary code or accessing sensitive data

**Authentication & Authorization:**
- Not prescribed by MCP itself
- Handled at transport layer (WebSocket headers, API keys, OAuth)
- Or within initial `connect` message payload
- Server authenticates client and authorizes resource/model access

**Clear Boundaries:**
- Server: State management and model access
- Client: Application logic and tool execution
- Minimizes attack surface area

### Protocol Design Principles

1. **Stateful by Default**: Support rich, long-running interactions efficiently
2. **Model and Transport Agnostic**: Flexibility, no vendor lock-in
3. **Extensible**: Message-based design allows new capabilities without breaking changes
4. **Interoperable**: Common standard for diverse ecosystem
5. **Secure**: Safe interaction model, especially for tool use

### Context Sharing Capability

**Resource URI Sharing:**
1. **Service A** creates resource, has multi-turn conversation
2. Escalation needed → Service A passes resource URI to **Service B**
3. Service B connects to same MCP server, loads resource by URI
4. Service B has **entire conversation history** instantly
5. Seamless continuation without context loss

**Power:** Enables complex multi-agent systems and workflow handoffs.

---

## 5. MCP Protocol Specification (2025-06-18)

### Protocol Foundation

**Core Technology:** JSON-RPC 2.0

**Key Characteristics:**
- Stateful sessions (not stateless REST)
- Bidirectional communication
- Session lifecycle: `initialize` → operations → `shutdown`

**Message Types:**
- **Request**: `jsonrpc: "2.0"`, unique `id`, `method`, optional `params`
- **Response**: `jsonrpc: "2.0"`, corresponding `id`, `result` or `error`
- **Notification**: Request without `id`, no response expected

### Tool Schema Requirements

**Standard:** JSON Schema (Draft 2020-12)

**Required Fields:**
```json
{
  "tool_id": "weather/getCurrentWeather",
  "description": "Get current weather for location",
  "parameters_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City and state, e.g., San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "default": "celsius"
      }
    },
    "required": ["location"]
  },
  "returns_schema": {
    "type": "object",
    "properties": {
      "temperature": {"type": "number"},
      "unit": {"type": "string"},
      "conditions": {"type": "string"}
    },
    "required": ["temperature", "unit", "conditions"]
  }
}
```

### Session Lifecycle

**1. Connection**
- Transport-layer connection established

**2. Initialization**
- Client: `initialize` request with capabilities
- Server: `initialize` response with server capabilities
- Client: `initialized` notification (session active)

**3. Operations**
- `mcp/tools/list`: Get available tool schemas
- `mcp/tools/invoke`: Execute tool with parameters
- `mcp/resources/create`: Instantiate stateful object, get ID
- `mcp/resources/delete`: Clean up resource

**4. Termination**
- Client: `shutdown` notification (stop new requests)
- Client: `exit` notification (terminate server)

### Message Types by Namespace

**Session (`mcp/session/`):**
- `initialize`: Capability negotiation
- `initialized`: Initialization complete
- `shutdown`: Graceful session end
- `exit`: Terminate server process

**Tools (`mcp/tools/`):**
- `list`: Get all tool schemas
- `invoke`: Execute specific tool

**Resources (`mcp/resources/`):**
- `create`: Create stateful resource, return ID
- `get`: Retrieve resource state
- `update`: Modify resource
- `delete`: Destroy resource

**UI (`mcp/ui/`):**
- `prompt`: Server-to-client notification for user input

### Schema Validation Requirements

**Server-Side (MUST):**
- Validate `params` against `parameters_schema` on every `invoke`
- Return JSON-RPC error `InvalidParams` (-32602) on validation failure
- Include details in error `data` field

**Client-Side (SHOULD):**
- Validate `result` against `returns_schema`
- Trust data and guard against server bugs
- Validate own parameters before sending

### Error Handling and Status Codes

**Standard JSON-RPC Codes:**
- `-32700`: Parse Error (invalid JSON)
- `-32600`: Invalid Request (not valid JSON-RPC)
- `-32601`: Method Not Found
- `-32602`: Invalid Params
- `-32603`: Internal Error

**MCP-Specific Codes (-32000 to -32099):**
- `-32001`: InitializationFailed
- `-32002`: ToolExecutionError
- `-32003`: ResourceNotFound
- `-32004`: AccessDenied

**Error Object:**
```json
{
  "code": -32602,
  "message": "Invalid params",
  "data": {
    "validation_errors": ["location is required"]
  }
}
```

### Server Implementation Best Practices

1. **Separate Protocol from Logic**: Isolate MCP message handling from tool implementation
2. **Asynchronous Execution**: Process long-running tools asynchronously
3. **Progress Updates**: For tasks >2-3 seconds, send server-to-client notifications
4. **Session Management**: Timeout/GC for abandoned sessions
5. **Security Sandboxing**: Never execute code/shell commands from parameters
6. **Clear Descriptions**: Tool `description` quality paramount for model understanding

### Versioning and Compatibility

**Version Negotiation:**
- Client sends supported version in `clientInfo`
- Server responds with session version in `serverInfo`
- Multiple version support possible
- `InitializationFailed` if no mutual version

**Date-Based Versioning:** `2025-06-18` suggests breaking changes tied to spec dates.

### Transport Layer Requirements

**Transport Agnostic:** Specification defines message format only.

**Common Transports:**
1. **stdio (stdin/stdout)**
   - Use case: Local child processes, development
   - Advantages: Simple, no network overhead

2. **WebSockets**
   - Use case: Network communication, web clients
   - Advantages: Persistent, low-latency, bidirectional

3. **TCP Sockets**
   - Use case: Inter-process, server-to-server
   - Advantages: Reliable, controlled network

**Implementation:** Layered design allows easy transport swapping.

---

## 6. Implementation Insights for vnprices-mcp

### Current Architecture Alignment

**Correctly Implemented:**
1. **FastMCP Pattern**: All tools use `@mcp.tool()` decorator
2. **Stateless Design**: Each tool invocation in fresh container
3. **Error Handling**: Try-catch blocks with informative messages
4. **JSON Returns**: All functions return JSON strings
5. **Pydantic Usage**: Type hints for parameter validation
6. **stdio Transport**: Proper transport for containerized deployment

### Dual Data Source Pattern

**Critical Implementation in `get_index_history`:**
```python
@mcp.tool()
def get_index_history(symbol: str, start: str, end: str, interval: str = "1D") -> str:
    """Get historical prices for Vietnamese or international indices."""
    try:
        # Vietnamese indices → VCI source via Quote
        if symbol in ["VNINDEX", "HNXINDEX", "UPCOMINDEX"]:
            quote = Quote(symbol)
            df = quote.history(start=start, end=end, interval=interval)

        # International indices → MSN source via Vnstock
        else:
            vnstock = Vnstock()
            df = vnstock.world_index(symbol=symbol, start=start, end=end, interval=interval)

        return df.to_json(orient="records", date_format="iso")
    except Exception as e:
        return f"Error: {str(e)}"
```

**Why This Matters:**
- Different data sources have different capabilities
- Routing logic ensures correct API calls
- Prevents errors from using wrong source

### Container Orchestration Flow

**vnprices-mcp Data Flow:**
```
Claude Desktop
    ↓ (stdio transport)
MCP Gateway (Docker MCP Gateway container)
    ↓ (docker run vnprices-mcp:latest)
vnprices Container (fresh instance per tool call)
    ↓ (vnstock3 library)
Quote/Vnstock objects
    ↓ (HTTP requests)
VCI/MSN Data Sources
    ↓ (JSON responses)
pandas DataFrame processing
    ↓ (JSON string)
Return path: Container → Gateway → Claude Desktop
```

**Key Constraints:**
- No state between calls (stateless tools only)
- Each invocation spins up new container
- Container size ~1.2GB (consider startup time)
- No API keys needed (vnstock3 handles internally)

### Configuration Management

**Current Setup:**
```
~/.docker/mcp/
├── config.yaml          # Gateway config: vnprices enabled
├── registry.yaml        # Points to catalogs
└── catalogs/
    └── custom.yaml      # vnprices tool definitions
```

**Critical Maintenance:**
- Tool changes in `server.py` require catalog updates
- Catalog must reflect actual tool signatures
- Gateway restart needed after catalog changes
- Claude Desktop restart required for tool discovery

### Docker Build Optimization

**Current Dockerfile Pattern:**
```dockerfile
FROM python:3.11-slim

# System dependencies for wordcloud/vnstock3
RUN apt-get update && apt-get install -y \
    gcc g++ build-essential python3-dev \
    libfreetype6-dev libpng-dev libjpeg-dev pkg-config

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

ENTRYPOINT ["python3", "server.py"]
```

**Why System Dependencies Matter:**
- vnstock3 depends on wordcloud
- wordcloud requires compilation (C extensions)
- Image libraries needed for visual processing
- Without these, build fails

### Best Practices for vnprices-mcp

**1. Adding New Tools:**
```python
# 1. Add to server.py
@mcp.tool()
def get_bond_history(symbol: str, start: str, end: str) -> str:
    """Get bond historical prices."""
    try:
        # Implementation using vnstock3
        return json.dumps(result)
    except Exception as e:
        return f"Error: {str(e)}"

# 2. Rebuild container
# docker build --no-cache -t vnprices-mcp:latest .

# 3. Update ~/.docker/mcp/catalogs/custom.yaml
# tools:
#   - name: get_bond_history

# 4. Restart Claude Desktop (Cmd+Q, reopen)
```

**2. Debugging Tools Not Appearing:**
```bash
# Check gateway logs
docker logs -f $(docker ps -q -f ancestor=docker/mcp-gateway)

# Look for:
# - "Enabled servers: vnprices"
# - "X tools listed"

# Verify image exists
docker images | grep vnprices-mcp
```

**3. Debugging Data Fetching:**
```bash
# Test vnstock3 directly in container
docker run -it vnprices-mcp:latest python3 -c "
from vnstock import Quote
q = Quote('VCI')
print(q.history('2024-01-01', '2024-12-31'))
"
```

**4. View Runtime Logs:**
```bash
# Find vnprices container ID when tool is called
docker ps -a | grep vnprices

# View logs
docker logs <container-id> --tail 100
```

### Performance Considerations

**Container Startup Overhead:**
- Fresh container per tool call = ~1-2 second overhead
- Acceptable for financial data queries (not real-time)
- Alternative: Keep container alive (requires architecture change)

**Data Fetching Time:**
- vnstock3 fetches from external APIs
- Network latency varies by source (VCI vs MSN)
- Historical data queries typically 2-5 seconds
- Consider caching for frequently requested data (future enhancement)

**Memory Usage:**
- Base Python 3.11 slim: ~150MB
- vnstock3 + dependencies: ~1GB
- pandas + data processing: variable
- Container limit: Define in catalog YAML

### Future Enhancement Opportunities

**1. Caching Layer:**
```python
# Add Redis or in-memory cache for frequent queries
# Cache key: (symbol, start, end, interval)
# TTL: 1 hour for historical data
```

**2. Async Implementation:**
```python
# Current: Synchronous blocking
@mcp.tool()
def get_stock_history(...) -> str:
    # Blocks until complete

# Future: Async for concurrency
@mcp.tool()
async def get_stock_history(...) -> str:
    # Allows concurrent requests
    async with aiohttp.ClientSession() as session:
        # Async HTTP requests
```

**3. Resource Management:**
```python
# Current: Stateless tools only
# Future: Stateful resources
@mcp.resource()
class StockWatcher:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.cache = {}

    async def watch(self):
        # Persistent monitoring
```

**4. Batch Operations:**
```python
@mcp.tool()
def get_multiple_stocks(
    symbols: List[str],
    start: str,
    end: str
) -> str:
    """Fetch multiple stocks in one call to reduce overhead."""
    results = {}
    for symbol in symbols:
        # Fetch all at once
    return json.dumps(results)
```

### Security Considerations

**Current Security Posture:**
- No authentication (vnstock3 uses public APIs)
- No user input validation beyond type hints
- Container isolation provides sandbox
- stdio transport prevents network exposure

**Recommendations:**
1. **Input Sanitization:**
```python
import re

@mcp.tool()
def get_stock_history(symbol: str, start: str, end: str) -> str:
    # Validate symbol format (prevent injection)
    if not re.match(r'^[A-Z0-9]{1,10}$', symbol):
        return "Error: Invalid symbol format"

    # Validate date format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', start):
        return "Error: Invalid date format (use YYYY-MM-DD)"
```

2. **Rate Limiting:**
```python
# Add rate limiting to prevent API abuse
from datetime import datetime, timedelta

request_log = {}

def check_rate_limit(client_id: str) -> bool:
    if client_id in request_log:
        if datetime.now() - request_log[client_id] < timedelta(seconds=1):
            return False
    request_log[client_id] = datetime.now()
    return True
```

3. **Error Message Sanitization:**
```python
# Current: Exposes full exception
return f"Error: {str(e)}"

# Better: Sanitize sensitive info
try:
    # ...
except Exception as e:
    error_msg = str(e)
    # Remove any API keys, URLs, or sensitive data
    sanitized = re.sub(r'api_key=\w+', 'api_key=***', error_msg)
    return f"Error: {sanitized}"
```

### Testing Strategy

**Current Testing Gap:**
- No automated tests
- Manual testing via Docker commands

**Recommended Test Suite:**

**1. Unit Tests (server.py):**
```python
# tests/test_tools.py
import pytest
from server import get_stock_history, get_forex_history

def test_get_stock_history_valid():
    result = get_stock_history("VCI", "2024-01-01", "2024-01-31")
    assert "Error" not in result
    data = json.loads(result)
    assert len(data) > 0

def test_get_stock_history_invalid_symbol():
    result = get_stock_history("INVALID", "2024-01-01", "2024-01-31")
    assert "Error" in result

def test_date_format_validation():
    result = get_stock_history("VCI", "2024/01/01", "2024-01-31")
    assert "Error" in result
```

**2. Integration Tests (Docker):**
```bash
#!/bin/bash
# tests/test_container.sh

# Build image
docker build -t vnprices-mcp:test .

# Test vnstock3 import
docker run vnprices-mcp:test python3 -c "from vnstock import Quote; print('OK')"

# Test data fetching
docker run vnprices-mcp:test python3 -c "
from vnstock import Quote
q = Quote('VCI')
df = q.history('2024-01-01', '2024-01-31')
assert len(df) > 0
print('OK')
"
```

**3. MCP Protocol Tests:**
```python
# tests/test_mcp_protocol.py
from mcp.server.fastmcp import FastMCP

def test_tools_registered():
    # Verify all tools registered correctly
    tools = mcp.list_tools()
    assert len(tools) == 4
    assert "get_stock_history" in [t.name for t in tools]

def test_tool_schemas():
    # Verify schemas are valid JSON Schema
    tools = mcp.list_tools()
    for tool in tools:
        assert "parameters" in tool.schema
        assert "description" in tool.schema
```

---

## Conclusion

This comprehensive research provides a solid foundation for understanding and extending the vnprices-mcp server. The key insights are:

1. **vnstock3** provides a well-designed, pandas-centric API for Vietnamese financial data with clear source routing patterns
2. **Docker MCP Gateway** orchestrates containers using file-based configuration and stdio transport for simple, secure communication
3. **FastMCP** offers a Pythonic, decorator-based framework with automatic schema generation and transport abstraction
4. **MCP Protocol** defines a stateful, JSON-RPC 2.0 based standard with client-side tool execution for security
5. **vnprices-mcp** correctly implements these patterns but has opportunities for enhancement in caching, async operations, testing, and security

The current implementation is production-ready for basic use cases. The identified enhancement opportunities provide a roadmap for scaling and hardening the system for more demanding applications.

---

**Research Completed:** 2025-11-02
**Tools Used:** Zen MCP (gemini-2.5-pro)
**Next Steps:** Review findings, prioritize enhancements, implement testing framework
