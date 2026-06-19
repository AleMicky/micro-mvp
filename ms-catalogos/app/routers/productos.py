import uuid
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.migrations import STATIC_PRODUCTOS_DIR
from app.crud.precio_producto import crud_precio_producto
from app.crud.producto import crud_producto
from app.events.publisher import publish_event
from app.models.producto import Producto
from app.schemas.precio_producto import PrecioProductoCreate, PrecioProductoResponse
from app.schemas.producto import (
    ProductoCreate,
    ProductoImagenResponse,
    ProductoResponse,
    ProductoUpdate,
)

router = APIRouter(prefix="/productos", tags=["productos"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024


def _to_producto_response(
    producto: Producto, precio_actual: Decimal | None = None
) -> ProductoResponse:
    response = ProductoResponse.model_validate(producto)
    response.precio_actual = precio_actual
    return response


async def _enrich_producto(db: AsyncSession, producto: Producto) -> ProductoResponse:
    precio = await crud_precio_producto.get_activo(db, producto.id)
    return _to_producto_response(producto, precio.precio_venta if precio else None)


async def _enrich_productos(db: AsyncSession, productos: list[Producto]) -> list[ProductoResponse]:
    if not productos:
        return []
    ids = [p.id for p in productos]
    precios_map = await crud_precio_producto.get_activos_map(db, ids)
    return [
        _to_producto_response(p, precios_map[p.id].precio_venta if p.id in precios_map else None)
        for p in productos
    ]


async def _get_producto_or_404(db: AsyncSession, producto_id: int) -> Producto:
    producto = await crud_producto.get(db, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


def _validate_image(imagen: UploadFile) -> str:
    if imagen.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no permitido. Use JPG, PNG o WEBP",
        )
    ext = Path(imagen.filename or "").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extensión no permitida. Use .jpg, .jpeg, .png o .webp",
        )
    return ext


def _delete_image_file(imagen_url: str | None) -> None:
    if not imagen_url or not imagen_url.startswith("/static/productos/"):
        return
    filename = imagen_url.rsplit("/", 1)[-1]
    file_path = STATIC_PRODUCTOS_DIR / filename
    if file_path.is_file():
        file_path.unlink()


@router.get("", response_model=list[ProductoResponse])
async def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
):
    productos = await crud_producto.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)
    return await _enrich_productos(db, productos)


@router.get("/codigo/{codigo}", response_model=ProductoResponse)
async def obtener_producto_por_codigo(codigo: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select

    stmt = select(Producto).where(Producto.codigo == codigo)
    producto = (await db.execute(stmt)).scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return await _enrich_producto(db, producto)


@router.post("/{producto_id}/precios", response_model=PrecioProductoResponse, status_code=status.HTTP_201_CREATED)
async def crear_precio_producto(
    producto_id: int,
    payload: PrecioProductoCreate,
    db: AsyncSession = Depends(get_db),
):
    await _get_producto_or_404(db, producto_id)
    return await crud_precio_producto.crear_precio(db, producto_id, payload)


@router.get("/{producto_id}/precios", response_model=list[PrecioProductoResponse])
async def listar_precios_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    await _get_producto_or_404(db, producto_id)
    return await crud_precio_producto.get_historial(db, producto_id)


@router.get("/{producto_id}/precio-actual", response_model=PrecioProductoResponse)
async def obtener_precio_actual_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    await _get_producto_or_404(db, producto_id)
    precio = await crud_precio_producto.get_activo(db, producto_id)
    if not precio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Precio activo no encontrado")
    return precio


@router.post("/{producto_id}/imagen", response_model=ProductoImagenResponse)
async def subir_imagen_producto(
    producto_id: int,
    imagen: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    producto = await _get_producto_or_404(db, producto_id)
    ext = _validate_image(imagen)

    content = await imagen.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen no debe superar 2MB",
        )

    _delete_image_file(producto.imagen_url)

    filename = f"{producto_id}_{uuid.uuid4().hex}{ext}"
    file_path = STATIC_PRODUCTOS_DIR / filename
    file_path.write_bytes(content)

    imagen_url = f"/static/productos/{filename}"
    producto.imagen_url = imagen_url
    await db.commit()
    await db.refresh(producto)

    return ProductoImagenResponse(imagen_url=imagen_url)


@router.delete("/{producto_id}/imagen", response_model=ProductoImagenResponse)
async def eliminar_imagen_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await _get_producto_or_404(db, producto_id)
    _delete_image_file(producto.imagen_url)
    producto.imagen_url = None
    await db.commit()
    await db.refresh(producto)
    return ProductoImagenResponse(imagen_url="")


@router.get("/{producto_id}", response_model=ProductoResponse)
async def obtener_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await _get_producto_or_404(db, producto_id)
    return await _enrich_producto(db, producto)


@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def crear_producto(payload: ProductoCreate, db: AsyncSession = Depends(get_db)):
    precio_venta = payload.precio_venta
    producto = await crud_producto.create(db, payload)

    precio_inicial = precio_venta
    if precio_inicial is None and producto.precio_base and producto.precio_base > 0:
        precio_inicial = producto.precio_base

    if precio_inicial is not None and precio_inicial > 0:
        await crud_precio_producto.crear_precio_inicial(db, producto.id, precio_inicial)

    await publish_event(
        "ProductCreated",
        {"producto_id": producto.id, "codigo": producto.codigo, "nombre": producto.nombre},
    )
    return await _enrich_producto(db, producto)


@router.put("/{producto_id}", response_model=ProductoResponse)
async def actualizar_producto(
    producto_id: int,
    payload: ProductoUpdate,
    db: AsyncSession = Depends(get_db),
):
    producto = await _get_producto_or_404(db, producto_id)
    updated = await crud_producto.update(db, producto, payload)
    await publish_event("ProductUpdated", {"producto_id": updated.id, "codigo": updated.codigo})
    return await _enrich_producto(db, updated)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await _get_producto_or_404(db, producto_id)
    producto_id_val = producto.id
    codigo = producto.codigo
    _delete_image_file(producto.imagen_url)
    await crud_producto.delete(db, producto)
    await publish_event("ProductDeleted", {"producto_id": producto_id_val, "codigo": codigo})
