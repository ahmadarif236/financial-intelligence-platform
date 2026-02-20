# Use official Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Install system dependencies for pandas and psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY ./backend /code/backend

# Change working directory to backend
WORKDIR /code/backend

# Create necessary directories
RUN mkdir -p data uploads

# Expose port (Hugging Face Spaces explicitly looks for 7860 by default)
EXPOSE 7860

# Command to run the application (Hugging Face passes the PORT variable)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 7860"]
