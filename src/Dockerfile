# Stage 1: Frontend build (same Debian release as the final image, so the node binary and native modules match its libc)
FROM node:24-bookworm-slim AS frontend

WORKDIR /application/front_end/docgenie

# manifests only, so source edits don't invalidate the npm ci layer
COPY application/front_end/docgenie/package*.json ./

RUN npm ci

COPY application/front_end/docgenie ./

# next.config.mjs sets output: "standalone", so .next/standalone holds a server with only the traced deps
RUN npm run build

# Stage 2: Backend (Python)
FROM python:3.12-slim-bookworm

# curl is used by the docker-compose healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# only the node binary is needed at runtime (the standalone server is run with `node server.js`, no npm)
COPY --from=frontend /usr/local/bin/node /usr/local/bin/node

# Verify Node.js installation
RUN node --version

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY application /application
COPY --from=frontend /application/front_end/docgenie/.next/standalone /application/front_end/docgenie
COPY --from=frontend /application/front_end/docgenie/.next/static /application/front_end/docgenie/.next/static

# tells main.py to run the built frontend instead of `npm run dev`
ENV FRONTEND_STANDALONE=1

# Expose the ports
EXPOSE 8888
EXPOSE 3000

# .env is supplied at runtime via compose env_file, not baked into the image
COPY main.py .
COPY config.py .

# Run the server
CMD ["python3", "main.py"]
