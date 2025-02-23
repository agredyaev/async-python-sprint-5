from datetime import UTC, datetime


def get_timestamp() -> datetime:
    """Get current timestamp."""
    return datetime.now(tz=UTC)
