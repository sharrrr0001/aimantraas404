"""
WSGI Entry Point for AI Mantraas Student Portal
================================================
This file serves as the entry point for WSGI-compatible servers
such as Gunicorn, uWSGI, or cloud platforms like Render, Heroku, etc.
"""

import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, initialize_app

# Initialize the application
initialize_app()

# Application instance for WSGI server
application = app

# For development debugging
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
