#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Simple Resume MCP Server...${NC}"

# 1. Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

# 2. Check for ngrok token
if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo "⚠️  NGROK_AUTHTOKEN not found in .env"
    echo "   Please create .env with NGROK_AUTHTOKEN=your_token"
    exit 1
fi

# 3. Start FastAPI Server
echo "Starting FastAPI server..."
nohup uvicorn server:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > server.pid
echo -e "${GREEN}✓ Server running (PID: $SERVER_PID)${NC}"

# 4. Start ngrok
echo "Starting ngrok..."
if [ -z "$NGROK_DOMAIN" ]; then
    nohup ngrok http 8000 --log=stdout > ngrok.log 2>&1 &
else
    nohup ngrok http 8000 --domain=$NGROK_DOMAIN --log=stdout > ngrok.log 2>&1 &
fi
NGROK_PID=$!
echo $NGROK_PID > ngrok.pid
echo -e "${GREEN}✓ ngrok running (PID: $NGROK_PID)${NC}"

# 5. Wait for ngrok to initialize
echo "Waiting for tunnel..."
sleep 3

# 6. Get public URL
PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✓ Resume MCP Server is LIVE!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "  Local:   http://localhost:8000"
echo "  Public:  $PUBLIC_URL"
echo ""
echo "  MCP Endpoint: $PUBLIC_URL/mcp"
echo ""
echo "  Logs:    tail -f server.log ngrok.log"
echo "  Stop:    ./stop.sh"
echo ""
echo -e "${BLUE}👉 Use this URL in ChatGPT Custom GPT Action${NC}"
echo -e "${BLUE}=========================================${NC}"
