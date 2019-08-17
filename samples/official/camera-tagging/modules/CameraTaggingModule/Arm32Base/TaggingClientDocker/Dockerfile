FROM arm32v7/node:10-slim

COPY package*.json ./
COPY yarn.lock ./

RUN yarn install

EXPOSE 3000