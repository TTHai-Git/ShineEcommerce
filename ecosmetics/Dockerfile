# Use the official Python 3.10.0 image
FROM python:3.10.0-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m django
USER django

# Set the working directory
WORKDIR /ecosmetics

# Copy requirements and install dependencies
COPY --chown=django:django requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY --chown=django:django . .

# Expose the development server port
EXPOSE 8000

# Collect static files (optional, for production)
# RUN python manage.py collectstatic --noinput

# Default command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
