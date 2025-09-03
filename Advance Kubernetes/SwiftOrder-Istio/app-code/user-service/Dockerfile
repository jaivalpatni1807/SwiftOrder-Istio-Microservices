# app-code/user-service/Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY . .
RUN npm install express pg
EXPOSE 8080
CMD ["node", "server.js"]