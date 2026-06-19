from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificacionResponse(BaseModel):
    id: int
    cliente_id: int | None
    tipo: str
    contenido: str
    evento_origen: str
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)
