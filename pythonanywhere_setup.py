# PythonAnywhere setup script
# Run this on PythonAnywhere console

import os
import subprocess

# Install dependencies
subprocess.run(['pip3.10', 'install', '--user', 'flask', 'pandas', 'yfinance', 'prophet', 'plotly', 'openpyxl', 'requests', 'python-dotenv'])

# Create directories
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

print("Setup complete! Your app is ready to run.")
