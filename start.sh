#!/bin/bash
set -e

echo "========================================"
echo "  Orthodontic Patient Chat - Startup"
echo "========================================"

# Install backend deps
echo ""
echo "[1/3] Installing Python dependencies..."
cd backend
pip install -r requirements.txt -q
echo "Done."

# Start backend in background
echo ""
echo "[2/3] Starting FastAPI backend on http://localhost:8000 ..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Install and start frontend
echo ""
echo "[3/3] Installing and starting React frontend on http://localhost:3000 ..."
cd ../frontend
npm install --silent
npm start &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "  App running!"
echo "  Patient portal:     http://localhost:3000"
echo "  API docs:           http://localhost:8000/docs"
echo "  Professor login:    professor@clinic.edu / professor123"
echo "========================================"
echo ""
echo "Optional: Install Ollama for AI responses"
echo "  curl -fsSL https://ollama.com/install.sh | sh"
echo "  ollama pull llama3"
echo ""
echo "Press Ctrl+C to stop all services."

wait $BACKEND_PID $FRONTEND_PID
