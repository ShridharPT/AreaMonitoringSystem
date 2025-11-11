#!/bin/bash
# Build script for Render deployment

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p logs
mkdir -p screenshots
mkdir -p data

echo "Build completed successfully!"
