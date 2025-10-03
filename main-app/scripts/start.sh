#!/bin/bash
echo "🚀 Starting Intelligence Sharing System..."

echo "✅ Step 1: Compiling contracts..."
npx hardhat compile

echo "✅ Step 2: Deploying contract..."
npx hardhat run scripts/deploy.js --network hardhat

echo "✅ Step 3: Starting Python API..."
python3 -m venv venv 2>/dev/null || echo "Virtual env exists"
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8003 --reload