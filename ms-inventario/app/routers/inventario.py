from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.excel import excel_service

router = APIRouter(tags=["inventario"])


@router.post("/loadExcel", status_code=status.HTTP_201_CREATED)
async def cargar_excel(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    return await excel_service.cargar_excel(db, file)
