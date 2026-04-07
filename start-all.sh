#!/bin/bash

# Meetstream AI - Start All Services
echo "[START] Starting Meetstream AI Platform..."

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "[WARN] tmux not found. Installing with brew..."
    brew install tmux
fi

# Kill any existing tmux session
tmux kill-session -t meetstream 2>/dev/null

# Create new tmux session
tmux new-session -d -s meetstream -n "Meetstream AI"

# Window 1: Backend
tmux send-keys -t meetstream "cd backend && ./start.sh" C-m

# Split window horizontally
tmux split-window -h -t meetstream

# Window 2: Frontend
tmux send-keys -t meetstream "cd frontend && npm run dev" C-m

# Attach to session
echo ""
echo "[READY] All services started in tmux session 'meetstream'"
echo ""
echo "Commands:"
echo "  - View services: tmux attach -t meetstream"
echo "  - Detach: Press Ctrl+B then D"
echo "  - Stop all: tmux kill-session -t meetstream"
echo ""
echo "Services:"
echo "  - Backend:  http://localhost:8000"
echo "  - Frontend: http://localhost:5173"
echo "  - Health:   http://localhost:8000/health"
echo ""

# Attach to the session
tmux attach -t meetstream
