# Use the official Python image
FROM python:3.10.0-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /ecosmetics

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && apt-get clean

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
# Use --default-timeout to avoid timeout issues
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy project files
COPY . .

# Expose the Django development server port
EXPOSE 8000

# Add the entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Use the entrypoint script as the default entry point
ENTRYPOINT ["docker-entrypoint.sh"]

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
