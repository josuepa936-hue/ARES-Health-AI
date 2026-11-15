# syntax=docker/dockerfile:1
# Test harness only. Build the production image first; never deploy this to Render.
FROM node:24-bookworm-slim@sha256:dc26ae92c9fb15cf6b1d63e20f0944b2efe0f115b20e00be48fb23fceb061c54 AS node
FROM ares-public-demo:local
USER root
# Preparation may use Internet. No installs run in the isolated validation phase.
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export SSL_CERT_FILE=/run/secrets/proxy_ca; fi; \
    apt-get update && apt-get install -y --no-install-recommends chromium && rm -rf /var/lib/apt/lists/*
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/npm/ /usr/local/lib/node_modules/npm/
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/proxy_ca; fi; \
    npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build
WORKDIR /app
COPY offline_checks/ ./offline_checks/
# Refresh API source even if the prepared base tag is older; do not alter it.
RUN --mount=type=bind,source=src,target=/prepared-src \
    cp -a /prepared-src/. /app/src/ && chmod -R a=rX /app && \
    mkdir -p /results && chmod 1777 /results && chmod 0555 offline_checks/run.sh
ENV ARES_PUBLIC_DEMO=0 ARES_RESEARCH_ENABLED=1 HOME=/tmp/ares-home XDG_CACHE_HOME=/tmp/ares-cache
USER 10001:10001
ENTRYPOINT ["/app/offline_checks/run.sh"]
