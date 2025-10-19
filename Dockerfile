# Multi-stage Dockerfile for 3D Face Reconstruction App
# Optimized for both CPU and GPU deployment

# Stage 1: Backend (Python)
FROM python:3.10-slim as backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    libopencv-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/server

# Copy requirements and install Python dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ .

# Stage 2: Frontend (Node.js)
FROM node:18-alpine as frontend

WORKDIR /app/client

# Copy package files
COPY client/package*.json ./

# Install dependencies
RUN npm install

# Copy client code
COPY client/ .

# Build frontend
RUN npm run build

# Stage 3: Final image
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend from stage 1
COPY --from=backend /app/server /app/server
COPY --from=backend /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy frontend build from stage 2
COPY --from=frontend /app/client/dist /app/client/dist

# Copy nginx config for serving frontend
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 5000 80

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DEVICE=cpu

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Start script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

# For GPU support, build with:
# docker build --build-arg CUDA_VERSION=11.8 -t 3d-face-recon:gpu .
# And run with:
# docker run --gpus all -p 5000:5000 -p 80:80 3d-face-recon:gpu
