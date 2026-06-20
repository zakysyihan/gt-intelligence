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
COPY data/ ./data/
COPY .streamlit/ .streamlit/

# Expose Streamlit port
EXPOSE 8000

# Run Streamlit
CMD ["streamlit", "run", "src/app/app.py", "--server.port=8000", "--server.address=0.0.0.0"]
