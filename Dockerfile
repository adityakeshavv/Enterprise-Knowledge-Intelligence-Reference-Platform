FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and reference database
COPY backend /app/backend
COPY config /app/config
COPY main.py /app/main.py
COPY backend/nebula9_reference.db /app/nebula9_reference.db

ENV PYTHONPATH=/app/backend:/app
ENV PORT=8000

EXPOSE 8000

CMD ["python", "main.py"]
