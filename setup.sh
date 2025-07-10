#!/bin/bash

# Cover Letter Agent Setup Script
echo "🚀 Setting up Cover Letter Agent..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To use the Cover Letter Agent:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the agent: python scripts/run_cover_letter_agent.py -i data/job_description.txt"
echo ""
echo "For more options, run: python scripts/run_cover_letter_agent.py --help" 