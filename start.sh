#!/bin/bash

# Setup virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

# Start with PM2
pm2 start ecosystem.config.js