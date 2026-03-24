FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY rurussian_mcp ./rurussian_mcp
COPY README.md .

# Install the package
RUN pip install --no-cache-dir -e .

# Set default command
ENTRYPOINT ["rurussian-mcp"]
