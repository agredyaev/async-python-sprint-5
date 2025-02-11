# Base stage for docker environment setup
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

# Set environment variables
    # user
ENV GID=1000 \
    UID=1000 \
    # python
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # path
    BASE_PATH=/opt/app

# Set python path
ENV PYTHONPATH="$BASE_PATH":"$BASE_PATH"/tests
ENV PYTHONPATH="$BASE_PATH":"$BASE_PATH"/.venv/bin
ENV PATH=""$BASE_PATH"/.venv/bin:$PATH"

# Set work directory
WORKDIR "$BASE_PATH"

# Set the default shell to bash with pipefail option
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

# Copy common files
COPY pyproject.toml uv.lock ./
COPY ./core ./core
COPY ./services/auth/pyproject.toml ./services/auth/pyproject.toml
COPY ./docker/useradd.sh ./useradd.sh
RUN chmod +x ./useradd.sh

# Initialize
CMD ["sleep", "0.1"]
