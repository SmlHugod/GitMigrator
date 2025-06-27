#!/bin/bash
# Gitea to GitHub Migration Tool Launcher

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the migration tool with all passed arguments
python migrate.py "$@" 