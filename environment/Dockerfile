FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application files into /app/
COPY app/ /app/

# Install pinned dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Make start script executable
RUN chmod +x /app/start.sh

EXPOSE 8080

CMD ["/app/start.sh"]
