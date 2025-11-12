#!/bin/bash
# Stop Resume MCP Server + ngrok

echo "========================================="
echo "  Stopping Resume MCP Server"
echo "========================================="

# Kill server
if [ -f server.pid ]; then
    SERVER_PID=$(cat server.pid)
    if kill -0 $SERVER_PID 2>/dev/null; then
        echo "Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null
        rm server.pid
        echo "✓ Server stopped"
    else
        echo "✓ Server not running"
        rm server.pid
    fi
else
    echo "✓ No server PID file"
fi

# Kill ngrok
if [ -f ngrok.pid ]; then
    NGROK_PID=$(cat ngrok.pid)
    if kill -0 $NGROK_PID 2>/dev/null; then
        echo "Stopping ngrok (PID: $NGROK_PID)..."
        kill $NGROK_PID 2>/dev/null
        rm ngrok.pid
        echo "✓ ngrok stopped"
    else
        echo "✓ ngrok not running"
        rm ngrok.pid
    fi
else
    echo "✓ No ngrok PID file"
fi

# Fallback: kill by port and name
lsof -ti:8000 | xargs kill -9 2>/dev/null
pkill -9 -f "ngrok" 2>/dev/null

echo ""
echo "========================================="
echo "  ✓ All stopped!"
echo "========================================="

