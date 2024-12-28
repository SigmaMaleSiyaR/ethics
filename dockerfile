FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libxss1 \
    libappindicator3-1 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver manually (download the latest version)
RUN CHROMEDRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wgethttps://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chrome-linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Set Chromium path (if needed)
ENV CHROME_BIN=/usr/bin/chromium

# Set up the rest of the application
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

# Expose port and run the app
EXPOSE 5000
CMD ["python", "app.py"]
