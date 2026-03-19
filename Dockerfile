# Use a lightweight Python image
FROM python:3.10-slim

# Install system dependencies for dlib, face_recognition, and OpenCV
RUN apt-get update && apt-get install -y \
    libx11-6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Command to run your FastAPI app
# Use $PORT so Railway can assign its own port
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}