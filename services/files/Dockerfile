FROM python-base:0.1.0 AS base

ARG USERNAME=files

# Install project dependencies
RUN uv sync --package files --frozen


# Copy application code
COPY ./src ./

# Create non-root user and group
RUN chmod +x ./entrypoint.sh  && \
    ./useradd.sh "${GID}" "${UID}" "${USERNAME}" "${BASE_PATH}"

# Switch to non-root user
USER "${USERNAME}"

# Use entrypoint.sh to perform run tasks
ENTRYPOINT ["./entrypoint.sh"]
