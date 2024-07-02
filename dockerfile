# Stage 1: Build stage
FROM python:3.9-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    gcc \
    musl-dev \
    libxrender \
    libxext \
    libzbar

# Install gunicorn
RUN pip install --no-cache-dir gunicorn

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Stage 2: Production stage
FROM python:3.9-alpine

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache \
    libxrender \
    libxext \
    libzbar

# Copy built Python dependencies and gunicorn from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy application code from builder stage
COPY --from=builder /app /app

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 5000
EXPOSE 5000

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
