#!/bin/bash

# Claude Viewer API Server Runner

echo "Starting Claude Viewer API Server..."

# Change to script directory
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

# Run the FastAPI server with uvicorn
.venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 15011 --reload