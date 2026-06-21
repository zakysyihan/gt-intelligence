FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY static/ ./static/
COPY data/ ./data/
COPY .streamlit/ .streamlit/
COPY start.sh .

RUN chmod +x start.sh

# Expose both ports
EXPOSE 8000 8501

# Start both services
CMD ["./start.sh"]
