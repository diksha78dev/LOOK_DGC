@echo off
title LOOK-DGC Docker Builder
echo ================================================
echo   LOOK-DGC Docker Build Script
echo   Developed by: Gopichand
echo ================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed or not running
    echo Please install Docker Desktop and ensure it's running
    pause
    exit /b 1
)

echo Building LOOK-DGC Docker image...
docker build -t look-dgc:latest .

if errorlevel 1 (
    echo Error: Docker build failed
    pause
    exit /b 1
)

echo.
echo Docker image built successfully!
echo.
echo To run LOOK-DGC in Docker:
echo   docker run -it --rm -e DISPLAY=host.docker.internal:0 look-dgc
echo.
echo Or use Docker Compose:
echo   docker-compose -f docker-compose.windows.yml up
echo.
pause