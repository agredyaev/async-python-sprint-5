FROM python-base:0.1.0 AS base

ARG USERNAME=files_test

# Install project dependencies
RUN uv sync --all-groups --all-packages --frozen


# Copy application code
COPY ./src ./
COPY ./tests/functional/tests ./tests
COPY ./tests/functional/tests/tests_entrypoint.sh ./tests_entrypoint.sh

# Create non-root user and group
RUN chmod +x ./tests_entrypoint.sh  && \
    ./useradd.sh "${GID}" "${UID}" "${USERNAME}" "${BASE_PATH}"

# Switch to non-root user
USER "${USERNAME}"

# Use entrypoint.sh to perform run tasks
ENTRYPOINT ["./tests_entrypoint.sh"]
