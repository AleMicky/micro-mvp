from pathlib import Path

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_DOCUMENT_SIZE = 25 * 1024 * 1024


def clasificar_adjunto(content_type: str, filename: str) -> str:
    ext = Path(filename or "").suffix.lower()
    if content_type in ALLOWED_IMAGE_TYPES and ext in ALLOWED_IMAGE_EXTENSIONS:
        return "imagen"
    if content_type in ALLOWED_DOCUMENT_TYPES and ext in ALLOWED_DOCUMENT_EXTENSIONS:
        return "documento"
    raise ValueError("Tipo de archivo no permitido")


def limite_para(tipo_mensaje: str) -> int:
    return MAX_IMAGE_SIZE if tipo_mensaje == "imagen" else MAX_DOCUMENT_SIZE
