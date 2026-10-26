# Use official Python 3.13 image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies first (to cache this layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Command to run the pipeline
CMD ["python", "main.py"]