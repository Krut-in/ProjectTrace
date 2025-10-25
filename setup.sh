#!/bin/bash

echo "Setting up Email+Calendar Graph System..."

# Create project structure
mkdir -p src/{data,models,analysis,visualization,utils}
mkdir -p data/{raw,processed}
mkdir -p outputs/{graphs,reports,visualizations}
mkdir -p tests

# Create __init__.py files
touch src/__init__.py
touch src/data/__init__.py
touch src/models/__init__.py
touch src/analysis/__init__.py
touch src/visualization/__init__.py
touch src/utils/__init__.py

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the analysis:"
echo "  python src/main.py"
echo ""
echo "Outputs will be in the outputs/ directory"
