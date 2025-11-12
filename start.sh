#!/bin/bash
# Start Resume MCP Server + ngrok

# Load environment
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Default values
PORT=${SERVER_PORT:-8000}
DOMAIN=${NGROK_DOMAIN:-anix.ngrok.app}

echo "========================================="
echo "  Starting Resume MCP Server"
echo "========================================="

# Kill existing processes
echo "Cleaning up old processes..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null
pkill -9 -f ngrok 2>/dev/null
sleep 1

# Start Python server
echo "Starting server on port $PORT..."
python3 server.py > server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > server.pid
echo "✓ Server running (PID: $SERVER_PID)"
sleep 2

# Start ngrok
echo "Starting ngrok tunnel..."
if [ -n "$NGROK_AUTHTOKEN" ]; then
    ngrok config add-authtoken $NGROK_AUTHTOKEN 2>/dev/null
fi

ngrok http --domain=$DOMAIN $PORT > ngrok.log 2>&1 &
NGROK_PID=$!
echo $NGROK_PID > ngrok.pid
echo "✓ ngrok running (PID: $NGROK_PID)"
sleep 3

echo ""
echo "========================================="
echo "  ✓ Resume MCP Server is LIVE!"
echo "========================================="
echo ""
echo "  Public:  https://$DOMAIN"
echo "  Local:   http://localhost:$PORT"
echo ""
echo "  Health:  https://$DOMAIN/health"
echo "  Resume:  https://$DOMAIN/resume"
echo ""
echo "  Logs:    tail -f server.log ngrok.log"
echo "  Stop:    ./stop.sh"
echo ""
echo "========================================="

