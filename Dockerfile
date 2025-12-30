# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        libglx0 \
        libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY tuxun_agent/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/uploads /app/data /app/data/vector_db

# Expose port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "uvicorn tuxun_agent.main:app --host $API_HOST --port $API_PORT"]