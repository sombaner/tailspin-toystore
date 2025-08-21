FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/server

# Install build essentials (in case some deps need compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy server requirements and install
COPY server/requirements.txt /app/server/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ /app/server/

# Copy demo DB into image for simplicity (ephemeral)
RUN mkdir -p /app/data
COPY data/tailspin-toys.db /app/data/tailspin-toys.db

EXPOSE 5100
CMD ["python", "app.py"]
