FROM python:3.11-slim

# Build arguments for proxy configuration (optional)
# Pass these at build time: docker build --build-arg HTTP_PROXY=http://proxy:port ...
ARG HTTP_PROXY=""
ARG HTTPS_PROXY=""
ARG NO_PROXY="localhost,127.0.0.1"

# Set proxy environment variables only if provided
ENV http_proxy="${HTTP_PROXY}"
ENV https_proxy="${HTTPS_PROXY}"
ENV no_proxy="${NO_PROXY}"

# Install system dependencies for Chrome, Firefox and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    firefox-esr \
    && wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /tmp/google-chrome-key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* /tmp/google-chrome-key.pub

# Install geckodriver manually to avoid GitHub API rate limits
RUN wget -q -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm /tmp/geckodriver.tar.gz

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
