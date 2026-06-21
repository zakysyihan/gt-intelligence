#!/bin/bash
# Start both FastAPI (port 8000) and Streamlit (port 8501)

echo "Starting GT Intelligence..."

# Start FastAPI backend on port 8000
echo "Starting FastAPI on port 8000..."
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 &

# Start Streamlit on port 8501
echo "Starting Streamlit on port 8501..."
streamlit run src/app/app.py --server.port=8501 --server.address=0.0.0.0 &

echo "Services started:"
echo "  - Custom UI: http://localhost:8000"
echo "  - Streamlit: http://localhost:8501"

wait
