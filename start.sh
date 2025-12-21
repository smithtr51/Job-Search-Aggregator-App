#!/bin/bash

# LinkedIn-Style Job Search Aggregator - Startup Script
# This script helps you start both backend and frontend servers

echo "🎯 LinkedIn-Style Job Search Aggregator"
echo "========================================"
echo ""

# Check if API keys are set
if [ -z "$SCRAPERAPI_KEY" ]; then
    echo "⚠️  Warning: SCRAPERAPI_KEY not set"
    echo "   Add to ~/.zshrc: export SCRAPERAPI_KEY='your_key_here'"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set"
    echo "   Add to ~/.zshrc: export ANTHROPIC_API_KEY='your_key_here'"
fi

echo ""
echo "Starting services..."
echo ""

# Function to start backend
start_backend() {
    echo "📡 Starting FastAPI backend on port 8000..."
    PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
    cd "$PROJECT_DIR"
    source venv/bin/activate
    cd api
    uvicorn main:app --reload --port 8000 &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    echo "⚛️  Starting React frontend on port 5173..."
    PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
    cd "$PROJECT_DIR/frontend"
    npm run dev &
    FRONTEND_PID=$!
    echo "   Frontend PID: $FRONTEND_PID"
}

# Start both services
start_backend
sleep 3
start_frontend

echo ""
echo "✅ Services started!"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

wait

