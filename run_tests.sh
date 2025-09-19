#!/bin/bash

echo "🧪 Running Atlan Customer Support Copilot Tests"
echo "=============================================="

# Backend Tests
echo ""
echo "🔧 Running Backend Tests..."
cd backend

if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

echo "Running Python tests with pytest..."
python -m pytest tests/test_simple.py -v --tb=short

if [ $? -eq 0 ]; then
    echo "✅ Backend tests passed!"
else
    echo "❌ Backend tests failed!"
    exit 1
fi

# Frontend Tests
echo ""
echo "🎨 Running Frontend Tests..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install --legacy-peer-deps
fi

echo "Running React tests with Vitest..."
npm run test:run

if [ $? -eq 0 ]; then
    echo "✅ Frontend tests passed!"
else
    echo "❌ Frontend tests failed!"
    exit 1
fi

echo ""
echo "🎉 All tests passed successfully!"
echo "=============================================="
