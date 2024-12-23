FROM node:20-slim

WORKDIR /app

# Copy package files first
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN npm install -g pnpm && \
    pnpm install --frozen-lockfile

# Copy source files (excluding node_modules)
COPY . .
RUN rm -rf node_modules && pnpm install --frozen-lockfile

# Build the application
RUN pnpm build

EXPOSE 3000

CMD ["pnpm", "preview", "--host", "0.0.0.0", "--port", "3000"]
