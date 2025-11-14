#!/bin/bash
# Job Automation Setup Script

echo "=========================================="
echo "Job Application Automation Setup"
echo "=========================================="

# Check Python version
echo -e "\n[1/5] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Create virtual environment
echo -e "\n[2/5] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo -e "\n[3/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo -e "\n[4/5] Installing Playwright browsers..."
playwright install chromium

# Create output directory
echo -e "\n[5/5] Creating output directory..."
mkdir -p output

# Test resume endpoint
echo -e "\n=========================================="
echo "Testing resume endpoint..."
echo "=========================================="
curl -s https://anix.ngrok.app/health | python3 -m json.tool || echo "Warning: Could not reach resume endpoint"

echo -e "\n=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run dry run: python orchestrator.py --dry-run"
echo "  3. Read QUICKSTART.md for full guide"
echo ""
echo "Quick test:"
echo "  python orchestrator.py --scrape-limit 10 --tier1-apps 5 --dry-run"
echo ""
