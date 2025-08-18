#!/bin/bash

# Build script for Render deployment
# This script handles common build issues and ensures compatibility

echo "🚀 Starting build process..."

# Check Python version
python --version
pip --version

# Upgrade pip
pip install --upgrade pip

# Install Python packages with specific versions
echo "📦 Installing Python dependencies..."

# Install core packages first (these versions are compatible with Python 3.11+)
pip install numpy==1.23.5
pip install pandas==1.5.3

# Install remaining packages
pip install -r requirements.txt

echo "✅ Build completed successfully!"
