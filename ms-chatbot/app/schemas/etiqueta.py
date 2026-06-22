from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EtiquetaCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#64748b", pattern=r"^#[0-9A-Fa-f]{6}$")


class EtiquetaUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class EtiquetaResponse(BaseModel):
    id: int
    nombre: str
    color: str
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class AsignarEtiquetaRequest(BaseModel):
    etiqueta_id: int
