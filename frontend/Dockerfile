FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm install

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Install a simple static file server
RUN npm install -g serve

EXPOSE 3000

# Serve the static files
CMD ["serve", "-s", "dist", "-l", "3000"]
