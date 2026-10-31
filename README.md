# Orlando Wait Times

[![CI](https://github.com/vitinhoBig/orlando-wait-times/actions/workflows/ci.yml/badge.svg)](https://github.com/vitinhoBig/orlando-wait-times/actions/workflows/ci.yml)

Continuous collector and forecasting pipeline for theme park wait times in Orlando, FL.

> Status: under construction (Module 1).

## Data sources

Wait times: [Powered by ThemeParks.wiki](https://www.themeparks.wiki/)

## Run with Docker

Requires Docker Desktop.

```bash
cp .env.example .env
# set POSTGRES_PASSWORD in .env (e.g. openssl rand -hex 16)
docker compose up -d db
docker compose run --rm app
docker compose down
```

The app currently runs a database smoke check (Module 1). PostgreSQL is exposed
only on `127.0.0.1:5434`; all timestamps are stored in UTC.