#!/bin/bash

# Navigate to your Django project directory
cd /c/project-robopsy

# Activate virtual environment if needed
source venv/Scripts/activate  # For Git Bash
# source venv/bin/activate      # For WSL/Linux

cd RobopsyApp

# Run Django server in the background
python manage.py runserver 0.0.0.0:8000 &

# Give the server a few seconds to start
sleep 5

# Open Chrome in kiosk (full screen) mode to your app
# Adjust the path if needed
/c/Program \Files/Mozilla Firefox/firefox.exe --kiosk http://localhost:8000
