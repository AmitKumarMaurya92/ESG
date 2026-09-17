# Frontend Dockerfile (development)
FROM node:20-alpine

WORKDIR /app

# Dependencies (cached layer)
COPY package.json package-lock.json* ./
RUN npm install

# Application code
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
