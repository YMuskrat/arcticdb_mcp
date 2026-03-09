FROM python:3.12-slim

RUN pip install --no-cache-dir arcticdb-mcp

ENV ARCTICDB_URI=""
ENV ARCTICDB_MCP_PORT=""

# Expose HTTP/SSE port (only used when ARCTICDB_MCP_PORT is set)
EXPOSE 8000

CMD ["python", "-m", "arcticdb_mcp"]
