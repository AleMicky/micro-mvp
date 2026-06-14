from app.crud.base import CRUDBase
from app.models.marca import Marca
from app.schemas.marca import MarcaCreate, MarcaUpdate

crud_marca = CRUDBase[Marca, MarcaCreate, MarcaUpdate](Marca)
