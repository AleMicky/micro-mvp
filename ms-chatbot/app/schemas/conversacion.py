from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MensajeRequest(BaseModel):
    sesion_id: str = Field(..., max_length=100)
    texto: str = Field(..., min_length=1)


class MensajeResponse(BaseModel):
    respuesta: str
    opciones: list[str] | None = None
    estado: str


class ConversacionResponse(BaseModel):
    id: int
    sesion_id: str
    estado: str
    contexto: dict
    cliente_id: int | None
    creado_en: datetime
    actualizado_en: datetime

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

    model_config = ConfigDict(from_attributes=True)


class MensajeItem(BaseModel):
    id: int
    direccion: str
    texto: str
    wa_message_id: str | None
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
