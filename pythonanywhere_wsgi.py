#!/usr/bin/env python3
"""
WSGI Configuration for Quizy Quiz Application on PythonAnywhere

This file configures the WSGI application for deployment on PythonAnywhere.
Replace 'yourusername' with your actual PythonAnywhere username.
"""

import sys
import os

# Add your project directory to the Python path
project_home = '/home/yourusername/QuizyWebApp'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_SECRET_KEY'] = 'CHANGE-THIS-TO-A-SECURE-SECRET-KEY-IN-PRODUCTION'

# Import your Flask application
from quizapp import app as application

# Production configuration
application.config.update(
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY'),
    ENV='production',
    DEBUG=False,
    TESTING=False
)

if __name__ == "__main__":
    application.run()