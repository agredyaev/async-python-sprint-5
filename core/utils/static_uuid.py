import hashlib
import uuid


def get_static_uuid(seed: str) -> uuid.UUID:
    """Generate a static UUID from a seed string."""
    sha = hashlib.sha256()
    sha.update(seed.encode())
    hash_bytes = sha.digest()[:16]
    return uuid.UUID(bytes=hash_bytes)
