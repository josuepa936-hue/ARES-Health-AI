# syntax=docker/dockerfile:1
FROM node:24-bookworm-slim@sha256:dc26ae92c9fb15cf6b1d63e20f0944b2efe0f115b20e00be48fb23fceb061c54 AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ARES_PUBLIC_DEMO=1 ARES_RESEARCH_ENABLED=0
WORKDIR /app
COPY requirements-deploy.lock ./
RUN python -m pip install --no-cache-dir -r requirements-deploy.lock && python -m pip check
COPY src/ ./src/
COPY --from=frontend /build/frontend/dist/ ./frontend/dist/
COPY deploy/ ./deploy/
RUN chmod -R a=rX /app && chmod 0555 deploy/start.sh
USER 10001:10001
EXPOSE 10000
CMD ["./deploy/start.sh"]
