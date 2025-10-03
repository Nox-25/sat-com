# weather-prediction-system/main.py

import streamlit as st
import sys
import os

# Add the project root to the Python path
# This allows us to import modules from the other directories
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend import dashboard

def main():
    """
    Main function to run the Streamlit application.
    """
    dashboard.main()

if __name__ == "__main__":
    # To run this application, use the command:
    # streamlit run weather-prediction-system/main.py
    # Make sure you have an API key in satellite_api_handler.py
    main()