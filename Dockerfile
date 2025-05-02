# Use an official Python runtime as a parent image
# Using 3.11 as a stable, widely supported version. Match your development env if possible.
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
# Using the requirements list WITHOUT python-dotenv
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This includes server.py (WITH HARDCODED SECRETS!), static/, templates/, Procfile etc.
# Files listed in .dockerignore will be excluded.
COPY . .

# Make port 8000 available to the world outside this container
# Gunicorn default port. Azure App Service often uses 8000 or 80.
EXPOSE 8000

# Define the command to run the app using Gunicorn
# Assumes your Flask app instance in server.py is named 'app'
# Assumes Procfile specifies 'web: gunicorn server:app' or similar
# Binds to all network interfaces on port 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "server:app"]