# Use an official Python runtime as a parent image
FROM python:3.9.13

# Set the working directory
WORKDIR /app

# Copy the backend files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file
COPY .env /app/.env

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
