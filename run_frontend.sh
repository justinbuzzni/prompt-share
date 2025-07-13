#!/bin/bash

# Claude Viewer Frontend Runner

echo "Starting Claude Viewer Frontend..."

# Change to frontend directory
cd "$(dirname "$0")/claude-viewer-frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dependencies not found. Installing..."
    npm install
fi

# Run the React app
npm start