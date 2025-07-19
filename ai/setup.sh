#!/bin/bash
# Setup script for Balatro RL AI environment

echo "Setting up Balatro RL AI environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "Usage:"
echo "  To activate environment: source venv/bin/activate"
echo "  To test environment is working: python -m ai.test_env"
echo "  To train agent: python -m ai.train_balatro"
