#!/bin/bash

# Build script for Render deployment
# This script handles common build issues and ensures compatibility

echo "🚀 Starting build process..."

# Upgrade pip
pip install --upgrade pip

# Install system dependencies if needed
# apt-get update && apt-get install -y build-essential python3-dev

# Install Python packages with specific versions
echo "📦 Installing Python dependencies..."

# Install core packages first
pip install numpy==1.24.3
pip install pandas==2.1.4

# Install remaining packages
pip install -r requirements.txt

echo "✅ Build completed successfully!"
