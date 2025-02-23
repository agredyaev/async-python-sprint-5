# Storage service

![Python](https://img.shields.io/badge/python-3.13-blue)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Actions status](https://github.com/agredyaev/async-python-sprint-5/actions/workflows/ci.yml/badge.svg)](https://github.com/agredyaev/async-python-sprint-4/actions)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)]()
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?logo=docker&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)]()
[![NGINX](https://img.shields.io/badge/NGINX-269539?logo=nginx&logoColor=white)]()
[![Pydantic](https://img.shields.io/badge/Pydantic-red?logo=pydantic&logoColor=white)]()
[![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)]()
[![MinIO](https://img.shields.io/badge/MinIO-FFA500?logo=minio&logoColor=white)]()
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://mit-license.org/)

---
A storage service that supports user authentication and file management for authorized users. Built with FastAPI, Redis, and MinIO, it provides secure and scalable file storage capabilities.
---
## Key Features
- **User Authentication**: Secure JWT-based authentication for managing access.
- **File Upload**: Upload files to object storage with metadata and versioning support.
- **File Download**: Stream files securely for authorized users.
- **File Listing**: Retrieve a list of files owned by the authenticated user.
- **File Revisions**: View file version history with detailed metadata.
- **Service Health Checks**: Monitor the health of database, cache, and storage services.

---

## API Endpoints

### Authentication
- **`/user/login`**: Authenticate and obtain a JWT token.
- **`/user/signup`**: Register a new user.

### File Management
- **`/files/upload`**: Upload a file to the storage service.
- **`/files/download`**: Download a file by its path or ID.
- **`/files/`**: List all files owned by the authenticated user.
- **`/files/revisions/`**: Retrieve version history for a specific file.

### Service Status
- **`/files/ping`**: Check the health status of the service.

---
## Deploy
```bash
# clone the repository
git clone https://github.com/agredyaev/async-python-sprint-5.git
cd async-python-sprint-5
# setup the environment
make setup
# activate the virtual environment
. ./.venv/bin/activate

# run auth tests
make compose-up-auth-tests-func
make clean
# run files tests
make compose-up-files-tests-func
make clean
# run the service
make compose-up
```
