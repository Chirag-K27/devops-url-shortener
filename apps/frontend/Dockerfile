# ── Stage 1: Build React app ───────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (cached layer)
COPY package.json package-lock.json* ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# ── Stage 2: Serve with NGINX ─────────────────────────────
FROM nginx:alpine AS production

# Remove default NGINX config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom NGINX config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React app from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
