#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
export FLASK_APP=backend/app.py
export FLASK_ENV=development

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and fill in your AWS credentials."
    exit 1
fi

echo "Starting MEP Agent..."
python3 -m flask run --host=0.0.0.0 --port=5000
