#!/bin/bash
set -e

# Validate PORT for Render
PORT=${PORT:-10000}

echo "Starting deployment on port $PORT..."

# 1. Start the Backend API in the background
# We bind to 127.0.0.1:5000 so it's only accessible internally (and by the frontend)
echo "Starting Backend on port 5000..."
cd backend
gunicorn app:app --bind 127.0.0.1:5000 --workers 2 --threads 2 --timeout 60 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to initialize
sleep 3

# 2. Start the Frontend App in the foreground
# This one binds to 0.0.0.0:$PORT so it's accessible from the internet via Render
echo "Starting Frontend on port $PORT..."
cd frontend
# Using exec ensures the frontend process takes over the shell and receives signals
exec gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 60
