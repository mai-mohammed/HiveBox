# Use a slim Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the source code
COPY src/ /app/src/

# Set the Python path to include src directory
ENV PYTHONPATH=/app/src

# Run the application
CMD ["python", "src/app.py"] 