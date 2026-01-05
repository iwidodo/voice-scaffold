"""
Demo script showing how to use the Streamlit UI.

This script provides instructions and helpers for running the appointment scheduler.
"""
import subprocess
import sys
import time
import requests


def check_backend():
    """Check if the backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    print("=" * 60)
    print("Appointment Scheduler - Streamlit UI Setup")
    print("=" * 60)
    print()
    
    # Check if backend is running
    print("Checking backend status...")
    if check_backend():
        print("✅ Backend is running at http://localhost:8000")
    else:
        print("❌ Backend is NOT running!")
        print()
        print("Please start the backend first:")
        print("  1. Open a new terminal")
        print("  2. cd to the appointment-scheduler directory")
        print("  3. Run: ./run_local.sh")
        print()
        response = input("Press Enter when backend is ready (or Ctrl+C to exit): ")
        
        # Check again
        if not check_backend():
            print("Still can't connect to backend. Exiting...")
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("Starting Streamlit UI...")
    print("=" * 60)
    print()
    print("The UI will open in your browser at http://localhost:8501")
    print()
    print("Try these example messages:")
    print("  - 'I have a rash that won't go away'")
    print("  - 'I need to see a doctor for headaches'")
    print("  - 'I'm looking for a pediatrician for my child'")
    print()
    print("Press Ctrl+C to stop the Streamlit server")
    print("=" * 60)
    print()
    
    time.sleep(2)
    
    # Run streamlit
    try:
        subprocess.run(["streamlit", "run", "streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n\nShutting down Streamlit UI...")
        print("Goodbye!")


if __name__ == "__main__":
    main()
