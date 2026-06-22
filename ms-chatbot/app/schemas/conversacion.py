from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.etiqueta import EtiquetaResponse


class MensajeRequest(BaseModel):
    sesion_id: str = Field(..., max_length=100)
    texto: str = Field(..., min_length=1)


class MensajeResponse(BaseModel):
    respuesta: str
    opciones: list[str] | None = None
    estado: str


class TunnelUrlResponse(BaseModel):
    url: str | None
    activo: bool


class ResponderRequest(BaseModel):
    texto: str = Field(..., min_length=1)


class ConversacionResponse(BaseModel):
    id: int
    sesion_id: str
    canal: str
    estado: str
    contexto: dict
    cliente_id: int | None
    creado_en: datetime
    actualizado_en: datetime
    etiquetas: list[EtiquetaResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ConversacionListItem(BaseModel):
    id: int
    sesion_id: str
    canal: str
    estado: str
    actualizado_en: datetime
    ultimo_mensaje: str | None = None
    ultimo_mensaje_en: datetime | None = None
    ultima_direccion: str | None = None
    etiquetas: list[EtiquetaResponse] = []

    model_config = ConfigDict(from_attributes=True)


class MensajeItem(BaseModel):
    id: int
    direccion: str
    origen: str
    texto: str
    tipo_mensaje: str = "texto"
    nombre_archivo: str | None = None
    wa_message_id: str | None
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
