# ==============================================================================
# DOCKER CONTAINER CONFIGURATION
# Production-ready Dockerfile for containerizing the FastAPI application.
# ==============================================================================

# Use a minimalist Python 3.10 base image to reduce footprint
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Update system repositories and install essential build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
# Done before copying the rest of the code to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project source code into the container
COPY . .

# Expose port 8000 for external API communication
EXPOSE 8000

# Define the startup command utilizing uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]