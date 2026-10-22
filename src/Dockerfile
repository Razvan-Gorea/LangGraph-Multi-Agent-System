# Stage 1: Frontend (same Debian release as the final image, so native node_modules binaries match its libc)
FROM node:24-bookworm-slim AS frontend

WORKDIR /application/front_end/docgenie

# manifests only, so source edits don't invalidate the npm ci layer
COPY application/front_end/docgenie/package*.json ./

RUN npm ci

# Stage 2: Backend (Python)
FROM python:3.12-slim-bookworm

# curl is used by the docker-compose healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Get Node.js and npm from the frontend stage
COPY --from=frontend /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

# Verify Node.js installation
RUN node --version && npm --version

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY application /application
COPY --from=frontend /application/front_end/docgenie/node_modules /application/front_end/docgenie/node_modules

# Expose the ports
EXPOSE 8888
EXPOSE 3000

# .env is supplied at runtime via compose env_file, not baked into the image
COPY main.py .
COPY config.py .

# Run the server
CMD ["python3", "main.py"]