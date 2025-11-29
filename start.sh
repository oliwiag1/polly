#!/bin/bash

# Polly Application Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Show help
show_help() {
    cat << EOF
Polly - Survey Application Management Script

Usage: ./start.sh [command]

Commands:
    dev             Start development environment (backend + frontend)
    dev-backend     Start only backend development server
    dev-frontend    Start only frontend development server
    docker          Build and start Docker containers
    docker-build    Build Docker images without starting
    docker-down     Stop and remove Docker containers
    docker-logs     Show Docker container logs
    stop            Stop all running services
    clean           Clean all build artifacts and containers
    install         Install all dependencies
    test            Run tests
    help            Show this help message

Examples:
    ./start.sh dev              # Start development servers
    ./start.sh docker           # Start with Docker Compose
    ./start.sh docker-logs      # View container logs

EOF
}

# Install dependencies
install_deps() {
    print_message "$BLUE" "📦 Installing dependencies..."
    
    print_message "$YELLOW" "Installing backend dependencies..."
    cd backend
    pip install -r requirements.txt
    cd ..
    
    print_message "$YELLOW" "Installing frontend dependencies..."
    cd client
    npm install
    cd ..
    
    print_message "$GREEN" "✅ Dependencies installed successfully!"
}

# Start development backend
start_dev_backend() {
    print_message "$BLUE" "🚀 Starting backend development server..."
    cd backend
    python -m app.main
}

# Start development frontend
start_dev_frontend() {
    print_message "$BLUE" "🚀 Starting frontend development server..."
    cd client
    npm run dev
}

# Start development environment
start_dev() {
    print_message "$BLUE" "🚀 Starting development environment..."
    
    # Start backend in background
    print_message "$YELLOW" "Starting backend on http://localhost:8000"
    cd backend
    python -m app.main &
    BACKEND_PID=$!
    cd ..
    
    # Wait a bit for backend to start
    sleep 3
    
    # Start frontend
    print_message "$YELLOW" "Starting frontend on http://localhost:5173"
    cd client
    npm run dev
    
    # Cleanup on exit
    trap "kill $BACKEND_PID 2>/dev/null" EXIT
}

# Start Docker containers
start_docker() {
    print_message "$BLUE" "🐳 Building and starting Docker containers..."
    docker-compose up --build
}

# Build Docker images
build_docker() {
    print_message "$BLUE" "🐳 Building Docker images..."
    docker-compose build
    print_message "$GREEN" "✅ Docker images built successfully!"
}

# Stop Docker containers
stop_docker() {
    print_message "$BLUE" "🛑 Stopping Docker containers..."
    docker-compose down
    print_message "$GREEN" "✅ Docker containers stopped!"
}

# Show Docker logs
docker_logs() {
    print_message "$BLUE" "📋 Showing Docker container logs..."
    docker-compose logs -f
}

# Stop all services
stop_all() {
    print_message "$BLUE" "🛑 Stopping all services..."
    
    # Stop any running Python processes
    pkill -f "python -m app.main" 2>/dev/null || true
    
    # Stop any running npm processes
    pkill -f "vite" 2>/dev/null || true
    
    # Stop Docker containers
    docker-compose down 2>/dev/null || true
    
    print_message "$GREEN" "✅ All services stopped!"
}

# Clean all build artifacts
clean_all() {
    print_message "$BLUE" "🧹 Cleaning build artifacts..."
    
    # Stop services first
    stop_all
    
    # Remove frontend build artifacts
    print_message "$YELLOW" "Cleaning frontend..."
    cd client
    rm -rf dist node_modules .vite
    cd ..
    
    # Remove Python cache
    print_message "$YELLOW" "Cleaning backend..."
    find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find backend -type f -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove Docker containers and images
    print_message "$YELLOW" "Cleaning Docker..."
    docker-compose down -v --rmi local 2>/dev/null || true
    
    print_message "$GREEN" "✅ Cleanup completed!"
}

# Run tests
run_tests() {
    print_message "$BLUE" "🧪 Running tests..."
    
    print_message "$YELLOW" "Running backend tests..."
    cd backend
    pytest 2>/dev/null || print_message "$YELLOW" "No backend tests found"
    cd ..
    
    print_message "$YELLOW" "Running frontend tests..."
    cd client
    npm run test 2>/dev/null || print_message "$YELLOW" "No frontend tests configured"
    cd ..
}

# Main script logic
case "${1:-help}" in
    dev)
        start_dev
        ;;
    dev-backend)
        start_dev_backend
        ;;
    dev-frontend)
        start_dev_frontend
        ;;
    docker)
        start_docker
        ;;
    docker-build)
        build_docker
        ;;
    docker-down)
        stop_docker
        ;;
    docker-logs)
        docker_logs
        ;;
    stop)
        stop_all
        ;;
    clean)
        clean_all
        ;;
    install)
        install_deps
        ;;
    test)
        run_tests
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_message "$RED" "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
