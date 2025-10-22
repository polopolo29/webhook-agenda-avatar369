#!/bin/bash
# A simple script to run the Flask application in a production-ready way.

# Change to the directory where the app.py is located
cd "$(dirname "$0")/sistema_adherencia"

# Number of worker processes
WORKERS=4

# The host and port to bind to
HOST="0.0.0.0"
PORT="5000"

echo "Starting Gunicorn server for the Asistente Médico PDF..."
exec gunicorn --workers $WORKERS --bind $HOST:$PORT app:app
