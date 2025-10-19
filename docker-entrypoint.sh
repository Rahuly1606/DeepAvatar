#!/bin/bash

# Docker entrypoint script for 3D Face Reconstruction App

set -e

echo "========================================="
echo "3D Face Reconstruction - Starting Services"
echo "========================================="

# Start Nginx (for serving frontend)
echo "Starting Nginx..."
nginx

# Start Flask backend
echo "Starting Flask backend..."
cd /app/server
python app.py

# Keep container running
tail -f /dev/null
