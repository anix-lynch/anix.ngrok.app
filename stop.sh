#!/bin/bash

echo "Stopping Resume MCP Server..."

if [ -f server.pid ]; then
    kill $(cat server.pid) 2>/dev/null
    rm server.pid
    echo "✓ Server stopped"
fi

if [ -f ngrok.pid ]; then
    kill $(cat ngrok.pid) 2>/dev/null
    rm ngrok.pid
    echo "✓ ngrok stopped"
fi

# Cleanup any stragglers
pkill -f "uvicorn server:app"
pkill -f "ngrok http 8000"

echo "Done."
