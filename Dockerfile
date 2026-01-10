FROM python:3.10-slim

# Install system dependencies (needed for psycopg2 might be useful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Backend Dependencies
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install Frontend Dependencies
COPY frontend/requirements.txt frontend/requirements.txt
RUN pip install --no-cache-dir -r frontend/requirements.txt

# Copy Application Code
COPY backend/ backend/
COPY frontend/ frontend/

# Copy Entrypoint Script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Set Environment Variables
# Backend runs on 5000 locally inside the container
ENV BACKEND_URL=http://127.0.0.1:5000/api
ENV FLASK_APP=backend/app.py

# Expose ports (Documentary only, Render controls $PORT)
EXPOSE 5000
EXPOSE 8080

# Command to run the application
CMD ["./entrypoint.sh"]
