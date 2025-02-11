# URL Shortener Service

![Python](https://img.shields.io/badge/python-3.13-blue)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Actions status](https://github.com/agredyaev/async-python-sprint-4/actions/workflows/ci.yml/badge.svg)](https://github.com/agredyaev/async-python-sprint-4/actions)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)]()
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?logo=docker&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)]()
[![NGINX](https://img.shields.io/badge/NGINX-269539?logo=nginx&logoColor=white)]()
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://mit-license.org/)
![Pydantic](https://img.shields.io/badge/Pydantic-red?logo=pydantic&logoColor=white)

---
Modern URL shortening microservice with analytics and user management. Built with FastAPI, Postgres, and Redis, containerized with Docker.

---
## Key Features
- Shorten long URLs with customizable visibility (public/private)
- Redirect to original URLs with click tracking
- User registration and JWT authentication
- URL statistics (total clicks, access times, client info)
- Health checks and service monitoring

---
## Deploy
```bash
# clone the repository
git clone https://github.com/agredyaev/async-python-sprint-4.git
cd async-python-sprint-4
# setup the environment
make setup
# activate the virtual environment
. ./.venv/bin/activate

# run the tests
make compose-tests

# run the service
make compose-up
```
