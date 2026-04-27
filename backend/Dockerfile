# Use an official Python base image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source
COPY . .

# Expose the application port
EXPOSE 8000

# Command used to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
