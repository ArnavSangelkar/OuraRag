#!/bin/bash

# Supabase MCP Setup Script for Oura RAG
# This script helps you set up Supabase MCP integration

set -e

echo "🚀 Supabase MCP Setup for Oura RAG"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your_openai_api_key

# Oura Configuration
OURA_PERSONAL_ACCESS_TOKEN=your_oura_token
EOF
    echo "✅ Created .env file. Please edit it with your actual credentials."
else
    echo "✅ .env file already exists"
fi

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if ! python3 -c "import supabase" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check if test script exists
if [ ! -f test_mcp.py ]; then
    echo "❌ test_mcp.py not found. Please ensure it exists."
    exit 1
fi

echo ""
echo "🔧 Setup complete! Next steps:"
echo ""
echo "1. Edit .env file with your actual credentials:"
echo "   - SUPABASE_URL: Your Supabase project URL"
echo "   - SUPABASE_SERVICE_ROLE_KEY: Your service role key"
echo "   - OPENAI_API_KEY: Your OpenAI API key"
echo "   - OURA_PERSONAL_ACCESS_TOKEN: Your Oura token"
echo ""
echo "2. Set up your Supabase database schema (see MCP_SETUP.md)"
echo ""
echo "3. Test your setup:"
echo "   python3 test_mcp.py"
echo ""
echo "4. Check the MCP_SETUP.md file for detailed instructions"
echo ""
echo "🎉 Happy coding!"
