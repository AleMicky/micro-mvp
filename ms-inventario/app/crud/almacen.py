from app.crud.base import CRUDBase
from app.models.almacen import Almacen
from app.schemas.almacen import AlmacenCreate, AlmacenUpdate

crud_almacen = CRUDBase[Almacen, AlmacenCreate, AlmacenUpdate](Almacen)
