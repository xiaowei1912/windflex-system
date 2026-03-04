FROM python:3.11-slim

LABEL maintainer="windflex"
LABEL description="Hardware Control Service for Windflex automation testing"

# Install system dependencies (adb, usbutils, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        android-tools-adb \
        usbutils \
        iproute2 \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create SSH key directory
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Non-root user for security (still needs write to /dev via group)
# We keep root here because privileged container is needed for USB/serial access

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["python", "main.py"]
