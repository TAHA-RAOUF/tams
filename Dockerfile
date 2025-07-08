# TAMS Flask Backend Dockerfile
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables (override in docker-compose or at runtime)
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Run migrations and start app
CMD gunicorn -b 0.0.0.0:5000 run:app
