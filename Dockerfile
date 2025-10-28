FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p instance templates static
RUN chmod 755 instance templates static

# Create non-root user (with proper permissions)
RUN useradd -m -u 1000 webuser && chown -R webuser:webuser /app
USER webuser

# Expose port
EXPOSE 80

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Run the application with gunicorn using run.py on port 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "run:app"]