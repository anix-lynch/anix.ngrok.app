#!/bin/bash
# Start PUBLIC Resume API Server (NO AUTH)
# For Perplexity, ChatGPT, Claude, and other AI tools

# Load environment
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Default values
PORT=${SERVER_PORT:-8000}
DOMAIN=${NGROK_DOMAIN:-anix.ngrok.app}

echo "========================================="
echo "  Starting PUBLIC Resume API Server"
echo "  NO AUTHENTICATION - AI Accessible"
echo "========================================="

# Kill existing processes
echo "Cleaning up old processes..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null
pkill -9 -f ngrok 2>/dev/null
sleep 1

# Start PUBLIC Python server
echo "Starting PUBLIC server on port $PORT..."
python3 server_public.py > server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > server.pid
echo "✓ Server running (PID: $SERVER_PID)"
sleep 2

# Start ngrok WITHOUT authentication
echo "Starting ngrok tunnel (PUBLIC - no auth)..."
if [ -n "$NGROK_AUTHTOKEN" ]; then
    ngrok config add-authtoken $NGROK_AUTHTOKEN 2>/dev/null
fi

# Start ngrok without IP restrictions or authentication
ngrok http --domain=$DOMAIN $PORT > ngrok.log 2>&1 &
NGROK_PID=$!
echo $NGROK_PID > ngrok.pid
echo "✓ ngrok running (PID: $NGROK_PID)"
sleep 3

echo ""
echo "========================================="
echo "  ✓ PUBLIC Resume API is LIVE!"
echo "========================================="
echo ""
echo "  Public:  https://$DOMAIN/resume"
echo "  Health:  https://$DOMAIN/health"
echo "  Summary: https://$DOMAIN/summary"
echo ""
echo "  ✓ NO AUTHENTICATION REQUIRED"
echo "  ✓ Accessible by: Perplexity, ChatGPT, Claude, etc."
echo ""
echo "  Test:"
echo "    curl https://$DOMAIN/resume"
echo ""
echo "  Logs:    tail -f server.log ngrok.log"
echo "  Stop:    ./stop.sh"
echo ""
echo "========================================="
