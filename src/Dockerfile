# Stage 2: Backend (Python)
FROM node:18-alpine AS frontend

COPY application ./application

WORKDIR /application/front_end/docgenie

RUN npm ci --legacy-peer-deps --verbose

WORKDIR /

FROM python:3.10.11-slim

# Get Node.js and npm
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Verify Node.js installation
RUN node --version && npm --version

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy stuff over from frontend build step
COPY --from=frontend /application /application

# Expose the ports
EXPOSE 8888
EXPOSE 3000

# Copy the .env file and main.py
COPY .env .
COPY main.py .
COPY config.py .

# Run the server
CMD ["python3", "main.py"]