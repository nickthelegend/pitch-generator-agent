# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_PORT=8080 \
    API_HOST=0.0.0.0 \
    MEDIA_DIR=/app/outputs

# Install system dependencies
# ffmpeg is required for video compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
# We also include extra libraries required for our specific API testing and functioning
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt httpx fastapi

# Copy the rest of the application code
COPY . .

# Create the outputs directory to store rendered videos
RUN mkdir -p /app/outputs

# Expose port 8080 to the outside world
EXPOSE 8080

# Command to run the FastApi application
CMD ["python", "main.py", "api"]
