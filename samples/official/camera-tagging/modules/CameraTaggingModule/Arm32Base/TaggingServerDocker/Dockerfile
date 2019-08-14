FROM arm32v7/node:10-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ffmpeg \
    && ls /var/lib/apt/lists \
    && rm -rf /var/lib/apt/lists/*

COPY package*.json /app/server/

WORKDIR /app/server
RUN npm install -q \
    && npm prune --production

EXPOSE 3002 3003