from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.etiqueta import EtiquetaCreate, EtiquetaResponse, EtiquetaUpdate
from app.services.etiqueta import etiqueta_service

router = APIRouter(prefix="/chatbot/etiquetas", tags=["chatbot-etiquetas"])


@router.get("", response_model=list[EtiquetaResponse])
async def listar_etiquetas(db: AsyncSession = Depends(get_db)):
    return await etiqueta_service.listar(db)


@router.post("", response_model=EtiquetaResponse, status_code=status.HTTP_201_CREATED)
async def crear_etiqueta(payload: EtiquetaCreate, db: AsyncSession = Depends(get_db)):
    return await etiqueta_service.crear(db, payload)


@router.put("/{etiqueta_id}", response_model=EtiquetaResponse)
async def actualizar_etiqueta(etiqueta_id: int, payload: EtiquetaUpdate, db: AsyncSession = Depends(get_db)):
    etiqueta = await etiqueta_service.get_by_id(db, etiqueta_id)
    if not etiqueta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Etiqueta no encontrada")
    return await etiqueta_service.actualizar(db, etiqueta, payload)


@router.delete("/{etiqueta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_etiqueta(etiqueta_id: int, db: AsyncSession = Depends(get_db)):
    etiqueta = await etiqueta_service.get_by_id(db, etiqueta_id)
    if not etiqueta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Etiqueta no encontrada")
    await etiqueta_service.eliminar(db, etiqueta)
