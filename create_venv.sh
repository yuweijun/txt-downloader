#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv venv

echo "Installing dependencies..."
source venv/bin/activate
pip install requests beautifulsoup4

echo ""
echo "=============================================="
echo "Setup completed successfully!"
echo "To run the scraper:"
echo "source venv/bin/activate && python scraper.py YOUR_URL"
echo "=============================================="