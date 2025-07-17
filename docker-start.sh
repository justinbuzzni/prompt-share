#!/bin/bash

# Docker Compose startup script for Prompt Share

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Created .env file from .env.example"
        print_warning "Please edit .env file with your configuration before running again."
        exit 1
    else
        print_error ".env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

# Parse command line arguments
MODE="production"
REBUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev|--development)
            MODE="development"
            shift
            ;;
        --rebuild)
            REBUILD=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--dev|--development] [--rebuild] [--help|-h]"
            echo ""
            echo "Options:"
            echo "  --dev, --development    Run in development mode"
            echo "  --rebuild              Rebuild containers before starting"
            echo "  --help, -h             Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Select docker-compose file based on mode
if [ "$MODE" = "development" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    print_status "Starting in development mode..."
else
    COMPOSE_FILE="docker-compose.yml"
    print_status "Starting in production mode..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    print_error "docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down

# Rebuild containers if requested
if [ "$REBUILD" = true ]; then
    print_status "Rebuilding containers..."
    docker-compose -f $COMPOSE_FILE build --no-cache
fi

# Start services
print_status "Starting services..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
print_status "Waiting for services to start..."
sleep 10

# Check service status
print_status "Checking service status..."
docker-compose -f $COMPOSE_FILE ps

print_status "Application started successfully!"
print_status ""
print_status "Services:"
print_status "  Frontend: http://localhost:3000"
print_status "  Backend API: http://localhost:8000"
print_status "  MongoDB: localhost:27017"
print_status "  Elasticsearch: http://localhost:9200"
print_status ""
print_status "To stop the application, run:"
print_status "  docker-compose -f $COMPOSE_FILE down"
print_status ""
print_status "To view logs, run:"
print_status "  docker-compose -f $COMPOSE_FILE logs -f"