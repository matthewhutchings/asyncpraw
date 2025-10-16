#!/bin/bash

# Deployment script for Reddit API Wrapper

set -e

echo "Starting deployment of Reddit API Wrapper..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    exit 1
fi

# Build and start the services
echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Test the health endpoint
echo "Testing health endpoint..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Service is healthy!"
else
    echo "❌ Service health check failed"
    docker-compose logs reddit-api-wrapper
    exit 1
fi

echo "🚀 Deployment completed successfully!"
echo "📖 API documentation available at: http://localhost:8000/docs"
echo "🏥 Health check available at: http://localhost:8000/health"
echo ""
echo "To view logs: docker-compose logs -f reddit-api-wrapper"
echo "To stop services: docker-compose down"