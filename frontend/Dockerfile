FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Apply current Alpine security updates before constructing the runtime layer.
# The runtime image contains only the Next.js standalone server and its
# production dependency closure. Package managers and development tooling are
# deliberately removed from the runtime attack surface.
RUN apk update \
    && apk upgrade --no-cache \
    && rm -rf /usr/local/lib/node_modules/npm \
    /usr/local/lib/node_modules/corepack \
    /opt/yarn* \
    /usr/local/bin/npm \
    /usr/local/bin/npx \
    /usr/local/bin/corepack \
    && addgroup -S -g 10001 appgroup \
    && adduser -S -u 10001 -G appgroup appuser

COPY --from=build --chown=appuser:appgroup /app/.next/standalone ./
COPY --from=build --chown=appuser:appgroup /app/.next/static ./.next/static
COPY --from=build --chown=appuser:appgroup /app/public ./public

USER 10001:10001
EXPOSE 3000
CMD ["node", "server.js"]
