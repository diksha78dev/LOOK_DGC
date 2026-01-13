#!/bin/bash

echo "================================================"
echo "  LOOK-DGC Docker Build Script"
echo "  Developed by: Gopichand"
echo "================================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker and ensure it's running"
    exit 1
fi

echo "Building LOOK-DGC Docker image..."
docker build -t look-dgc:latest .

if [ $? -ne 0 ]; then
    echo "Error: Docker build failed"
    exit 1
fi

echo
echo "Docker image built successfully!"
echo
echo "To run LOOK-DGC in Docker:"
echo "  xhost +local:docker"
echo "  docker run -it --rm -e DISPLAY=\$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix look-dgc"
echo
echo "Or use Docker Compose:"
echo "  docker-compose up"
echo