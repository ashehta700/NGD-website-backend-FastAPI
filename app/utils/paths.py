import os

# _CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# _APP_DIR = os.path.dirname(_CURRENT_DIR)

# _DEFAULT_STATIC_ROOT = "/app/static"
# STATIC_ROOT = os.environ.get("APP_STATIC_ROOT", _DEFAULT_STATIC_ROOT)

# Try to read from environment
STATIC_ROOT = os.getenv("APP_STATIC_ROOT")

# If not provided, fallback to /app/static
if not STATIC_ROOT:
    STATIC_ROOT = "/app/static"

def _normalize_parts(parts):
    for raw in parts:
        if not raw:
            continue
        cleaned = raw.replace("\\", "/")
        for chunk in cleaned.split("/"):
            chunk = chunk.strip()
            if chunk:
                yield chunk


def static_path(*parts: str, ensure: bool = False) -> str:
    """
    Build an absolute path inside the configured static root.

    Args:
        *parts: Path segments inside the static directory.
        ensure: Create the directory if it does not exist.
    """
    cleaned_parts = list(_normalize_parts(parts))
    path = os.path.join(STATIC_ROOT, *cleaned_parts)
    if ensure:
        os.makedirs(path, exist_ok=True)
    return path


def static_file_path(filename: str, *parts: str) -> str:
    """
    Build an absolute file path inside the static root, ensuring the parent
    directory exists.
    """
    directory = static_path(*parts, ensure=True)
    return os.path.join(directory, filename)

