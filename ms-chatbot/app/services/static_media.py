from pathlib import Path

LOGO_PATH = Path(__file__).resolve().parent.parent.parent / "static" / "logo.png"

_logo_cache: bytes | None = None


def obtener_logo() -> bytes | None:
    global _logo_cache
    if _logo_cache is None and LOGO_PATH.exists():
        _logo_cache = LOGO_PATH.read_bytes()
    return _logo_cache
