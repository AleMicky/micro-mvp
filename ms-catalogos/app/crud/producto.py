from app.crud.base import CRUDBase
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate

crud_producto = CRUDBase[Producto, ProductoCreate, ProductoUpdate](Producto)
