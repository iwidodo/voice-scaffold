#!/bin/bash
# Run Streamlit UI for appointment scheduler

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if backend is running
echo "Checking if backend is running..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "⚠️  WARNING: Backend server doesn't appear to be running!"
    echo "Please start it in another terminal with: ./run_local.sh"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Run Streamlit
echo "Starting Streamlit UI..."
streamlit run streamlit_app.py
