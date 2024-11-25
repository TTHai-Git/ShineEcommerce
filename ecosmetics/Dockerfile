# Use the official Python image
FROM python:3.10.0-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /ecosmetics

# Install system dependencies
# Add any required dependencies here to ensure proper package installation
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    gcc \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
# Use --default-timeout to avoid timeout issues
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose the Django development server port
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
