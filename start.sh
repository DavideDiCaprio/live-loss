#!/bin/bash
#
# This script automates the complete setup and launch
# of the live-loss FastAPI project.
#
# It will:
# 1. Create a Python virtual environment (if it doesn't exist)
# 2. Activate the virtual environment
# 3. Install all Python dependencies from requirements.txt
# 4. Install Node.js dependencies for the frontend
# 5. Compile the TypeScript code to JavaScript
# 6. Run the FastAPI server with auto-reload
#
# Run this script from the project root directory: ./start.sh
#

# Exit immediately if any command fails
set -e

echo "--- 1. Creating Python virtual environment 'venv'... ---"
python3 -m venv venv

echo "--- 2. Activating virtual environment... ---"
source venv/bin/activate

echo "--- 3. Installing Python dependencies... ---"
pip install -r requirements.txt

# run the frontend commands in a subshell (using parentheses)
# we don't have to 'cd ..' back to the root.
echo "--- 4. Installing Node.js dependencies (in /frontend)... ---"
(
  cd frontend
  npm install
)

echo "--- 5. Compiling TypeScript... ---"
(
  cd frontend
  npx tsc
)

echo "--- 6. Starting FastAPI server at http://127.0.0.1:8000 ---"
# The server will now run using the activated venv
uvicorn app.main:app --reload