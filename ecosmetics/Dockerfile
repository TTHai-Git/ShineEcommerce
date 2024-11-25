# Use the official Python 3.10.0 image
FROM python:3.10.0-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /ecosmetics

# Copy the requirements.txt file first
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the entire Django project
COPY . .

# Expose the development server port
EXPOSE 8000

# Default command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
