# Use a base image with Python and necessary dependencies
FROM python:3.9-slim

# Install system dependencies for Selenium and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    ca-certificates \
    libx11-dev \
    libx11-xcb1 \
    libgl1-mesa-glx \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxrandr2 \
    libxtst6 \
    libappindicator3-1 \
    libgdk-pixbuf2.0-0 \
    libdbus-glib-1-2 \
    xdg-utils

# Install the latest Chrome version
RUN wget https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chrome-linux64.zip
RUN unzip chrome-linux64.zip -d /opt/ && rm chrome-linux64.zip

# Set up ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/131.0.6778.204/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d /usr/local/bin && rm chromedriver_linux64.zip

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Flask app code to the container
COPY . /app/

# Expose the port your Flask app is running on (default is 5000)
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask app
CMD ["flask", "run"]
