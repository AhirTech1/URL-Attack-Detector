#!/bin/bash

echo "========================================"
echo "URL Attack Detector - Complete Setup"
echo "========================================"
echo ""

echo "[1/5] Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi
echo ""

echo "[2/5] Installing Python dependencies..."
cd backend
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi
echo ""

echo "[3/5] Generating training dataset..."
python3 scripts/generate_dataset.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to generate dataset"
    exit 1
fi
echo ""

echo "[4/5] Training ML model (this may take 2-5 minutes)..."
python3 scripts/train_model.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to train model"
    exit 1
fi
echo ""

echo "[5/5] Generating sample test files..."
python3 scripts/generate_sample_logs.py
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to generate sample files (optional)"
fi
echo ""

cd ..

echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Start the backend server:"
echo "   cd backend && python3 app.py"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   npm install && npm run dev"
echo ""
echo "3. Open http://localhost:5173 in your browser"
echo ""
