FROM python:3.11-slim

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    && wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /tmp/google-chrome-key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* /tmp/google-chrome-key.pub

# Set working directory
WORKDIR /tests

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy test code
COPY . .

# Create directories for test artifacts
RUN mkdir -p test_screenshots test_reports

# Default command (can be overridden)
CMD ["pytest", "-v", "--html=test_reports/report.html", "--self-contained-html"]
