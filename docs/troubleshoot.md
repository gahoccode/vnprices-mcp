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