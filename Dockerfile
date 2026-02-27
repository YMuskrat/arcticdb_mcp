FROM python:3.12-slim

RUN pip install --no-cache-dir arcticdb-mcp

ENV ARCTICDB_URI=""

CMD ["python", "-m", "arcticdb_mcp"]
